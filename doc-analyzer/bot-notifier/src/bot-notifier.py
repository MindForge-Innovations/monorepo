# ~~~ Imports ~~~
import os
import sys
import asyncio
from fastapi import FastAPI, HTTPException
from aiogram import Bot, Dispatcher, types
import uvicorn
import logging
from colorlog import ColoredFormatter


# ~~~ Logger Configuration ~~~
def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
        reset=True,
        style="%",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger


logger = setup_logging()


# ~~~ Init bot ~~~
def init_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        sys.exit(1)
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)
    return bot, dp


bot, dp = init_bot()

app = FastAPI()


# ~~~ FastAPI Endpoints ~~~
@app.get("/status/")
async def get_status():
    return {"status": "OK"}


@app.get("/notify/")
async def send_notification():
    group_id = "PIAiMarket"  # Make sure to replace 'PIAiMarket' with the actual chat ID
    try:
        await bot.send_message(
            chat_id=group_id, text="Notification sent to group!"
        )
        logger.info("Notification sent successfully to group")
        return {"message": "Notification sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ~~~ Start FastAPI ~~~
async def start_fastapi():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


# ~~~ Main Function ~~~
async def start_app():
    api_task = asyncio.create_task(start_fastapi())
    await asyncio.gather(api_task)


if __name__ == "__main__":
    asyncio.run(start_app())
