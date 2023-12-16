import discord
from discord.ext import commands, tasks
from random import choice
import requests
import os
import csv
from personal_library import giveaway_requests, API_dictionary_request, steam_games_sale_tracker, API_Weather
from datetime import time
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


@bot.event  # print that the bot is ready to make sure that it actually logged on
async def on_ready():
    print("Logged in as:")
    print(bot.user.name)
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


@bot.command(pass_context=True)
async def track(ctx, *, arg=None):
    """Track your favourite game on steam for a discount."""

    if arg == "gbp":
        cc_param = "gb"
    elif arg == "eur":
        cc_param = "ie"
    else:
        cc_param = "us"

    await ctx.message.author.send(f"Hey {ctx.message.author.mention}, which game would you like me to track for you? ")

    def check(message):
        return message.author == ctx.message.author and message.channel == ctx.message.channel

    reply_message = await bot.wait_for('message', check=check, timeout=60.0)

    if reply_message.content.lower().strip() == 'no':
        await ctx.message.author.send(f"Okay, I am going back to sleep.")
    else:
        games_list = steam_games_sale_tracker.fetch_list_of_games_by_name(
            reply_message.content.lower().strip())
        counter = 1
        bot_message = ''
        if len(games_list) == 1:
            # Process list of game as single
            my_dict = {
                "app_name": games_list[0]['name'],
                "app_id": games_list[0]['appid'],
                "author_id": ctx.message.author.id,
                "pref_cur": cc_param
            }
            helper.dump_dict_to_json(my_dict, helper.notifications_json_file)
            await ctx.message.author.send(f"Ok, I will track {games_list[0]['name']} for you.")
        elif len(games_list) > 2 and len(games_list) < 20:
            # Process more results
            for game in games_list:
                bot_message += str(counter)+'. '+game['name']+'\r\n'
                counter += 1
            await ctx.message.author.send(f"{bot_message}\r\nPlease select your choice by replying with a number from 1 to {counter-1}")
            reply_choice = await bot.wait_for('message', check=check, timeout=60.0)
            choice = int(reply_choice.content)

            my_dict = {
                "app_name": games_list[choice-1]['name'],
                "app_id": games_list[choice-1]['appid'],
                "author_id": ctx.message.author.id,
                "pref_cur": cc_param
            }

            helper.dump_dict_to_json(my_dict, helper.notifications_json_file)
            await ctx.message.author.send(f"Ok, I will track {games_list[choice-1]['name']} for you.")

        elif len(games_list) > 20:
            await ctx.message.author.send(f"Found {len(games_list)} games. This is a bit too much to send in the chat. Can you try to narrow it down by being more specific?")
        else:
            # No results
            await ctx.message.author.send("Couldn't find any games like that.")


@bot.command()
async def weather(ctx, *, city: str):
    """ weather function """
    await ctx.message.delete()
    result = API_Weather.unpack_response(city)
    if isinstance(result, str):
        await ctx.send(f'{result} - {city}')
    else:
        e = discord.Embed(
            title=f"There is {round(float(result['cur_temp']))}°C in {city}")
        e.add_field(name="Max Temperature", value=f"{result['max_temp']}°C")
        e.add_field(name="Min Temperature", value=f"{result['min_temp']}°C")
        e.add_field(name="Humidity", value=f"{result['humidity']}%")
        e.add_field(name="Wind Speed", value=f"{result['wind_speed']}m/s")
        e.add_field(name="Forecast", value=f"{result['cloudiness']}")
        e.set_thumbnail(url=result['weather_icon'])
        await ctx.send(embed=e)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    print(message.author)
    print(message.content)
    # record messages
    helper.record_messages(message)

# use - seconds=5, count=1 - for testing
# use minutes=30 for live


@tasks.loop(minutes=30)
async def myLoop():
    data = giveaway_requests.get_giveaways()

    # check if we have already sent this today

    if os.name == "nt":
        filename = os.sep.join(["personal_library", "game_history.csv"])
    elif os.name == "posix":
        filename = os.sep.join(
            ["/", "home", "menajerulrobotilor", "git_projects", "my_discord_bots", "personal_library", "game_history.csv"])

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

    discord_users = helper.get_unique_author_ids()
    for user in discord_users:
        list_of_games = helper.get_elements_by_author_id(
            helper.notifications_json_file, user)

        list_of_discounts = helper.verify_games(list_of_games)
        if list_of_discounts:
            recipient = await bot.fetch_user(user)

            combined_message = '\n'.join(list_of_discounts)

            await recipient.send(combined_message)

# LOGIN
bot.run(auth.KEY_BOT)
# END LOGIN
