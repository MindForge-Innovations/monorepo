"""
This module provides a Telegram bot able to interact with the user
and retrieves information from connected APIs.
"""

# ~~~ Imports ~~~
import asyncio
import os
import sys
import json
from fastapi import FastAPI, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

import redis
import httpx

import logging
from colorlog import ColoredFormatter

import uvicorn
from pydantic import BaseModel

# ___________________________________________________________________________________________
# TEMPORARY: Load environment variables from .env file
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file
# ___________________________________________________________________________________________


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


# ~~~ Init bot ~~~
def init_bot():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set")
        sys.exit(1)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    return bot, dp


# ~~~ Connection to Redis ~~~
def init_redis():
    REDIS_HOST = os.getenv(
        "REDIS_SERVER_HOST", "redisdb-master.default.svc.cluster.local"
    )
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = os.getenv("REDIS_SERVER_HTTP_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_PASSWORD = "YnkNRT0jv5"
    logger.info(
        f"Connecting to redis / host : {REDIS_HOST} port : {REDIS_PORT}"
    )
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=0,
        decode_responses=True,
    )
    return r


# ~~~ Redis Functions ~~~
def write_userdata_to_redis(redis_client, key, dict_mapping):
    logger.info(f"Writing to redis: {key} {dict_mapping}")
    redis_client.hset(key, mapping=dict_mapping)


def read_userdata_from_redis(redis_client, key):
    value = redis_client.hgetall(key)
    logger.info(f"reading from redis: {value}")
    return value if value else None


# ~~~ Variables globales ~~~
logger = setup_logging()
app = FastAPI()
bot, dp = init_bot()
redis_db = init_redis()

WELCOME_MESSAGE = """Welcome to SwissAi Center :-)
I am AIFred, an autonomous API agent, capable to give you information from the APIs that I have in stock.

"""


# ~~~ Pydantic models ~~~
class UserMessage(BaseModel):
    user_id: str
    message: str


# ~~~ FastAPI listener ~~~
@app.get("/status/")
async def get_status():
    """
    Check the status of the API.

    Returns
    -------
    dict
    """
    return {"status": "API is running"}


@app.post("/reply_to_user/")
async def reply_to_user(user_message: UserMessage):
    user_id = user_message.user_id
    message = user_message.message
    logger.info(f"Sending {message} to user {user_id}")

    try:
        await bot.send_message(chat_id=user_id, text=message)
        logger.info(f"Message sent successfully to user {user_id}")
        return {"message": "Message sent successfully"}
    except Exception as e:
        logger.error(f"Failed to send message to user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ~~~ Aiogram handlers ~~~
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)
    user_name = str(message.from_user.username)

    if not redis_db.exists(user_id):
        await message.reply(
            f"{WELCOME_MESSAGE}Welcome {user_name}, just in case your user ID is: {str(user_id)} Make sure your OPENAI API key is set before you start chatting with me."
        )
        empty_dict = {"api_key": "", "messageHistory": ""}
        write_userdata_to_redis(redis_db, user_id, empty_dict)
    else:
        await message.reply(f"{WELCOME_MESSAGE}Welcome back {user_name}!")


@dp.message()
async def echo_handler(message: types.Message):
    user_id = str(message.from_user.id)
    HOST = "192.168.49.2"
    PORT = 32290
    system_http_url = f"http://{HOST}:{PORT}/get_similar_apis/"
    user_data = {"user_id": user_id, "prompt": message.text, "k": 3}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(system_http_url, json=user_data)
            if response.status_code == 200:
                logger.info(f"Data sent successfully: {response.json()}")
                msg = "Here are the similar APIs that you might be interested in:\n"
                docs = [
                    json.loads(doc) for doc in response.json()["documents"][0]
                ]
                content = [
                    f"{c['API_Title'][:-2]}\n\t\t\t{c['Endpoint_Description']}\n"
                    for c in docs
                ]
                content = "".join(content)
                await bot.send_message(chat_id=user_id, text=f"{msg}{content}")

            else:
                logger.error(f"Failed to send data: {system_http_url}")
                logger.error(f"Failed to send data: {response}")
        except Exception as e:
            logger.error(f"Failed to send data: {str(e)}")
            await message.answer("Failed to process your message.")
            return


# ~~~ Start Telegram Bot ~~~
async def start_telegram_bot():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


# ~~~ Start FastApi ~~~
async def start_fastapi():
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8080, loop="asyncio")
    server = uvicorn.Server(config)
    await server.serve()


# ~~~ Main Function ~~~
async def start_app():
    bot_task = asyncio.create_task(start_telegram_bot())
    api_task = asyncio.create_task(start_fastapi())
    await asyncio.gather(bot_task, api_task)


if __name__ == "__main__":
    asyncio.run(start_app())
