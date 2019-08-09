# Work with Python 3.6
import discord
from discord.ext import commands
import requests
from key import key, token
from leagueDict import queueMode, rank, queueId, champs

TOKEN = token

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
    else:
        encryptedSummonerId = summonerInfoRequest['id']
        summonerName = summonerInfoRequest['name']
        detailedInfoURL  =  f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={key}'
        detailedInfoRequest = requests.get(url  =  detailedInfoURL).json()
        rankedInfo = f'>>> __**{summonerName}** ranked info:__\n'
        for queue in detailedInfoRequest:
            queueType = queueMode[queue['queueType']]
            tier = rank[queue['tier']]
            if tier in ['Challenger', 'Grandmaster', 'Master']:
                division = ''
            else:
                division = queue['rank']
            lp =  queue['leaguePoints']
            wins  = queue['wins']
            losses = queue['losses']
            rankedInfo += f'**{queueType}:**\n\t{tier} {division} {lp} LP\n\t{int(wins/(losses+wins)*100)}% win ratio\n\t{wins} wins {losses} losses\n'
        await ctx.send(rankedInfo)

    

@bot.command() #get game info
async def game(ctx, name: str):
    summonerInfoURL = f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}?api_key={key}'
    summonerInfoRequest = requests.get(url = summonerInfoURL).json()
    if 'status' in summonerInfoRequest:
        error = summonerInfoRequest['status']['status_code']
        response = f'> Error! Status Code {error}'
        await ctx.send(response)
    else:
        encryptedSummonerId = summonerInfoRequest['id']
        summonerName = summonerInfoRequest['name']
        gameInfoURL =  f'https://na1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{encryptedSummonerId}?api_key={key}'
        gameInfoRequest = requests.get(url = gameInfoURL).json()
        if 'status' in gameInfoRequest:
            error = gameInfoRequest['status']['status_code']
            response = f'> Error! Status Code {error}\n {summonerName} probably not in a game'
            await ctx.send(response)

        else:
            gameTypeId = gameInfoRequest['gameQueueConfigId']
            gameType  = queueId[str(gameTypeId)]
            blue = []
            red = []
            for player in gameInfoRequest['participants']:
                info = dict()
                info['name'] = player['summonerName']
                encryptedSummonerId =  player['summonerId']
                info['champion'] = champs[str(player['championId'])]
                detailedInfoURL  =  f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{encryptedSummonerId}?api_key={key}'
                detailedInfoRequest = requests.get(url  =  detailedInfoURL).json()
                for queue in detailedInfoRequest:
                    if queue['queueType'] == 'RANKED_SOLO_5x5':
                        tier = rank[queue['tier']]
                        if tier in ['Challenger', 'Grandmaster', 'Master']:
                            division = '' 
                        else:
                            division = queue['rank']
                        info['rank'] = f'{tier} {division}'
                        break
                if 'rank' not in info:
                    info['rank'] = 'Unranked'

                if player['teamId'] == 100:
                    blue.append(info)
                else:
                    red.append(info)

            gameInfo = f'>>> __**{gameType}**__\n**Blue Side**\n'
            for player in blue:
                name  = player['name']
                champ = player['champion']
                soloRank = player['rank']
                gameInfo += f'{name} **{champ}**\n\t{soloRank}\n'
            gameInfo += '**Red Side**\n'
            for player in red:
                name  = player['name']
                champ = player['champion']
                soloRank = player['rank']
                gameInfo += f'{name} **{champ}**\n\t{soloRank}\n'
            await ctx.send(gameInfo)

bot.run(TOKEN)