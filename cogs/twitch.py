from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel
import httpx
import asyncio

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud

from utils import utils

import secret

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

twitch_token = ''

async def auth():
    global twitch_token
    client_data: httpx.QueryParams = {
        'client_id': secret.twitch_secret['client_id'],
        'client_secret': secret.twitch_secret['client_secret'],
        'grant_type': 'client_credentials'
    }
    try:
        async with httpx.AsyncClient() as client:
                response = await client.post("https://id.twitch.tv/oauth2/token", params=client_data)
                print("Twitch Auth Status: " + str(response.status_code))
                response_json = response.json()
                twitch_token = response_json['access_token']
    except Exception as e:
        print('auth failed')
        print(str(e))

async def fetch(name):
    global twitch_token
    payload = { 'user_login': name}
    if twitch_token == '':
        await auth()
    headers = {
        'Authorization': 'Bearer ' + twitch_token,
        'Client-Id': secret.twitch_secret['client_id']
    }
    try:
        async with httpx.AsyncClient() as client:
                response = await client.get("https://api.twitch.tv/helix/streams", params=payload, headers=headers)
                return (response.status_code, response.json())
    except Exception as e:
        print('webpage not found')
        print(str(e))

async def main(bot: commands.Bot):
    streamers = [
        'moonstreuxx',
        'fallenxov',
        'dwalllaxer',
        'vinnythelegend'
    ]
    streamers_live = []
    channel = bot.get_channel(secret.BOT_SPAM_CHANNEL_ID)
    while True:
        for name in streamers:
            response = await fetch(name)
            while not response:
                print("no response retrying in 60s...")
                await asyncio.sleep(60)
                response = await fetch(name)
            while response[0] != 200:
                print("Retrying authentication in 60s...")
                await asyncio.sleep(60)
                global twitch_token
                twitch_token = ''
                response = await fetch(name)
            response_json = response[1]
            if response_json['data'] == []:
                try:
                    streamers_live.remove(name)
                    print(name + ": Going offline.")
                except:
                    pass
            else:
                if name not in streamers_live:
                    streamers_live.append(name)
                    await channel.send(content=f"https://www.twitch.tv/{name}", allowed_mentions=discord.AllowedMentions(roles=True)) #<@&1222684351054221312>\n
                    print(name + " live")
            await asyncio.sleep(5)
        await asyncio.sleep(5)



class Twitch(commands.Cog):
    def __init__(self, bot):
        print("starting twitch")
        self.bot: commands.Bot = bot
        self.router = APIRouter()

    
    @commands.Cog.listener()
    async def on_ready(self):
        await main(self.bot)
    
async def setup(bot):
	await bot.add_cog(Twitch(bot))