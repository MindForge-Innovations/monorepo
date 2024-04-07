import asyncio
import sys

import telebot
import requests
from flask import Flask, request
import json
import logging
from dotenv import load_dotenv
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Filter
from aiogram.enums import ParseMode
from aiogram.types import Message



import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

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
dp = Dispatcher()
memory = {}

helpMessage = """Welcome to AIFred. :-)
I am an autonomous API agent, capable to give you information from the APIs that I have in stock."""

# Define custom filter
class StartSession(Filter):
    def __init__(self, my_text: str) -> None:
        self.my_text = my_text

    async def __call__(self, message: Message) -> bool:
        return message.text == self.my_text




@dp.message(StartSession("/startSession"))
async def start(message: types.Message):
    """
    Handler for the /startSession command to start a session.
    """
    user_id = message.from_user.id
    if user_id not in memory:
        memory[user_id] = {"userID": user_id, "messageHistory": []}
    print(memory)
    await message.reply("Session started. You can start chatting.")

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.reply("Hi! Send /startSession to start a session.")

async def send_data_to_server(data,userID):
    try:
        # Open a connection to the server
        reader, writer = await asyncio.open_connection('127.0.0.1', 5000)

        # Send data
        writer.write(data.encode())

        # Read response
        response = await reader.read(1024)


        # Construct the dictionary with user and system messages
        message_dict = {
            "user": json.loads(data)['message'],
            "system": response.decode()  # Server response
        }

        # Append the dictionary to message history
        memory[userID]["messageHistory"].append(message_dict)
        # Close the connection
        writer.close()
        await writer.wait_closed()
        return response.decode()  # Return the response
    except Exception as e:
        print("Error:", e)

@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    #print(message)
    user_id = message.from_user.id
    #if user_id in memory:
    #    memory[user_id]["messageHistory"].append({"user" : message.text})

    print("entering try")
    try:

        data_to_send = {
            "userId": user_id,
            # "messageHistory": memory[user_id]["messageHistory"]
            "message" : message.text
        }
        # Convert data to JSON format
        json_data = json.dumps(data_to_send)
        # Send the JSON data to the server
        # client_socket.sendall(json_data.encode())
        # data = client_socket.recv(1024)
        print("Sending to srv")

        # Send data to the server asynchronously
        response = await send_data_to_server(json_data, user_id)  # Get the response
        print("Received from server:", response)
        print(memory)
        await message.answer(response)  # Use the response in message.answer()
        #await message.send_copy(chat_id=message.chat.id)
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

    print("Connected to server on port", SERVER_PORT)

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
