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

# Function to write a value to a key in a Redis database
async def write_dict_to_redis(dict_key, dict_mapping):
    # Connect to Redis
    print("Connecting to redis / host : ", REDIS_NET, " port : ", REDIS_PORT)
    r = redis.Redis(host=REDIS_NET, port=REDIS_PORT, db=0)
    print("Writing to redis:", dict_key, dict_mapping)
    # Set the value for the given key
    r.hset(dict_key, mapping=dict_mapping)

    # Optionally, you can specify an expiration time for the key
    # r.expire(key, 3600)  # This would expire the key in 1 hour (3600 seconds)

# Function to write a value to a key in a Redis database
async def read_dict_from_redis(dict_key):
    # Connect to Redis
    print("Connecting to redis / host : ", REDIS_NET, " port : ", REDIS_PORT)
    r = redis.Redis(host=REDIS_NET, port=REDIS_PORT, db=0)
    
    # Set the value for the given key
    value = r.hgetall(dict_key)
    print("reading from redis:", value)
    return value if value else None
 
    # Optionally, you can specify an expiration time for the key
    # r.expire(key, 3600)  # This would expire the key in 1 hour (3600 seconds)


@dp.message(StringFilter("/getHistory"))
async def get_history(message: types.Message):
    """
    Handler for the /getHistory command to get the chat history.
    """
    user_id = message.from_user.id

    userID_key = f"{user_id}"
    print("want history from user : ", userID_key)
    # Read chat history from Redis
    user_data = await read_dict_from_redis(userID_key)
    print("chat history : ", user_data)
    if user_data:
        # Convert bytes to dictionary
        existing_userData_decoded = {key.decode(): value.decode() for key, value in user_data.items()}
        
        chat_history = str(existing_userData_decoded['messageHistory'])


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
        memory[user_id] = {"userID": user_id, "api_key" : "empty","messageHistory": [], "hasAPIKey": '0'}
        # username does not exist it prints "None" 
        # username = message.from_user.username
        # print(username)
        # username_key = f"{user_id}_username"
        
        all_users_key = "allUsers"
        
        userID_key = f"{user_id}"

        empty_dict = {'api_key': 'empty', 'messageHistory': 'empty'}
        # Write username to Redis
        # await write_to_redis(username_key, username)
        # Write an empty list to Redis for the chat history
        await write_dict_to_redis(userID_key, empty_dict)
        #await write_to_redis(chat_history_key, "empty chat history")

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
    
    if user_id in memory and memory[user_id]["hasAPIKey"] == '0':
        await message.reply("Your next message will be considered as your API key.")
        memory[user_id]["hasAPIKey"] = '1'
        
        # consider that the next message will be the API key so now user has API key
        user_data = await read_dict_from_redis(f"{user_id}")
        print("user_data:", user_data)
        if user_data:
            # Convert bytes to dictionary
            existing_userData_decoded = {key.decode(): value.decode() for key, value in user_data.items()}
            print("existing_userData_decoded:", existing_userData_decoded)
            # Append message_dict to "messageHistory"
            existing_userData_decoded['hasAPIKey'] = '1'
            # Serialize updated data back to bytes
            updated_userData = {"api_key" : existing_userData_decoded["api_key"], "messageHistory" : existing_userData_decoded["messageHistory"]}
        await write_dict_to_redis(f"{user_id}", updated_userData)
        return
    
    elif user_id in memory and memory[user_id]["hasAPIKey"] == '1' or memory[user_id]["hasAPIKey"] == 'S':
        await message.reply("your api key has already been set.")
        return
    elif user_id not in memory: 
        await message.reply("Please start a session first.")
        return




async def send_data_to_server(data, user_id):
    try:
        userID_key = f"{user_id}"
        # Construct the dictionary with user and system messages

        response = requests.post(f"{SERVER_URL}/messages", json=data)
        print("Response from server:",  response.json())
        message_dict = {
            "user": data['message'],
            "system": response.json()['response']  # Server response
        }
        # Append the dictionary to message history
        memory[user_id]["messageHistory"].append(message_dict)
        redis_data = str(memory[user_id]["messageHistory"])
        print("Writing to redis:", memory[user_id]["messageHistory"])


        existing_userData = await read_dict_from_redis(userID_key)
        print("existing_userData:", existing_userData)
        if existing_userData:
            # Convert bytes to dictionary
            existing_userData_decoded = {key.decode(): value.decode() for key, value in existing_userData.items()}
            print("existing_userData_decoded:", existing_userData_decoded)
            # Append message_dict to "messageHistory"
            existing_userData_decoded['messageHistory'] = redis_data
            # Serialize updated data back to bytes
            updated_userData = {"api_key" : existing_userData_decoded["api_key"], "messageHistory" : redis_data}

        await write_dict_to_redis(userID_key, updated_userData)

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
        
        if memory[user_id]["hasAPIKey"] == '1':
            # write in redis the api key and reply only that the api key has been set
            user_data = await read_dict_from_redis(f"{user_id}")
            print("user_data:", user_data)
            if user_data:
                # Convert bytes to dictionary
                existing_userData_decoded = {key.decode(): value.decode() for key, value in user_data.items()}
                print("existing_userData_decoded:", existing_userData_decoded)
                # Append message_dict to "messageHistory"
                existing_userData_decoded['api_key'] = message.text
                # Serialize updated data back to bytes
                updated_userData = {"api_key" : message.text, "messageHistory" : existing_userData_decoded["messageHistory"]}
            await write_dict_to_redis(f"{user_id}", updated_userData)
            await message.answer("Your API key has been set.")
            memory[user_id]["hasAPIKey"] = 'S'
            return
        
        elif memory[user_id]["hasAPIKey"] == 'S' or memory[user_id]["hasAPIKey"] == '0':


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
