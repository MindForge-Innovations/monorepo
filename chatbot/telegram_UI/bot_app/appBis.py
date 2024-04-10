import asyncio
import sys

#import telebot
#import requests
#from flask import Flask, request
import json
import logging
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Filter
from aiogram.enums import ParseMode
from aiogram.types import Message

import socket

import redis

import requests



# Initialisation du logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

global chatID
global bot
global TOKEN
# Load environment variables from .env file
load_dotenv()
# Get the BOT_TOKEN from the environment variables
TOKEN = os.getenv("BOT_TOKEN")
print("TOKEN loaded")
bot = Bot(token=TOKEN)  # telebot.TeleBot(token=TOKEN)

REDIS_NET = os.getenv("REDIS_NETWORK")
REDIS_PORT = os.getenv("REDIS_PORT")

SYSTEM_NET = os.getenv("SYSTEM_NETWORK")
SYSTEM_PORT = os.getenv("SYSTEM_PORT")

SERVER_URL = "http://"+SYSTEM_NET+":8000"


dp = Dispatcher()
memory = {}

#global r = redis.Redis(host='localhost', port=6379, db=0)

helpMessage = """Welcome to AIFred. :-)
I am an autonomous API agent, capable to give you information from the APIs that I have in stock."""

# Define custom filter
class StringFilter(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text

# Function to read a value from a key in a Redis database
async def read_from_redis(key):
    # Connect to Redis
    # print("Reading from redis value with key : ", key)
    r = redis.Redis(host=REDIS_NET, port=REDIS_PORT, db=0)

    # Attempt to retrieve value from the key
    value = r.get(key)
    # print("Value returned from redis : ", value)
    # Return the value
    return value.decode('utf-8') if value else None

# Function to write a value to a key in a Redis database
async def write_to_redis(key, value):
    # Connect to Redis
    print("Connecting to redis / host : ", REDIS_NET, " port : ", REDIS_PORT)
    r = redis.Redis(host=REDIS_NET, port=REDIS_PORT, db=0)
    print("Writing to redis:", key, value)
    # Set the value for the given key
    r.set(key, value)

    # Optionally, you can specify an expiration time for the key
    # r.expire(key, 3600)  # This would expire the key in 1 hour (3600 seconds)


@dp.message(StringFilter("/getHistory"))
async def get_history(message: types.Message):
    """
    Handler for the /getHistory command to get the chat history.
    """
    user_id = message.from_user.id

    chat_history_key = f"{user_id}_chatHistory"
    print("want history : ", chat_history_key)
    # Read chat history from Redis
    chat_history = await read_from_redis(chat_history_key)
    print("chat history : ", chat_history)
    if chat_history:
        #chat_history_text = ""
        #for message in chat_history:
        #    chat_history_text += f"User: {message['user']}\nSystem: {message['system']}\n\n"
        #print(chat_history_text)
        # Send the chat history
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
        memory[user_id] = {"userID": user_id, "messageHistory": []}
        # username does not exist it prints "None" 
        # username = message.from_user.username
        # print(username)
        # username_key = f"{user_id}_username"
        
        all_users_key = "allUsers"
        
        chat_history_key = f"{user_id}_chatHistory"
        user_api_key = f"{user_id}_apiKey"

        # Write username to Redis
        # await write_to_redis(username_key, username)
        # Write an empty list to Redis for the chat history

        await write_to_redis(chat_history_key, "empty chat history")
        await write_to_redis(user_api_key, "empty api key")

    # print(memory)
    await message.reply("Session started. You can start chatting.")

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply("Hi! Send /startSession to start a session.")


@dp.message(StringFilter("/setApiKey"))
async def start(message: types.Message):
    """
    Handler for the /setApiKey command to register a userApiKey.
    """
    user_id = message.from_user.id  
    splitted_message = message.text.split(maxsplit=1)
    if len(splitted_message) < 2:
        await message.reply("Please provide an API key. \n Usage: /setApiKey <API_KEY>")
        return
    elif user_id in memory:
        user_api_key = f"{user_id}_apiKey"
        await write_to_redis(user_api_key, splitted_message[1])
        await message.reply("API key set successfully.")
        return
    else : 
        await message.reply("Please start a session first.")
        return




async def send_data_to_server(data, user_id):
    try:
        chat_history_key = f"{user_id}_chatHistory"
        # Construct the dictionary with user and system messages


        response = requests.post(f"{SERVER_URL}/messages", json=data)
        print("Response from server:",  response.json())
        message_dict = {
            "user": data['message'],
            "system": response.json()['response']  # Server response
        }
        # Append the dictionary to message history
        memory[user_id]["messageHistory"].append(message_dict)
        print("Writing to redis:", memory[user_id]["messageHistory"])

        await write_to_redis(chat_history_key, str(memory[user_id]["messageHistory"]))

        return response.json()["response"]
    except Exception as e:
        print("Error send_data:", e)


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    #print(message)
    user_id = message.from_user.id
    if user_id not in memory:
        await message.answer("Please start a session first.")
        return

    print("entering try")
    try:

        data_to_send = {
            "userId": user_id,
            # "messageHistory": memory[user_id]["messageHistory"]
            "message" : message.text
        }

        print("Sending to srv")

        # Send data to the server asynchronously
        response = await send_data_to_server(data_to_send, user_id)  # Get the response
        
        print("Received from server:", response)
        if response is None:
            default_message = "Sorry, there was an issue processing your request."
            await message.answer(default_message)
        else:   
            print(memory)
            await message.answer(response)  # Use the response in message.answer()

    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")




async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)



if __name__ == "__main__":
    # Create a socket object
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the server
    # Connect to the server
    # client_socket.connect((SERVER_IP, SERVER_PORT))

    # print("Connected to server on port", SERVER_PORT)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
