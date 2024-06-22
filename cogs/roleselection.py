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

        self.optional_roles = [1222684351054221312, 850013094758842400]

        @self.router.get('/discord/user/roles')
        async def role(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            user_data, new_token = await utils.FetchDiscordProfile(state, token)
            if not user_data.member or (591687038902992928 not in user_data.roles and not user_data.admin):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            
            operation = request.query_params['operation']
            role = request.query_params['role']
            if int(role) not in self.optional_roles:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid role")
            guild = self.bot.get_guild(secret.GUILD_ID)
            role = guild.get_role(int(role))
            member = guild.get_member(int(user_data.id))
            if operation == "add":
                await member.add_roles(role)
                new_user = crud.user_add_role(db, user_data.id, role.id)
                return new_user
            elif operation == "remove":
                await member.remove_roles(role)
                new_user = crud.user_remove_role(db, user_data.id, role.id)
                return new_user
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad operation")


            


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
        db = SessionLocal()
        db_user = crud.get_user(db=db, user_id=ctx.author.id)
        guild = self.bot.get_guild(secret.GUILD_ID)
        role: discord.Role = guild.get_role(int(role))
        if operation == "add":
            await ctx.author.add_roles(role)

            if db_user:
                crud.user_add_role(db=db, user_id=ctx.author.id, role_id=role.id)
            else:
                new_user = utils.create_user_from_member(ctx.author)
                crud.create_user(db=db, user=new_user)

            await ctx.reply(f"Added {role}", ephemeral=True)
        else:
            await ctx.author.remove_roles(role)
            
            if db_user:
                crud.user_remove_role(db=db, user_id=ctx.author.id, role_id=role.id)
            else:
                new_user = utils.create_user_from_member(ctx.author)
                crud.create_user(db=db, user=new_user)

            await ctx.reply(f"Removed {role}", ephemeral=True)

        db.close()
        

    
async def setup(bot):
	await bot.add_cog(RoleSelection(bot))