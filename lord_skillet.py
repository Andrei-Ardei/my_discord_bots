import discord
from discord import Game
from discord.ext import commands, tasks
import random
from random import choice
import requests
import json
import os
import csv
from personal_library import giveaway_requests
from datetime import datetime, date, timedelta, time
import pytz

intents = discord.Intents.default()

if os.name == "nt":
    intents.message_content = True
else:
    intents.messages = True

intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

bot_locations = [" and quietly listening"]
################### FUNCTIONS BELOW ##############

def append_data_to_csv(filename, date,game_title):
    if not os.path.isfile(filename):
        # File does not exist, create a new one and write headers
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "game_title"])  # Write headers
            writer.writerow([date, game_title])  # Write data
    else:
        # File exists, append data
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, game_title])  # Write data

def check_game_title(filename, game_title):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        
        for row in reader:
            date_str = row[0]  # Assuming the date is in the first column
            game_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
            
            if game_date >= thirty_days_ago and game_date <= today and row[1] == game_title:
                return True  # Game title found within the past 30 days

    return False  # Game title not found within the past 30 days


###END FUNCTIONS

@bot.event  # print that the bot is ready to make sure that it actually logged on
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    await bot.change_presence(activity=Game(name=f"{choice(bot_locations)}"))
    myLoop.start()


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



# loop task every day
utc = pytz.UTC
times = [
    time(hour=8, tzinfo=utc),
    time(hour=12, minute=30, tzinfo=utc),
    time(hour=16, minute=40, second=30, tzinfo=utc),
    time(hour=18, minute=59, tzinfo=utc)
]
@tasks.loop(hours=4)  # use - seconds=5, count=1 - for testing, time=times for live
async def myLoop():
    data = giveaway_requests.get_giveaways()

#check if we have already sent this today
    filename = os.sep.join(["personal_library","game_history.csv"])
    #Loop through all potential giveaways in a day
    for giveaway in data:
        did_we_send_this_today = check_game_title(filename=filename,game_title=giveaway['title'])
        print(f"Did we really already send this game?: {did_we_send_this_today}")
        if did_we_send_this_today:
            print("do not post the results")
        else:
            def get_final_url(url):
                response = requests.get(url, allow_redirects=True)
                return response.url

            final_url = get_final_url(giveaway['open_giveaway_url'])

            embed = discord.Embed(
            title=giveaway['title'],
            description=giveaway['description'],
            color=discord.Color.green(),
            url=final_url
            )
            embed.set_thumbnail(url=giveaway['thumbnail'])
            embed.set_image(url=giveaway['image'])
            embed.add_field(name='Worth', value=giveaway['worth'])
            embed.add_field(name='Instructions', value=giveaway['instructions'], inline=False)
            embed.add_field(name='Platforms', value=giveaway['platforms'])
            embed.add_field(name='End Date', value=giveaway['end_date'])
            embed.set_footer(text='Published on: ' + giveaway['published_date'])

            #channel send message
            channel_id=1049021869648523335
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed)
            append_data_to_csv(filename=filename,date=giveaway['published_date'],game_title=giveaway['title'])

#####LOGIN
# set folder path for key based on the environment
if os.name == "nt":
    path = os.sep.join(["C:", "users", "Andrei", "vault.json"])
elif os.name == "posix":
    path = os.sep.join(["/", "home", "pi", "key", "vault.json"])


# open file
f = open(path)
# load it as json
j = json.load(f)
# store the key value

bot.run(str(j["lord_skillet"]["key"]))
#END LOGIN

