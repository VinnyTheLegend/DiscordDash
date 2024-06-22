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

class RoleSelection(commands.Cog):
    def __init__(self, bot):
        print("starting roleselection")
        self.bot: commands.Bot = bot
        self.router = APIRouter()

        @self.router.get('/api/roles/add')
        async def role(request: Request, db: Session = Depends(get_db)):
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

    @commands.hybrid_command(name='role', with_app_command=True)
    @discord.app_commands.describe(operation="Add or remove roles?", role="Which role?")
    @discord.app_commands.choices(operation=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="remove", value="remove")
    ])
    @discord.app_commands.choices(role=[
        discord.app_commands.Choice(name="Twitch Notifications", value="1222684351054221312"),
        discord.app_commands.Choice(name="Drops", value="850013094758842400")
    ])
    async def role(self, ctx: commands.Context, *, operation: str, role: str):
        """Add/Remove optional roles."""
        guild = self.bot.get_guild(secret.GUILD_ID)
        role = guild.get_role(int(role))
        if operation == "add":
           await ctx.author.add_roles(role)
           await ctx.reply(f"Added {role}", ephemeral=True)
        else:
            await ctx.author.remove_roles(role)
            await ctx.reply(f"Removed {role}", ephemeral=True)

        

    
async def setup(bot):
	await bot.add_cog(RoleSelection(bot))