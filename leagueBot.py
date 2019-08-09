# Work with Python 3.6
import discord
from discord.ext import commands
import requests
from secrets import key, token
from leagueDict import queueMode, ranks, queueId, champs

#api calls
def summonerInfoAPI(name): #used to get encrypted summoner id
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    return requests.get(url = summonerInfoURL).json()

def detailedInfoAPI(encryptedSummonerId): #used to get ranked info  for summoner
    detailedInfoURL  =  f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={key}'
    return requests.get(url  =  detailedInfoURL).json()

def gameInfoAPI(encryptedSummonerId): #used to get match info
    gameInfoURL =  f'https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}?api_key={key}'
    return requests.get(url = gameInfoURL).json()

#functions
def playerInfo(player):
    name  = player['name']
    champ = player['champion']
    soloRank = player['rank']
    return f'\t\t**{champ}** {name}\n\t\t\t{soloRank}\n'

def divisionInfo(queue, tier):
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
        tier = ranks[queue['tier']]
        division = divisionInfo(queue, tier)
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
                tier = ranks[queue['tier']]
                division = divisionInfo(queue, tier)
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
async def tft(ctx, *args):
    embed  = discord.Embed(title  =  'TFT', description  = 'Ranked stats for:')
    for arg in  args:
        summonerInfoRequest = summonerInfoAPI(arg)
        if 'status' in summonerInfoRequest:
            embed.add_field(name = arg, value = 'Summoner not found')
        else:
            encryptedSummonerId = summonerInfoRequest['id']
            summonerName = summonerInfoRequest['name']
            detailedInfoRequest = detailedInfoAPI(encryptedSummonerId)
            ranked = False
            for queue in detailedInfoRequest:
                if queue['queueType'] == 'RANKED_TFT':
                    tier = ranks[queue['tier']]
                    division = divisionInfo(queue, tier)
                    ranked = True
                    break
            if ranked:
                rank = f'{tier} {division}'
            else:
                rank  = 'Unranked'
            embed.add_field(name = f'{summonerName}', value = f'{rank}')
    await ctx.send(embed = embed)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Pix!!", description="Pix is here to help! List of commands are:", color=0xeee657)

    embed.add_field(name="!hello", value="Says hello!", inline=False)
    embed.add_field(name="!game summonerName", value="Gives the game information of the summoner, remember no spaces!", inline=False)
    embed.add_field(name="!info summonerName", value="Gives the ranked information of the summoner, remember no spaces!", inline=False)
    embed.add_field(name="!help", value="Gives this message", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)


































