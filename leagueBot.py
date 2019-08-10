import discord
from discord.ext import commands
import requests
from random import choice
from secrets import key, token
from leagueDict import queueMode, ranks, queueId, champsById, roles, champsByName

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

def summonerChampMasterAPI(encryptedSummonerId, champId):
   summonerChampMasterInfo = f'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}/by-champion/{champId}?api_key={key}'
   return requests.get(url = summonerChampMasterInfo).json()

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
        response = f'> Error! Summoner not found (or bad API key)'
        await ctx.send(response)
        return
    #summoner found
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    detailedInfoRequest = detailedInfoAPI(encryptedSummonerId)
    summonerRankedInfo = f'>>> __**{summonerName}** ranked info:__\n'
    response = summonerRankedInfo
    if len(detailedInfoRequest) == 0:
        response += 'Unranked in all queues!'
        await ctx.send(response)
        return
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
        response = f'> Error! Summoner not found (or bad API key)'
        await ctx.send(response)
        return
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    gameInfoRequest = gameInfoAPI(encryptedSummonerId)
    #summoner not  in game/in  tft  game/bad api key
    if 'status' in gameInfoRequest:
        errorMsg = f'>>> Error! {summonerName} probably not in a game ¯\\_(ツ)_/¯\n'
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
        if champId in  champsById:
            info['champion'] = champsById[champId]
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

@bot.command() #tft ranked info
async def tft(ctx, *args):
    embed  = discord.Embed(title  =  'TFT', description  = 'Ranked stats for:')
    for arg in  args:
        if arg[-1] == ',':
            name = arg[:-1]
        else:
            name  =  arg
        summonerInfoRequest = summonerInfoAPI(name)
        if 'status' in summonerInfoRequest:
            embed.add_field(name = name, value = 'Summoner not found')
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
async  def random(ctx, role, name = None):
    role = role.lower()
    if role not in ['top', 'mid', 'jungle', 'bot', 'support']:
        response = 'Unrecognized role. List of accepted roles:\ntop\njungle\nmid\nbot\nsupport'
        await  ctx.send(response)
        return
    champ = choice(roles[role])
    if  name == None: #only  want a random champ for a  role
        await ctx.send(f'You wanna play {role}? Try **{champ}** this game')
        return
    seen = set()
    summonerInfoRequest = summonerInfoAPI(name)
    #summoner  not  found/bad api key
    if 'status' in summonerInfoRequest:
        response = f'> Error! Summoner not found (or bad API key)'
        await ctx.send(response)
        return
    #summoner found
    encryptedSummonerId = summonerInfoRequest['id']
    summonerName = summonerInfoRequest['name']
    while len(seen) != len(roles[role]):
        if champ not in seen:
            seen.add(champ)
            champId = champsByName[champ]
            champInfo = summonerChampMasterAPI(encryptedSummonerId, champId)
            if not champInfo['chestGranted']:
                await ctx.send(f'You haven\'t gotten a chest for **{champ}** yet')
                return

        champ = choice(roles[role])

    await ctx.send(f'Wow! You have no chests available for {role}!')

@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Pix!!', description='Pix is here to help! List of commands are:', color = 0xeee657)

    embed.add_field(name = '!hello', value = 'Says hello!', inline = False)
    embed.add_field(name = '!game summonerName', value = 'Gives the game information of the summoner, remember no spaces!', inline = False)
    embed.add_field(name = '!info summonerName', value = 'Gives the ranked information of the summoner, remember no spaces!', inline = False)
    embed.add_field(name = '!tft [summonerName]s', value = 'Gives the ranked information of the summoners, remember no spaces in the names, separate individual summoners by a space!', inline = False)
    embed.add_field(name = 'random role [summonerName]', value = 'Gives a random champ suggestion by role [top, jungle, mid, bot, suppoer], optional summoner name argument to give a champ you haven\'t gotten a chest for yet', inline = False)
    embed.add_field(name = '!help', value='Gives this message', inline = False)

    await ctx.send(embed=embed)

bot.run(TOKEN)


































