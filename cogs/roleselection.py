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

ROLE_CHOICES = []

class RoleSelection(commands.Cog):
    def __init__(self, bot):
        print("starting roleselection")
        self.bot: commands.Bot = bot
        self.router = APIRouter()

        self.optional_role_ids = [1222684351054221312, 850013094758842400]
        self.optional_roles = []

        @self.router.get('/discord/user/roles')
        async def roleaddremove(request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            
            member = self.guild.get_member(int(db_user.id))
            member_role = 591687038902992928
            veteran_role = 591687458819932172
            general_role = 591686523142012948
            warlord_role = 591686220996935691
            has_admin_role = not (not member.get_role(general_role) and not member.get_role(warlord_role))
            if not member or (not member.get_role(member_role) and not member.get_role(veteran_role) and not has_admin_role):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            print('authorized')
            
            operation = request.query_params['operation']
            role = request.query_params['role_id']
            print(role, operation)
            if int(role) not in self.optional_role_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid role")
            role = self.guild.get_role(int(role))
            member = self.guild.get_member(int(db_user.id))
            if operation == "add":
                await member.add_roles(role)
                new_user = crud.user_add_role(db, db_user.id, str(role.id))
                return new_user
            elif operation == "remove":
                await member.remove_roles(role)
                new_user = crud.user_remove_role(db, db_user.id, str(role.id))
                return new_user
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad operation")


    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.bot.get_guild(secret.GUILD_ID)
        for role_id in self.optional_role_ids:
           role = self.guild.get_role(role_id)
           self.optional_roles.append(role)
           ROLE_CHOICES.append(discord.app_commands.Choice(name=str(role.name), value=str(role.id)))
    

    @commands.hybrid_command(name='role', with_app_command=True)
    @discord.app_commands.describe(operation="Add or remove roles?", role="Which role?")
    @discord.app_commands.choices(operation=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="remove", value="remove")
    ])
    @discord.app_commands.choices(role=ROLE_CHOICES)
    async def role(self, ctx: commands.Context, *, operation: str, role: str):
        """Add/Remove optional roles."""
        db = SessionLocal()
        db_user = crud.get_user(db=db, user_id=str(ctx.author.id))
        role: discord.Role = self.guild.get_role(int(role))
        if operation == "add":
            await ctx.author.add_roles(role)
            if db_user:
                crud.user_add_role(db=db, user_id=str(ctx.author.id), role_id=role.id)
            else:
                new_user = utils.create_user_from_member(ctx.author)
                new_user['roles'].append(role.id)
                crud.create_user(db=db, user=new_user)
            await ctx.reply(f"Added {role}", ephemeral=True)
        else:
            await ctx.author.remove_roles(role)
            if db_user:
                crud.user_remove_role(db=db, user_id=str(ctx.author.id), role_id=role.id)
            else:
                new_user = utils.create_user_from_member(ctx.author)
                new_user['roles'].remove(role.id)
                crud.create_user(db=db, user=new_user)
            await ctx.reply(f"Removed {role}", ephemeral=True)
        db.close()
        

    
async def setup(bot):
	await bot.add_cog(RoleSelection(bot))