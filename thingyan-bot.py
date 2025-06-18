import json
import logging
import requests
import os  # NEW: For loading environment variables
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode

# --- Logging Configuration ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Bot Token from Environment Variable ---
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable not set")

# --- JSON Data Source URL ---
THINGYAN_SONGS_JSON_URL = "https://raw.githubusercontent.com/ULayGyiDev/thingyanahlann/main/songs.json"
song_data = []

# --- REQUIRED: Channel ID and Invite Link ---
REQUIRED_CHANNEL_ID = -1002664997277
REQUIRED_CHANNEL_INVITE_LINK = "https://t.me/thingyanahlann"
REQUIRED_CHANNEL_USERNAME = "@thingyanahlann"

# --- Load JSON from Remote GitHub URL ---
def load_song_data_from_json_file():
    global song_data
    try:
        response = requests.get(THINGYAN_SONGS_JSON_URL)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success" and "data" in data:
            song_data = []
            for item in data["data"]:
                if all(key in item for key in ["song_name", "artist", "album", "archive_link"]):
                    song_data.append({
                        "title": item["song_name"].strip(),
                        "artist": item["artist"].strip(),
                        "album": item["album"].strip(),
                        "link": item["archive_link"].strip()
                    })
            logger.info(f"Successfully loaded {len(song_data)} songs from remote JSON.")
        else:
            logger.warning(f"JSON data not in expected format: {data}")
            song_data = []
    except Exception as e:
        logger.error(f"Error fetching JSON from URL: {e}")
        song_data = []
    return song_data

# Load once at startup
load_song_data_from_json_file()

# --- Channel Membership Check Function ---
async def check_channel_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        chat_member = await context.bot.get_chat_member(REQUIRED_CHANNEL_ID, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            logger.info(f"User {user_id} is not a member of the required channel.")
            await update.message.reply_text(
                f"ဒီ bot ကို အသုံးပြုဖို့အတွက် ကျွန်တော်တို့ရဲ့ {REQUIRED_CHANNEL_USERNAME} channel ကို အရင် join ပေးဖို့ လိုအပ်ပါတယ်။\n"
                f"Channel Link: {REQUIRED_CHANNEL_INVITE_LINK}\n\n"
                "Join ပြီးပြီဆိုရင် /start ကို ပြန်နှိပ်ပြီး စမ်းသပ်နိုင်ပါတယ်။"
            )
            return False
    except Exception as e:
        logger.error(f"Error checking channel membership for user {user_id}: {e}")
        await update.message.reply_text(
            f"Channel membership ကို စစ်ဆေးရာမှာ ပြဿနာပေါ်လာပါတယ်။ ကျေးဇူးပြုပြီး {REQUIRED_CHANNEL_USERNAME} channel ကို Join ပြီး /start ကို ပြန်နှိပ်ပေးပါ။\n"
            f"Channel Link: {REQUIRED_CHANNEL_INVITE_LINK}"
        )
        return False

# --- Bot Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    await update.message.reply_text(
        "မင်္ဂလာပါ! သင်္ကြန်သီချင်းတွေကို ရှာဖွေနိုင်ဖို့ ကူညီပေးပါမယ်။\n\n"
        "သီချင်းအမည်၊ အဆိုတော် သို့မဟုတ် album အလိုက် ရှာဖွေနိုင်ပါတယ်။\n"
        "ဥပမာ: `သီချင်း မိုး` (သို့) `အဆိုတော် စိုင်းထီဆိုင်` (သို့) `album Classic Thingyan`"
    )

async def search_songs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    global song_data
    current_song_data = load_song_data_from_json_file() if not song_data else song_data
    if not current_song_data:
        await update.message.reply_text("သီချင်းအချက်အလက်များကို ရယူရာတွင် ပြဿနာရှိနေပါသည်။ ကျေးဇူးပြု၍ ခဏကြာပြီးမှ ထပ်ကြိုးစားပေးပါ။")
        return

    user_input = update.message.text.lower().strip()
    found_songs = []
    query = user_input

    if user_input.startswith("သီချင်း"):
        query = user_input.replace("သီချင်း", "", 1).strip()
        for song in current_song_data:
            if query in song["title"].lower():
                found_songs.append(song)
    elif user_input.startswith("အဆိုတော်"):
        query = user_input.replace("အဆိုတော်", "", 1).strip()
        for song in current_song_data:
            if query in song["artist"].lower():
                found_songs.append(song)
    elif user_input.startswith("album"):
        query = user_input.replace("album", "", 1).strip()
        for song in current_song_data:
            if query in song["album"].lower():
                found_songs.append(song)
    else:
        if query:
            for song in current_song_data:
                if (query in song["title"].lower() or
                    query in song["artist"].lower() or
                    query in song["album"].lower()):
                    found_songs.append(song)

    if found_songs:
        unique_songs = []
        seen_links = set()
        for song in found_songs:
            if song["link"] not in seen_links:
                unique_songs.append(song)
                seen_links.add(song["link"])

        response = "ရှာတွေ့သော သီချင်းများ:\n\n"
        for song in unique_songs:
            escaped_title = escape_markdown(song['title'], version=2)
            escaped_artist = escape_markdown(song['artist'], version=2)
            escaped_album = escape_markdown(song['album'], version=2)
            escaped_link = escape_markdown(song['link'], version=2)

            response += (
                f"**Title**: {escaped_title}\n"
                f"**Artist**: {escaped_artist}\n"
                f"**Album**: {escaped_album}\n"
                f"**Link**: {escaped_link}\n\n"
            )
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text(f"'{user_input}' နဲ့ ပတ်သက်တဲ့ သီချင်း မတွေ့ပါ။ ရှာဖွေမှု ပုံစံ မှန်ကန်ကြောင်း သေချာစစ်ဆေးပေးပါ။")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_channel_membership(update, context):
        return

    await update.message.reply_text(
        "ဒီ bot ကို အသုံးပြုနည်းကတော့:\n"
        "`/start` - bot ကိုစတင်ရန်\n"
        "`သီချင်း [သီချင်းအမည်]` - သီချင်းအမည်နဲ့ရှာရန်\n"
        "`အဆိုတော် [အဆိုတော်အမည်]` - အဆိုတော်အမည်နဲ့ရှာရန်\n"
        "`album [album အမည်]` - album အမည်နဲ့ရှာရန်\n"
        "prefix မပါပဲ သီချင်းအမည် သို့မဟုတ် အဆိုတော်အမည် သို့မဟုတ် album အမည်ကို တိုက်ရိုက် ရိုက်ထည့်၍လည်း ရှာဖွေနိုင်ပါသည်။\n"
        "ကျေးဇူးပြု၍ မှန်ကန်သော ပုံစံအတိုင်း ရိုက်ထည့်ပါ။"
    )

# --- Main function to run the bot ---
def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_songs))
    logger.info("Bot is polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Bot stopped.")

if __name__ == "__main__":
    main()
