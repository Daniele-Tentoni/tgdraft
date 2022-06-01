import logging
import sys
from tgdraft.bot import Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    filters,
)

import os
from dotenv import load_dotenv

load_dotenv()
from pymongo.mongo_client import MongoClient
from pymongo.database import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def mongo_connection() -> MongoClient:
    username = os.environ.get("MONGODB_USERNAME")
    password = os.environ.get("MONGODB_PASSWORD")
    logger.debug(f"Connect to db using {username}")
    conn_string = f"mongodb+srv://{username}:{password}@cluster0.ut26d.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(conn_string)

    try:
        return client
    except Exception as ex:
        logger.error(f"Unable to connect to the server due to {ex}.")
        sys.exit(os.EX_CANTCREAT)
    finally:
        del username, password


def mongo_db(client: MongoClient) -> Database:
    return client.tgdraft


TOKEN = os.environ.get("BOT_TOKEN")

PORT = int(os.environ.get("PORT", "8443"))


def cli() -> None:
    """Execute the bot."""
    client = mongo_connection()
    db = mongo_db(client)
    application = Application.builder().token(TOKEN).build()
    bot = Bot(logger, mongo=db)
    updater = application.updater
    application.add_handler(
        CommandHandler("start", bot.start_deep, filters.Regex("cube"))
    )
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("change_name", bot.change_name))
    application.add_handler(CommandHandler("new_cube", bot.new_cube))
    application.add_handler(InlineQueryHandler(bot.inline_query))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text)
    )
    application.add_handler(CallbackQueryHandler(bot.callback_sign_me))
    if os.environ.get("ENV", "localhost") == "HEROKU":
        updater.start_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url="https://tgdraft.herokuapp.com/" + TOKEN,
        )
    else:
        application.run_polling()


if __name__ == "__main__":
    cli()
