from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.responses import FileResponse

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud

from utils import logger, utils
from datetime import datetime

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
        self.router = APIRouter()   

        @self.router.get('/api/logs', response_model=list[str])
        async def logs(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True:
                return FileResponse(logger.path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
        
        @self.router.get('/api/logs/recent', response_model=list[str])
        async def logs(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True:
                return logger.last_25
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        log = ''
        if before.channel == None:
            self.connected[member.id] = datetime.now()
            log = member.name + ' connected to ' + after.channel.name
            print(logger.new(log))
        else:
            if after.channel != before.channel:
                if member.id in self.connected:
                    connected_time = datetime.now() - self.connected[member.id]
                    connected_seconds = connected_time.total_seconds()
                    connected_minutes = round(connected_seconds / 60, 1)
                    del self.connected[member.id]
                else:
                    connected_minutes = 0

                db = SessionLocal()
                db_user = crud.get_user(db=db, user_id=member.id)
                if db_user:
                    crud.update_user_connection_time(db=db, user_id=member.id, time=connected_minutes)
                else:
                    new_user = utils.create_user_from_member(member)
                    new_user['connection_time'] = connected_minutes
                    crud.create_user(db=db, user=new_user)
                db.close()

                log = member.name + ' disconnected from ' + before.channel.name + f" ({connected_minutes}mins)"
                print(logger.new(log))
                if after.channel: 
                    self.connected[member.id] = datetime.now()
                    log = member.name + ' connected to ' + after.channel.name
                    print(logger.new(log))

    @commands.hybrid_command(name='voicelogs', with_app_command=True)
    async def voicelogs(self, ctx):
        """Show last 25 voice events"""
        logs = "## Last 25 Events\n```diff\n"
        for log in logger.last_25:
            if 'disconnected' in log:
                log = '-' + log
            if 'connected' in log and 'disconnected' not in log:
                log = '+' + log
            logs = logs + log + '\n'
        logs = logs + "```"
        await ctx.send(logs)


async def setup(bot):
	await bot.add_cog(DiscordLogs(bot))