from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel

from routers.oauth import getCookies

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud

import secret

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Message(BaseModel):
    message: str

class TestCog(commands.Cog):
    def __init__(self, bot):
        print("starting testroute")
        self.bot = bot
        self.router = APIRouter()   

        @self.router.get('/api/test')
        async def test(request: Request, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.admin == True:
                await self.bot.get_channel(secret.BOT_SPAM_CHANNEL_ID).send("Someone clicked a button on a website to trigger this message. Gio is gay. That is all.")
                return {"message": "sent"}
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not an admin")

        
        @self.router.post('/api/echo')
        async def echo(request: Request, message: Message, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")


            if db_user.admin == True:
                await self.bot.get_channel(secret.BOT_SPAM_CHANNEL_ID).send(message.message)
                return {"message": "sent"}
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not an admin")

        
        @self.router.get('/api/guild/members')
        async def test(request: Request, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")

            guild = self.bot.get_guild(591684990811635724)
            members = []
            for member in guild.members:

                roles = []
                for role in member.roles:
                    role_new = {
                        'id': role.id,
                        'name': role.name
                    }
                    roles.append(role_new)

                member_new = {
                     'global_name': member.global_name,
                     'roles': roles
                }
                members.append(member_new)
            return members

    @commands.hybrid_command(name='ping', with_app_command=True)
    async def ping(self, ctx):
        """asd"""
        await ctx.reply("Pong")

    @commands.hybrid_command(name='sync', with_app_command=True)
    async def sync(self, ctx):
        """Sync app commands (usually requires discord client restart)"""
        member: discord.Member = ctx.author
        if member.name == 'vinnyprime':
            sync = await self.bot.tree.sync()
            await ctx.reply(f"Synced {len(sync)} command(s)", ephemeral=True)
        else:
            await ctx.reply("Only Vinny is allowed to do that.", ephemeral=True)

    @commands.hybrid_command(name='hello', with_app_command=True)
    @discord.app_commands.describe(member='who to say hello to')
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        
        await ctx.reply("Ephemeral test", ephemeral=True)
        
        self._last_member = member

    async def test(self):
         await self.bot.get_channel(1040851566736986193).send("cog triggered")
    
async def setup(bot):
	await bot.add_cog(TestCog(bot))