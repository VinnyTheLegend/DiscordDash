from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import FileResponse

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud, schemas

from utils import logger, utils
from datetime import datetime, timedelta

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DiscordLogs(commands.Cog):
    def __init__(self, bot):
        print("starting discordlogs")
        self.bot = bot
        self.connected = {}
        self.muted = {}
        self.deafened = {}
        self.router = APIRouter()   

        @self.router.get('/api/logs', response_model=list[str])
        async def logs(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True: #type: ignore
                return FileResponse(logger.path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
        
        @self.router.get('/api/logs/recent', response_model=list[str])
        async def logsrecent(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True: #type: ignore
                return logger.last_25
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
    
    def unmute(self, member: discord.Member, after: discord.VoiceState):
        if member.id in self.muted: 
            muted_time: timedelta = datetime.now() - self.muted[member.id]
            muted_seconds = muted_time.total_seconds()
            muted_minutes = round(muted_seconds / 60, 1)
            if after.self_deaf == False:
                print(logger.new(member.name + " unmuted " + f'({muted_minutes}mins)'))

            db = SessionLocal()
            db_user = crud.get_user(db=db, user_id=str(member.id))
            new_user = utils.create_user_from_member(member)
            if db_user:
                new_user['muted_time'] = db_user.muted_time + muted_minutes
                crud.update_user(db=db, user_id=new_user['id'], user=schemas.UserCreate(**new_user))
            else:
                new_user['muted_time'] = muted_minutes
                crud.create_user(db=db, user=schemas.UserCreate(**new_user))
            db.close()

            del self.muted[member.id]

    def undeafen(self, member: discord.Member, after: discord.VoiceState):
        if member.id in self.deafened:
            deafened_time: timedelta = datetime.now() - self.deafened[member.id]
            deafened_seconds = deafened_time.total_seconds()
            deafened_minutes = round(deafened_seconds / 60, 1)
            print(logger.new(f'{member.name} undeafened ({deafened_minutes}mins)'))

            db = SessionLocal()
            db_user = crud.get_user(db=db, user_id=str(member.id))
            new_user = utils.create_user_from_member(member)
            if db_user:
                new_user['deafened_time'] = db_user.deafened_time + deafened_minutes
                crud.update_user(db=db, user_id=new_user['id'], user=schemas.UserCreate(**new_user))
            else:
                new_user['deafened_time'] = deafened_minutes
                crud.create_user(db=db, user=schemas.UserCreate(**new_user))
            db.close()

            del self.deafened[member.id]

        if after.channel and after.self_mute == True:
            print(logger.new(member.name + " muted"))
            self.muted[member.id] = datetime.now()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log = ''
        if before.channel == None:
            self.connected[member.id] = datetime.now()
            log = member.name + ' connected to ' + after.channel.name
            print(logger.new(log))
            if after.self_deaf == True:
                print(logger.new(member.name + " deafened"))
                self.deafened[member.id] = datetime.now()
            elif after.self_mute == True:
                self.muted[member.id] = datetime.now()
                print(logger.new(member.name + " muted"))
        else:
            if after.channel != before.channel:
                if member.id in self.connected:
                    connected_time: timedelta = datetime.now() - self.connected[member.id]
                    connected_seconds = connected_time.total_seconds()
                    connected_minutes = round(connected_seconds / 60, 1)
                    del self.connected[member.id]
                else:
                    connected_minutes = 0

                db = SessionLocal()
                db_user = crud.get_user(db=db, user_id=str(member.id))
                new_user = utils.create_user_from_member(member)
                if db_user:
                    new_user['connection_time'] = db_user.connection_time + connected_minutes
                    crud.update_user(db=db, user_id=new_user['id'], user=schemas.UserCreate(**new_user))
                else:
                    new_user['connection_time'] = connected_minutes
                    crud.create_user(db=db, user=schemas.UserCreate(**new_user))
                db.close()

                log = member.name + ' disconnected from ' + before.channel.name + f" ({connected_minutes}mins)"
                print(logger.new(log))
                if after.channel: 
                    self.connected[member.id] = datetime.now()
                    log = member.name + ' connected to ' + after.channel.name
                    print(logger.new(log))
                else:
                    if member.id in self.deafened:
                        self.undeafen(member, after)
                    if member.id in self.muted:
                        self.unmute(member, after)
        if after.channel:
            if before.self_deaf == False and after.self_deaf == True:
                print(logger.new(member.name + " deafened"))
                self.deafened[member.id] = datetime.now()
                if member.id in self.muted:
                    self.unmute(member, after)
            elif before.self_deaf == True and after.self_deaf == False:
                self.undeafen(member, after)
            elif before.self_mute == False and after.self_mute == True:
                self.muted[member.id] = datetime.now()
                print(logger.new(member.name + " muted"))
            elif before.self_mute == True and after.self_mute == False:
                self.unmute(member, after)



    @commands.hybrid_command(name='voicelogs', with_app_command=True)
    async def voicelogs(self, ctx):
        """Show last 25 voice events"""
        logs = "## Last 25 Events\n```diff\n"
        for log in logger.last_25:
            if 'disconnected' in log or ' muted' in log or ' deafened' in log:
                log = '-' + log
            elif 'connected' in log or 'unmuted' in log or 'undeafened' in log:
                log = '+' + log
            logs = logs + log + '\n'
        logs = logs + "```"
        await ctx.send(logs)


async def setup(bot):
	await bot.add_cog(DiscordLogs(bot))