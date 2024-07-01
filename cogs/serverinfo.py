from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel

from datetime import datetime

import discord
from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud, schemas

from utils import utils
import secret

class RoleResponse(BaseModel):
    id: str
    name: str

class MemberResponse(BaseModel):
    id: str
    username: str
    global_name: str
    nickname: str
    avatar: str
    roles: list[RoleResponse]

class GuildResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    member_count: int
    role_count: int
    voice_channel_count: int
    text_channel_count: int
    emoji_count: int
    verification_level: str
    boosts: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        print("starting serverinfo")
        self.bot = bot
        self.router = APIRouter()   

        @self.router.get('/api/guild/members', response_model=list[schemas.User])
        async def members(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")

            guild: discord.Guild = self.bot.get_guild(secret.GUILD_ID)
            members = []
            for member in guild.members:
                db_member = crud.get_user(db, member.id)
                new_member = schemas.UserCreate(**utils.create_user_from_member(member))
                if db_member:
                    new_member = crud.update_user(db, member.id, new_member)
                else:
                    new_member = crud.create_user(db, new_member)
                members.append(new_member)
            return members
        
        @self.router.get('/api/guild', response_model=GuildResponse)
        async def guild(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")

            guild: discord.Guild = self.bot.get_guild(secret.GUILD_ID)

            guild_response = {
                'id': str(guild.id),
                'name': guild.name,
                'created_at': guild.created_at,
                "member_count": guild.member_count,
                "role_count": len(guild.roles),
                "voice_channel_count": len(guild.voice_channels),
                "text_channel_count": len(guild.text_channels),
                "emoji_count": len(guild.emojis),
                "verification_level": str(guild.verification_level),
                "boosts": guild.premium_subscription_count
            }


            return GuildResponse(**guild_response)

    @commands.hybrid_command(name='serverinfo', with_app_command=True)
    async def serverinfo(self, ctx):
        """Show server info"""
        guild: discord.Guild = self.bot.get_guild(secret.GUILD_ID)

        roles = str(len(guild.roles))
        emojis = str(len(guild.emojis))
        voice_channels = str(len(guild.voice_channels))
        text_channels = str(len(guild.text_channels))

        embeded = discord.Embed(title=guild.name, description='Server Info', color=0xEE8700)
        embeded.set_thumbnail(url=guild.icon.url)
        embeded.add_field(name="Created on:", value=guild.created_at.strftime('%d %B %Y at %H:%M UTC+3'), inline=False)
        embeded.add_field(name="Server ID:", value=guild.id, inline=False)
        embeded.add_field(name="Users on server:", value=guild.member_count, inline=True)
        embeded.add_field(name="Server owner:", value=guild.owner, inline=True)

        embeded.add_field(name="Verification Level:", value=guild.verification_level, inline=True)

        embeded.add_field(name="Roles:", value=roles, inline=True)
        embeded.add_field(name="Emojis:", value=emojis, inline=True)
        embeded.add_field(name="Voice Channels:", value=voice_channels, inline=True)
        embeded.add_field(name="Text Channels:", value=text_channels, inline=True)

        await ctx.reply(embed=embeded) 
    
async def setup(bot):
	await bot.add_cog(ServerInfo(bot))