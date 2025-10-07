from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel
import httpx
import asyncio

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud, schemas

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
    except httpx.RequestError as exc:
        print("Twitch Authentication Failure:")
        print(exc)

async def fetch(streamers: list[str]):
    global twitch_token
    payload = []
    for streamer in streamers:
        payload.append(['user_login', streamer])
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
    except httpx.RequestError as exc:
        print(f"Twitch helix stream request error:")
        print(repr(exc))

async def main(bot: commands.Bot):
    streamers_live = set()
    channel = bot.get_channel(secret.BOT_SPAM_CHANNEL_ID)
    consecutive_errors = 0
    
    while True:
        try:
            db = SessionLocal()
            db_streamers = crud.get_twitchstreams(db)
            db.close()
            
            if not db_streamers: 
                await asyncio.sleep(5)
                continue

            streamers = [stream.user_login for stream in db_streamers]
            response = await fetch(streamers)

            if not response:
                print("Twitch: no response retrying in 5s...")
                consecutive_errors += 1
                if consecutive_errors > 3:
                    streamers_live.clear()
                await asyncio.sleep(5)
                continue

            if response[0] != 200:
                print("Twitch: Retrying authentication in 60s...")
                consecutive_errors += 1
                if consecutive_errors > 3:
                    streamers_live.clear()
                await asyncio.sleep(60)
                global twitch_token
                twitch_token = ''
                continue

            consecutive_errors = 0
            response_json = response[1]
            
            current_live = {stream['user_login'] for stream in response_json['data']}
            
            for streamer in current_live - streamers_live:
                await channel.send(
                    content=f"https://www.twitch.tv/{streamer}", 
                    allowed_mentions=discord.AllowedMentions(roles=True)
                )
                print(f"{streamer} live")
            
            for streamer in streamers_live - current_live:
                print(f"{streamer}: Going offline.")
            
            streamers_live = current_live
            
        except Exception as e:
            print(f"Error in Twitch monitoring loop: {str(e)}")
            consecutive_errors += 1
            if consecutive_errors > 3:
                streamers_live.clear()
            await asyncio.sleep(5)
            continue
        
        await asyncio.sleep(5)



class Twitch(commands.Cog):
    def __init__(self, bot):
        print("starting twitch")
        self.bot: commands.Bot = bot
        self.router = APIRouter()

        @self.router.get('/api/twitchstreams', response_model=list[schemas.TwitchStream])
        async def get_streams(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            has_admin_role = not (not secret.general_id in db_user.roles and not secret.warlord_id in db_user.roles)
            if not db_user.member or (secret.member_id in db_user.roles and not secret.veteran_id in db_user.roles and not has_admin_role):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not authorized")
            
            return crud.get_twitchstreams(db)
        
        @self.router.post('/api/twitchstreams/add')
        async def add_stream(stream: str, *, request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            
            guild = self.bot.get_guild(secret.GUILD_ID)
            member = guild.get_member(int(db_user.id))
            crud.update_user(db, member.id, schemas.UserCreate(**utils.create_user_from_member(member)))
            has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
            if not member or (not member.get_role(secret.veteran_id) and not has_admin_role):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not authorized")
            
            if not stream:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no stream provided")
            if not crud.get_twitchstream(db, stream):
                return crud.create_twitchstream(db, schemas.TwitchStream(user_login=stream, added_by=str(db_user.id)))
            else:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="entry already exists")
            

        @self.router.delete('/api/twitchstreams/remove')
        async def add_stream(stream: str, *, request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            
            guild = self.bot.get_guild(secret.GUILD_ID)
            member = guild.get_member(int(db_user.id))
            crud.update_user(db, member.id, schemas.UserCreate(**utils.create_user_from_member(member)))
            has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
            if not member or (not member.get_role(secret.veteran_id) and not has_admin_role):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not authorized")
            
            if not stream:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no stream provided")
            
            db_stream = crud.get_twitchstream(db, stream)
            if not db_stream:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="stream not found")
            
            return crud.del_twitchstream(db, stream)
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        await main(self.bot)
    
async def setup(bot):
	await bot.add_cog(Twitch(bot))