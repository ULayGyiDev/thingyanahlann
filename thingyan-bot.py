import json
import logging
import requests
import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Environment & Constants ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")

THINGYAN_SONGS_JSON_URL = "https://raw.githubusercontent.com/ULayGyiDev/thingyanahlann/main/songs.json"

REQUIRED_CHANNEL_ID = -1002664997277
REQUIRED_CHANNEL_INVITE_LINK = "https://t.me/thingyanahlann"
REQUIRED_CHANNEL_USERNAME = "@thingyanahlann"

# Global song data list
song_data = []

# --- Load JSON Data ---
def load_song_data_from_json_file() -> list:
    global song_data
    try:
        logger.info(f"Fetching songs JSON from {THINGYAN_SONGS_JSON_URL}")
        response = requests.get(THINGYAN_SONGS_JSON_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success" and "data" in data:
            songs = []
            for item in data["data"]:
                if all(k in item for k in ("song_name", "artist", "album", "archive_link")):
                    songs.append({
                        "title": item["song_name"].strip(),
                        "artist": item["artist"].strip(),
                        "album": item["album"].strip(),
                        "link": item["archive_link"].strip(),
                    })
            song_data = songs
            logger.info(f"Loaded {len(song_data)} songs from remote JSON")
        else:
            logger.warning("JSON data not in expected format")
            song_data = []
    except Exception as e:
        logger.error(f"Error loading songs JSON: {e}")
        song_data = []
    return song_data


# Load once at startup
load_song_data_from_json_file()

# --- Channel membership check ---
async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
        else:
            logger.info(f"User {user_id} is NOT a member")
            await update.message.reply_text(
                f"ဒီ bot ကို အသုံးပြုဖို့အတွက် ကျွန်တော်တို့ရဲ့ {REQUIRED_CHANNEL_USERNAME} channel ကို အရင် join ပေးဖို့ လိုအပ်ပါတယ်။\n"
                f"Channel Link: {REQUIRED_CHANNEL_INVITE_LINK}\n\n"
                "Join ပြီးပြီဆိုရင် /start ကို ပြန်နှိပ်ပြီး စမ်းသပ်နိုင်ပါတယ်။"
            )
            return False
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        await update.message.reply_text(
            f"Channel membership ကို စစ်ဆေးရာမှာ ပြဿနာပေါ်လာပါတယ်။ ကျေးဇူးပြုပြီး {REQUIRED_CHANNEL_USERNAME} channel ကို Join ပြီး /start ကို ပြန်နှိပ်ပေးပါ။\n"
            f"Channel Link: {REQUIRED_CHANNEL_INVITE_LINK}"
        )
        return False


# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    keyboard = [
        [
            InlineKeyboardButton("သီချင်း (Song)", callback_data="prefix_သီချင်း"),
            InlineKeyboardButton("အဆိုတော် (Artist)", callback_data="prefix_အဆိုတော်"),
            InlineKeyboardButton("album (Album)", callback_data="prefix_album"),
        ],
        [InlineKeyboardButton("🔄 Refresh Songs Data", callback_data="refresh_songs")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "မင်္ဂလာပါ! သင်္ကြန်သီချင်းတွေကို ရှာဖွေနိုင်ဖို့ ကူညီပေးပါမယ်။\n\n"
        "သီချင်းအမည်၊ အဆိုတော် သို့မဟုတ် album အလိုက် ရှာဖွေနိုင်ပါတယ်။\n"
        "အောက်မှာ ရှာဖွေရန် category တစ်ခု ရွေးချယ်ပါ။",
        reply_markup=reply_markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    await update.message.reply_text(
        "ဒီ bot ကို အသုံးပြုနည်းကတော့:\n"
        "`/start` - bot ကိုစတင်ရန်\n"
        "`သီချင်း [သီချင်းအမည်]` - သီချင်းအမည်နဲ့ရှာရန်\n"
        "`အဆိုတော် [အဆိုတော်အမည်]` - အဆိုတော်နဲ့ရှာရန်\n"
        "`album [album အမည်]` - album အမည်နဲ့ရှာရန်\n"
        "prefix မပါပဲ သီချင်း၊ အဆိုတော် သို့မဟုတ် album ကို တိုက်ရိုက် ရိုက်ထည့်၍လည်း ရှာဖွေနိုင်ပါသည်။\n"
        "မှန်ကန်သော ပုံစံအတိုင်း ရိုက်ထည့်ပေးပါ။"
    )


# --- Callback Query Handler for Inline Keyboard ---

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge callback to Telegram

    data = query.data

    if data.startswith("prefix_"):
        prefix = data.split("_", 1)[1]
        await query.message.reply_text(
            f"'{prefix}' စာလုံးနဲ့ စတင်ပြီး ရိုက်ထည့်ပေးပါ။\nဥပမာ: `{prefix} မိုး`",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    elif data == "refresh_songs":
        await query.message.reply_text("Songs data ကို Refresh လုပ်နေပါပြီ...")
        new_data = load_song_data_from_json_file()
        await query.message.reply_text(
            f"Songs data refreshed. ယခု {len(new_data)} သီချင်း ရရှိထားပါတယ်။"
        )


# --- Search Handler ---

async def search_songs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    global song_data
    if not song_data:
        song_data = load_song_data_from_json_file()
        if not song_data:
            await update.message.reply_text(
                "သီချင်းအချက်အလက်များကို ရယူရာတွင် ပြဿနာရှိနေပါသည်။ ကျေးဇူးပြု၍ ခဏကြာပြီးမှ ထပ်ကြိုးစားပေးပါ။"
            )
            return

    user_input = update.message.text.strip()
    lowered_input = user_input.lower()

    # Determine prefix and query string
    prefix = None
    query = lowered_input

    if lowered_input.startswith("သီချင်း "):
        prefix = "title"
        query = lowered_input.replace("သီချင်း", "", 1).strip()
    elif lowered_input.startswith("အဆိုတော် "):
        prefix = "artist"
        query = lowered_input.replace("အဆိုတော်", "", 1).strip()
    elif lowered_input.startswith("album "):
        prefix = "album"
        query = lowered_input.replace("album", "", 1).strip()
    else:
        prefix = "all"  # NO prefix - search all fields

    if not query:
        await update.message.reply_text(
            "ရှာဖွေရန် စာလုံးတစ်ခုခု ရိုက်ထည့်ပေးပါ။"
        )
        return

    found_songs = []
    for song in song_data:
        if prefix == "title" and query in song["title"].lower():
            found_songs.append(song)
        elif prefix == "artist" and query in song["artist"].lower():
            found_songs.append(song)
        elif prefix == "album" and query in song["album"].lower():
            found_songs.append(song)
        elif prefix == "all" and (
            query in song["title"].lower()
            or query in song["artist"].lower()
            or query in song["album"].lower()
        ):
            found_songs.append(song)

    if found_songs:
        # Remove duplicates by link
        unique_songs = []
        seen_links = set()
        for s in found_songs:
            if s["link"] not in seen_links:
                unique_songs.append(s)
                seen_links.add(s["link"])

        response = "ရှာတွေ့သော သီချင်းများ:\n\n"
        for song in unique_songs:
            t = escape_markdown(song["title"], version=2)
            a = escape_markdown(song["artist"], version=2)
            al = escape_markdown(song["album"], version=2)
            l = escape_markdown(song["link"], version=2)

            response += (
                f"**Title**: {t}\n"
                f"**Artist**: {a}\n"
                f"**Album**: {al}\n"
                f"**Link**: {l}\n\n"
            )
        await update.message.reply_text(
            response, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            f"'{escape_markdown(user_input, version=2)}' နဲ့ ပတ်သက်တဲ့ သီချင်း မတွေ့ပါ။\n"
            "ရှာဖွေမှု ပုံစံ မှန်ကန်ကြောင်း သေချာစစ်ဆေးပေးပါ။",
            parse_mode=ParseMode.MARKDOWN_V2,
        )

# --- Main ---

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, search_songs)
    )

    logger.info("Bot started, polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
