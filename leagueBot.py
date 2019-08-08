# Work with Python 3.6
import discord
from discord.ext import commands
import requests
from key import key

#league info
print(key)

leagueDict =  {
    'RANKED_SOLO_5x5': 'Solo Queue',
    'RANKED_FLEX_SR': 'Summoner\'s Rift Flex',
    'RANKED_TFT': 'Teamfight Tactics',
    'RANKED_FLEX_TT': 'Twisted Treeline Flex',
    'CHALLENGER': 'Challenger',
    'GRANDMASTER':  'Grandmaster',
    'MASTER': 'Master',
    'DIAMOND': 'Diamond',
    'PLATINUM':  'Platinum',
    'GOLD': 'Gold',
    'SILVER': 'Silver',
    'BRONZE': 'Bronze',
    'IRON': 'Iron'
}

TOKEN = 'NjA4Nzc2NDcxMjQyMzQyNDAx.XUw9ow.rCfU4o8THvojoGLyFwVgHiCv9uQ'

bot = commands.Bot(command_prefix  = '!')

@bot.event

@bot.event
async def on_ready():
    print('The bot is ready!')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def hello(ctx):
    member = ctx.message.author.id
    await ctx.send(f'Hello <@{member}>')

@bot.command()
async def test(ctx):
    embed = discord.Embed(title="nice bot", description="Nicest bot there is ever.", color=0xeee657)

    # give info about you here
    embed.add_field(name="Author", value="cats?")

    await ctx.send(embed=embed)


@bot.command()
async def test1(ctx, name: str):
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    summonerInfoRequest = requests.get(url = summonerInfoURL).json()
    print(summonerInfoRequest)
    print('status' in summonerInfoRequest)

    await ctx.send('testing')

@bot.command() #get summoner info
async def info(ctx, name: str):
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    summonerInfoRequest = requests.get(url = summonerInfoURL).json()
    if 'status' in summonerInfoRequest:
        error = summonerInfoRequest['status']['status_code']
        response = f'> Error! Status Code {error}'
        await ctx.send(response)
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    detailedInfoURL  =  f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={key}'
    detailedInfoRequest = requests.get(url  =  detailedInfoURL).json()
    rankedInfo = f'>>> __**{summonerName}** ranked info:__\n'
    for queue in detailedInfoRequest:
        queueType = leagueDict[queue['queueType']]
        tier = leagueDict[queue['tier']]
        if tier in ['Challenger', 'Grandmaster', 'Master']:
            rank = ''
        else:
            rank = queue['rank']
        lp =  queue['leaguePoints']
        wins  = queue['wins']
        losses = queue['losses']
        rankedInfo += f'**{queueType}:**\n\t{tier} {rank} {lp} LP\n\t{int(wins/(losses+wins)*100)}% win ratio\n\t{wins} wins {losses} losses\n'
    await ctx.send(rankedInfo)

    

@bot.command() #get game info
async def game(ctx, name: str):
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    summonerInfoRequest = requests.get(url = summonerInfoURL).json()
    encryptedSummonerId = summonerInfoRequest['id']
    gameInfoURL =  f'https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}?api_key={key}'
    gameInfoRequest = requests.get(url = gameInfoURL).json()
    await ctx.send('hi')

bot.run(TOKEN)