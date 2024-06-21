from fastapi import APIRouter, HTTPException, Request, status, Depends

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

class TestCog(commands.Cog):
    def __init__(self, bot):
        print("starting testroute")
        self.bot = bot
        self.router = APIRouter()   

        @self.router.get('/api/roles/add')
        async def rolesadd(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            data, new_token = await utils.FetchDiscordProfile(state, token)
            if not data.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
                


    @commands.hybrid_command(name='ping', with_app_command=True)
    async def ping(self, ctx):
        """asd"""
        await ctx.reply("Pong")

    
async def setup(bot):
	await bot.add_cog(TestCog(bot))