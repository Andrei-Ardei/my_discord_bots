import discord
from discord import Game
from discord.ext import commands
import random
from random import choice
import requests
import json
import os
import csv


intents = discord.Intents.default()

if os.name == "nt":
    intents.message_content = True
else:
    intents.messages = True

intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot_locations = [" and quietly listening to everything you say"]


@bot.event  # print that the bot is ready to make sure that it actually logged on
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    await bot.change_presence(activity=Game(name=f"{choice(bot_locations)}"))


@bot.command(pass_context=True)  # define the first command and set prefix to '!'
async def hello(ctx):
    await ctx.send("Hello!!")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    print(message.author)
    print(message.content)
    ######################################################## record messages
    filename = "skillet_data.csv"

    if not os.path.isfile(filename):
        # File does not exist, create a new one and write headers
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Message"])  # Write headers
            writer.writerow([message.author, message.content])  # Write data
    else:
        # File exists, append data
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([message.author, message.content])  # Write data

    ####################################################### stop record messages
    match message.content:
        case "$hello":
            await message.channel.send("Hello!")

        case "$mananci cariciu":
            await message.channel.send("ba tu pe-al meu")

        case "purple ketchup":
            await message.channel.send("Yum yum, delicious.")


# set folder path for key based on the environment
if os.name == "nt":
    path = os.sep.join(["C:", "users", "Andrei", "vault.json"])
elif os.name == "posix":
    path = os.sep.join(["home", "pi", "key", "vault.json"])


# open file
f = open(path)
# load it as json
j = json.load(f)
# store the key value

bot.run(str(j["lord_skillet"]["key"]))
