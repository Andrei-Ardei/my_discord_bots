import discord
from discord import Game
from discord.ext import commands, tasks
from random import choice
import requests
import os
import csv
from personal_library import giveaway_requests, API_dictionary_request
from datetime import datetime, date, timedelta, time
import pytz
import auth
import helper

utc = pytz.UTC
times = [
    time(hour=8, tzinfo=utc),
    time(hour=12, minute=30, tzinfo=utc),
    time(hour=16, minute=40, second=30, tzinfo=utc),
    time(hour=18, minute=59, tzinfo=utc)
]

intents = discord.Intents.default()

if os.name == "nt":
    intents.message_content = True
else:
    intents.messages = True

intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)

bot_locations = [" and quietly listening"]


# FUNCTIONS BELOW

def append_data_to_csv(filename, date, game_title):
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

# END FUNCTIONS


@bot.event  # print that the bot is ready to make sure that it actually logged on
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
    await bot.change_presence(activity=Game(name=f"{choice(bot_locations)}"))
    myLoop.start()


# define the first command
@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send("Hello!!")


@bot.command(pass_context=True)
async def word(ctx, *, arg):
    '''Returns the word definition eg.,> $word horse <'''
    word_definition_list = API_dictionary_request.query_dictionary(arg)

    if not 'title' in word_definition_list and len(word_definition_list) > 0:
        list_of_word_descriptions = helper.parse_online_dictionary_results(
            word_definition_list=word_definition_list)
        word_descriptions = '\r\n\r\n'.join(list_of_word_descriptions)
        embed = discord.Embed(
            # title=f'**{arg.lower()}**',
            description=word_descriptions,
            color=discord.Color.from_rgb(5, 243, 255),
            # url=final_url
        )
        embed.set_thumbnail(url='https://freesvg.org/img/Cat-in-a-pan.png')

        # embed.add_field(name='Instructions', value='test', inline=False)
        # embed.set_footer(text='Published on: ')

        await ctx.send(embed=embed)
    elif 'title' in word_definition_list:
        embed2 = discord.Embed(
            title=f'{word_definition_list["title"]}',
            description=f'{word_definition_list["message"]}\r\n{word_definition_list["resolution"]}',
            color=discord.Color.from_rgb(237, 67, 55),
            # url=final_url
        )
        await ctx.send(embed=embed2)
    else:
        await ctx.send('There is some error with the dictionary, please investigate.')


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    print(message.author)
    print(message.content)
    # record messages
    helper.record_messages(message)

# use - seconds=5, count=1 - for testing, time=times for live


@tasks.loop(minutes=30)
async def myLoop():
    data = giveaway_requests.get_giveaways()

    # check if we have already sent this today

    if os.name == "nt":
        filename = os.sep.join(["personal_library", "game_history.csv"])
    elif os.name == "posix":
        filename = os.sep.join(
            ["/", "home", "pi", "git_projects", "my_discord_bots", "personal_library", "game_history.csv"])

    # filename = os.sep.join(["personal_library","game_history.csv"])
    # Loop through all potential giveaways in a day
    for giveaway in data:
        did_we_send_this_today = helper.check_game_title(
            filename=filename, game_title=giveaway['title'])
        print(
            f"Did we really already send this game?: {did_we_send_this_today}")
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
            embed.add_field(name='Instructions',
                            value=giveaway['instructions'], inline=False)
            embed.add_field(name='Platforms', value=giveaway['platforms'])
            embed.add_field(name='End Date', value=giveaway['end_date'])
            embed.set_footer(text='Published on: ' +
                             giveaway['published_date'])

            # channel send message
            channel_id = 925636804823121951
            channel = bot.get_channel(channel_id)
            await channel.send(embed=embed)
            helper.append_data_to_csv(
                filename=filename, date=giveaway['published_date'], game_title=giveaway['title'])


# LOGIN
bot.run(auth.KEY_BOT)
# END LOGIN
