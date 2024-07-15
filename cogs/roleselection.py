from fastapi import APIRouter, HTTPException, Request, status, Depends

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

ROLE_CHOICES = []



class RoleSelection(commands.Cog):
    def __init__(self, bot):
        print("starting roleselection")
        self.bot: commands.Bot = bot
        self.router = APIRouter()

        @self.router.post('/discord/guild/roles/optional/add')
        async def optional_add(role_add_id: str, *, request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            
            guild = self.bot.get_guild(secret.GUILD_ID)
            member = guild.get_member(int(db_user.id))
            has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
            if not has_admin_role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not authorized")

            if not role_add_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no role specified")
            self.update_optional_roles()
            if role_add_id in self.optional_role_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="role already optional")

            role = guild.get_role(int(role_add_id))
            if not role:
                crud.del_role(db, role_add_id)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role doesnt exist")
            db_role = crud.get_role(db, str(role.id))
            if db_role:
                new_role = schemas.Role(id=str(role.id), name=role.name, optional=True, added_by=str(member.id))
                return crud.update_role(db, db_role.id, new_role)
                
        @self.router.post('/discord/guild/roles/optional/remove')
        async def optional_remove(role_remove_id: str, *, request: Request, db: Session = Depends(get_db)):
            state, token = utils.getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")
            if not db_user.member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            
            guild = self.bot.get_guild(secret.GUILD_ID)
            member = guild.get_member(int(db_user.id))
            has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
            if not has_admin_role:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not authorized")

            if not role_remove_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="no role specified")         
            self.update_optional_roles()
            if role_remove_id not in self.optional_role_ids:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="role not optional")

            role = guild.get_role(int(role_remove_id))
            if not role:
                crud.del_role(db, role_remove_id)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role doesnt exist")
            db_role = crud.get_role(db, str(role.id))
            if db_role:
                new_role = schemas.Role(id=str(role.id), name=role.name, optional=False, added_by=None)
                return crud.update_role(db, db_role.id, new_role)


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
            
            guild = self.bot.get_guild(secret.GUILD_ID)
            member = guild.get_member(int(db_user.id))
            crud.update_user(db, member.id, schemas.UserCreate(**utils.create_user_from_member(member)))
            has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
            if not member or (not member.get_role(secret.member_id) and not member.get_role(secret.veteran_id) and not has_admin_role):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
            print('authorized')
            
            operation = request.query_params['operation']
            role = request.query_params['role_id']
            print(role, operation)
            self.update_optional_roles()
            if role not in self.optional_role_ids:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role not optional")
            role = guild.get_role(int(role))
            if operation == "add":
                if role in member.roles:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid role")
                await member.add_roles(role)
                new_user = crud.user_add_role(db, db_user.id, str(role.id))
                return new_user
            elif operation == "remove":
                await member.remove_roles(role)
                new_user = crud.user_remove_role(db, db_user.id, str(role.id))
                return new_user
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bad operation")

    def update_optional_roles(self):
        db = SessionLocal()
        db_roles = crud.get_roles(db)
        db.close()
        guild = self.bot.get_guild(secret.GUILD_ID)
        self.db_optional_roles = []
        self.optional_roles = []
        self.optional_role_ids = []
        ROLE_CHOICES = []
        for db_role in db_roles:
            if db_role.optional:
                self.db_optional_roles.append(db_role)
                role = guild.get_role(int(db_role.id))
                self.optional_role_ids.append(db_role.id)
                self.optional_roles.append(role)
                print(role.id)
                ROLE_CHOICES.append(discord.app_commands.Choice(name=str(role.name), value=str(role.id)))

        self.role_ids: list[str] = []
        for role in guild.roles:
            self.role_ids.append(str(role.id))
        for role in db_roles:
            if role.id not in self.role_ids:
                crud.del_role(db, role.id)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update_optional_roles()

    @commands.hybrid_command(name='role', with_app_command=True)
    @discord.app_commands.describe(operation="Add or remove roles?", role="Which role?")
    @discord.app_commands.choices(operation=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="remove", value="remove")
    ])
    @discord.app_commands.choices(role=ROLE_CHOICES)
    async def role(self, ctx: commands.Context, *, operation: str, role: str):
        """Add/Remove optional roles."""
        is_member = False
        for author_role in ctx.author.roles:
            if author_role.id in [secret.member_id, secret.veteran_id, secret.general_id, secret.warlord_id]:
                is_member = True
                break
        if not is_member:
                await ctx.reply("Unauthorized.", ephemeral=False)
                return
        if role not in self.optional_role_ids:
            await ctx.reply("That role is not optional")
            return

        guild = self.bot.get_guild(secret.GUILD_ID)
        db = SessionLocal()
        db_user = crud.get_user(db=db, user_id=str(ctx.author.id))
        role: discord.Role = guild.get_role(int(role))
        if operation == "add":
            await ctx.author.add_roles(role)
            if role not in ctx.author.roles:
                if db_user:
                    crud.user_add_role(db=db, user_id=str(ctx.author.id), role_id=role.id)
                else:
                    new_user = utils.create_user_from_member(ctx.author)
                    new_user['roles'].append(role.id)
                    crud.create_user(db=db, user=new_user)
                await ctx.reply(f"Added {role}", ephemeral=True)
            else:
                await ctx.reply("User already has selected role.", ephemeral=True)
        else:
            await ctx.author.remove_roles(role)
            if role in ctx.author.roles:
                if db_user:
                    crud.user_remove_role(db=db, user_id=str(ctx.author.id), role_id=role.id)
                else:
                    new_user = utils.create_user_from_member(ctx.author)
                    new_user['roles'].remove(role.id)
                    crud.create_user(db=db, user=new_user)
                await ctx.reply(f"Removed {role}", ephemeral=True)
            else:
                await ctx.reply("User does not have selected role.", ephemeral=True)

            db.close()
        

    
async def setup(bot):
	await bot.add_cog(RoleSelection(bot))