"""
This module provides a Telegram bot able to interact with the user
and retrieves information from connected APIs.
"""

# ~~~ Imports ~~~
import asyncio
import sys
import os
import logging
from colorlog import ColoredFormatter

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Filter
from aiogram.enums import ParseMode
from aiogram.types import Message

import redis
import requests

# ___________________________________________________________________________________________
# TEMPORARY: Load environment variables from .env file
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file

import warnings

warnings.filterwarnings("ignore")
# ___________________________________________________________________________________________


# ~~~ Configuration du Logger ~~~
def get_logger():
    global logger
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

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    return logger


# ~~~ Variables globales ~~~
global dp
global chatID
global bot
global TELEGRAM_BOT_TOKEN
memory = {}
redis_client = None

WELCOME_MESSAGE = """Welcome to AIFred. :-)
I am an autonomous API agent, capable to give you information from the APIs that I have in stock.
You can start a session by sending /startSession."""

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TELEGRAM_BOT_TOKEN")

ORCHESTRATOR_HOST = os.getenv("ORCHESTRATOR_HOST")
ORCHESTRATOR_PORT = os.getenv("ORCHESTRATOR_PORT")

SERVER_URL = f"http://{ORCHESTRATOR_HOST}:{ORCHESTRATOR_PORT}"


# ~~~ Connection to Redis ~~~
def connect_to_redis():
    REDIS_HOST = os.getenv(
        "REDIS_HOST", "redisdb-master.default.svc.cluster.local"
    )
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    logger.info(
        "Connecting to redis / host : ", REDIS_HOST, " port : ", REDIS_PORT
    )
    r = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0
    )
    return r


# ~~~ Redis Functions ~~~
async def write_userdata_to_redis(dict_key, dict_mapping):
    logger.info("Writing to redis:", dict_key, dict_mapping)
    redis_client.hset(dict_key, mapping=dict_mapping)


async def read_userdata_from_redis(dict_key):
    value = redis_client.hgetall(dict_key)
    logger.info("reading from redis:", value)
    return value if value else None


# ~~~ String Filter ~~~
class StringFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text


# ~~~ Command Handlers ~~~
@dp.message(StringFilter("/getHistory"))
async def get_history(message: types.Message):
    """
    Handler for the /getHistory command to get the chat history.
    """
    user_id = message.from_user.id
    logger.info("want history from user : ", user_id)

    # Read chat history from Redis
    user_data = await read_userdata_from_redis(user_id)
    logger.info("chat history : ", user_data)

    if user_data:
        existing_userData_decoded = {
            key.decode(): value.decode() for key, value in user_data.items()
        }
        chat_history = str(existing_userData_decoded["messageHistory"])
        await message.reply(chat_history)
    else:
        await message.reply("No chat history found.")


@dp.message(StringFilter("/startSession"))
async def start(message: types.Message):
    """
    Handler for the /startSession command to start a session.
    """
    user_id = message.from_user.id

    if user_id not in memory:
        memory[user_id] = {
            "userID": user_id,
            "api_key": "empty",
            "messageHistory": [],
            "hasAPIKey": "0",
        }

        userID_key = f"{user_id}"

        empty_dict = {"api_key": "empty", "messageHistory": "empty"}
        await write_userdata_to_redis(userID_key, empty_dict)

    await message.reply("Session started. You can start chatting.")


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply(WELCOME_MESSAGE)


# TODO: implement a service to set the API key of telegram user externally
# @dp.message(StringFilter("/setApiKey"))
# async def start(message: types.Message):
#     """
#     Handler for the /setApiKey command to register a userApiKey.
#     """
#     user_id = message.from_user.id

#     if user_id in memory and memory[user_id]["hasAPIKey"] == '0':
#         await message.reply("Your next message will be considered as your API key.")
#         memory[user_id]["hasAPIKey"] = '1'

#         # consider that the next message will be the API key so now user has API key
#         user_data = await read_dict_from_redis(f"{user_id}")
#         logger.info("user_data:", user_data)
#         if user_data:
#             # Convert bytes to dictionary
#             existing_userData_decoded = {key.decode(): value.decode() for key, value in user_data.items()}
#             logger.info("existing_userData_decoded:", existing_userData_decoded)
#             # Append message_dict to "messageHistory"
#             existing_userData_decoded['hasAPIKey'] = '1'
#             # Serialize updated data back to bytes
#             updated_userData = {"api_key" : existing_userData_decoded["api_key"], "messageHistory" : existing_userData_decoded["messageHistory"]}
#         await write_dict_to_redis(f"{user_id}", updated_userData)
#         return

#     elif user_id in memory and memory[user_id]["hasAPIKey"] == '1' or memory[user_id]["hasAPIKey"] == 'S':
#         await message.reply("your api key has already been set.")
#         return
#     elif user_id not in memory:
#         await message.reply("Please start a session first.")
#         return


async def send_data_to_server(data, user_id):
    try:
        userID_key = f"{user_id}"
        # Construct the dictionary with user and system messages

        response = requests.post(f"{SERVER_URL}/messages", json=data)
        logger.info("Response from server:", response.json())
        message_dict = {
            "user": data["message"],
            "system": response.json()["response"],  # Server response
        }
        # Append the dictionary to message history
        memory[user_id]["messageHistory"].append(message_dict)
        redis_data = str(memory[user_id]["messageHistory"])
        logger.info("Writing to redis:", memory[user_id]["messageHistory"])

        existing_userData = await read_userdata_from_redis(userID_key)
        logger.info("existing_userData:", existing_userData)
        if existing_userData:
            # Convert bytes to dictionary
            existing_userData_decoded = {
                key.decode(): value.decode()
                for key, value in existing_userData.items()
            }
            logger.info("existing_userData_decoded:", existing_userData_decoded)
            # Append message_dict to "messageHistory"
            existing_userData_decoded["messageHistory"] = redis_data
            # Serialize updated data back to bytes
            updated_userData = {
                "api_key": existing_userData_decoded["api_key"],
                "messageHistory": redis_data,
            }

        await write_userdata_to_redis(userID_key, updated_userData)

        return response.json()["response"]
    except Exception as e:
        logger.info("Error send_data:", e)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    # logger.info(message)
    user_id = message.from_user.id
    if user_id not in memory:
        await message.answer("Please start a session first.")
        return

    logger.info("entering try")
    try:

        if memory[user_id]["hasAPIKey"] == "1":
            # write in redis the api key and reply only that the api key has been set
            user_data = await read_userdata_from_redis(f"{user_id}")
            logger.info("user_data:", user_data)
            if user_data:
                # Convert bytes to dictionary
                existing_userData_decoded = {
                    key.decode(): value.decode()
                    for key, value in user_data.items()
                }
                logger.info(
                    "existing_userData_decoded:", existing_userData_decoded
                )
                # Append message_dict to "messageHistory"
                existing_userData_decoded["api_key"] = message.text
                # Serialize updated data back to bytes
                updated_userData = {
                    "api_key": message.text,
                    "messageHistory": existing_userData_decoded[
                        "messageHistory"
                    ],
                }
            await write_userdata_to_redis(f"{user_id}", updated_userData)
            await message.answer("Your API key has been set.")
            memory[user_id]["hasAPIKey"] = "S"
            return

        elif (
            memory[user_id]["hasAPIKey"] == "S"
            or memory[user_id]["hasAPIKey"] == "0"
        ):

            data_to_send = {
                "userId": user_id,
                # "messageHistory": memory[user_id]["messageHistory"]
                "message": message.text,
            }

            logger.info("Sending to srv")

            response = await send_data_to_server(
                data_to_send, user_id
            )  # Get the response

            logger.info("Received from server:", response)
            if response is None:
                default_message = (
                    "Sorry, there was an issue processing your request."
                )
                await message.answer(default_message)
            else:
                logger.info(memory)
                await message.answer(
                    response
                )  # Use the response in message.answer()

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")


async def main() -> None:
    get_logger()
    bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
