# Work with Python 3.6
import discord
from discord.ext import commands
import requests
from secrets import key, token
from leagueDict import queueMode, rank, queueId, champs

#api calls
def summonerInfoAPI(name):
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    return requests.get(url = summonerInfoURL).json()

def detailedInfoAPI(encryptedSummonerId):
    detailedInfoURL  =  f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={key}'
    return requests.get(url  =  detailedInfoURL).json()

def gameInfoAPI(encryptedSummonerId):
    gameInfoURL =  f'https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}?api_key={key}'
    return requests.get(url = gameInfoURL).json()

#functions
def playerInfo(player):
    name  = player['name']
    champ = player['champion']
    soloRank = player['rank']
    return f'\t\t**{champ}** {name}\n\t\t\t{soloRank}\n'

def division(queue, tier):
    if tier in ['Challenger', 'Grandmaster', 'Master']:
        return ''
    else:
        return queue['rank']

TOKEN = token

bot = commands.Bot(command_prefix  = '!')
bot.remove_command('help')

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
    await ctx.send(f'Hello <@{member}>! Remember to have fun!')

@bot.command() #get summoner info
async def info(ctx, name: str):
    summonerInfoRequest = summonerInfoAPI(name)
    #summoner  not  found/bad api key
    if 'status' in summonerInfoRequest:
        error = summonerInfoRequest['status']['status_code']
        response = f'> Error! Status Code {error}'
        await ctx.send(response)
        return
    #summoner found
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    detailedInfoRequest = detailedInfoAPI(encryptedSummonerId)
    summonerRankedInfo = f'>>> __**{summonerName}** ranked info:__\n'
    response = summonerRankedInfo
    for queue in detailedInfoRequest:
        queueType = queueMode[queue['queueType']]
        tier = rank[queue['tier']]
        division = division(queue, tier)
        lp =  queue['leaguePoints']
        wins  = queue['wins']
        losses = queue['losses']

        mode = f'**{queueType}:**\n'
        queueInfo = f'\t{tier} {division} {lp} LP\n'
        winRatio = f'\t{int(wins/(losses+wins)*100)}% win ratio\n'
        winLoss = f'\t{wins} wins {losses} losses\n'
        response += (mode + queueInfo + winRatio + winLoss)
    await ctx.send(response)

    

@bot.command() #get game info
async def game(ctx, name: str):
    summonerInfoRequest = summonerInfoAPI(name)
    #summoner not  found/bad api key
    if 'status' in summonerInfoRequest:
        error = summonerInfoRequest['status']['status_code']
        response = f'> Error! Status Code {error}'
        await ctx.send(response)
        return
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    gameInfoRequest = gameInfoAPI(encryptedSummonerId)
    #summoner not  in game/in  tft  game/bad api key
    if 'status' in gameInfoRequest:
        error = gameInfoRequest['status']['status_code']
        errorMsg = f'>>> Error! Status Code {error}\n'
        errorSummoner = f'{summonerName} probably not in a game ¯\\_(ツ)_/¯\n'
        response = errorMsg + errorSummoner
        await ctx.send(response)
        return
    #summoner in game
    gameTypeId = gameInfoRequest['gameQueueConfigId']
    gameType  = queueId[str(gameTypeId)]
    blue = []
    red = []
    for player in gameInfoRequest['participants']:
        info = dict()
        info['name'] = player['summonerName']
        encryptedSummonerId =  player['summonerId']
        champId = str(player['championId'])
        if champId in  champs:
            info['champion'] = champs[champId]
        else:
            info['champion']  = 'Unknown Champion'
        detailedInfoRequest = detailedInfoAPI(encryptedSummonerId)
        for queue in detailedInfoRequest:
            if queue['queueType'] == 'RANKED_SOLO_5x5':
                tier = rank[queue['tier']]
                division = division(queue, tier)
                info['rank'] = f'{tier} {division}'
                break
        if 'rank' not in info:
            info['rank'] = 'Unranked'

        if player['teamId'] == 100:
            blue.append(info)
        else:
            red.append(info)
    gameInfo = f'>>> __**{gameType}**__\n'
    blueSide = '\t**Blue Side**\n'
    response = (gameInfo + blueSide)
    for player in blue:
        response += playerInfo(player)
    redSide = '\t**Red Side**\n'
    response += redSide
    for player in red:
        response += playerInfo(player)
    await ctx.send(response)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Yummi!!", description="Yummi is here to help! List of commands are:", color=0xeee657)

    embed.add_field(name="!hello", value="Says hello!", inline=False)
    embed.add_field(name="!game summonerName", value="Gives the game information of the summoner, remember no spaces!", inline=False)
    embed.add_field(name="!info summonerName", value="Gives the ranked information of the summoner, remember no spaces!", inline=False)
    embed.add_field(name="!help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)


































