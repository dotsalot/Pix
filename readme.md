# Pix
A helpful discord bot using the Riot API

## Requirements
The bot is written in Python 3.6.7
It uses [discord.py](https://discordpy.readthedocs.io/en/latest/index.html#) to handle bot commands 

## Features
The bot has 6 commands:
-help
-hello
-info
-game
-tft
-random

## Usage
All commands are prefaced with **!**

### help
The !help command gives back all the commands the bot can perform, along with the required or optional arguments.

### hello
The !hello command simply returns a greeting.

### info
!info summonerName gives back the ranked information of the summoner. The summoner name argument is required and cannot contain spaces. 

### game
!game summonerName gives back the champions being played and solo queue ranking for every summoner in the current live game, organized by side. Only works for SR, ARAM, TT modes,(and some event modes, but at the time of writing this bot, no event modes were out, uncertain behavior for events).

### tft
!tft [summonerNames] gives back the TFT ranking of the listed summoners. The summoners are separated by a single space, but their names may not contain spaces.

### random
!random role (*optional* summonerName) gives back a random champion to play for the given role. Including a summonerName will give back a champion that the summoner has not earned a chest for yet.

## Notes
This bot is deployed using Heroku. The Riot API key and Discord bot token are stored in Heroku config vars. For deploying locally, I stored the key/token in a secret file.

The leagueDict.py file needs to be updated periodically. The list of champions in each of the roles can change each patch as new metas evolve. Additionally, any new champions added to the game will need to be manually added. Same goes for new game modes.

The motivation for this bot was the current lack of APIs for the new Teamfight Tactics game mode. The !tft command is an attempt at a temporary solution. Many people use 3rd party sites to view game information that includes the ranks of their teammates and opponents. I would like to do the same for TFT, but there are currently no available APIs. This command allows you to enter any number of summonerNames and view their TFT rank without having to individually search them up.

######  Last updated on 8/12/19


