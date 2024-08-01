from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel

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


class LeftOrRight(commands.Cog):
    def __init__(self, bot):
        print("starting leftorright")
        self.bot: commands.bot = bot
        self.router = APIRouter()

        @self.router.get('/api/leftorright')
        async def get_lor(skip:int = 0, limit:int = 100, *, request: Request, db: Session = Depends(get_db)):
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
            
            return crud.get_leftorrights(db, skip, limit)

        @self.router.post('/api/leftorright/add')
        async def add_lor(name: str, img_url: str, *, request: Request, db: Session = Depends(get_db)):
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
            
            if not name or not img_url:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing img details")
            db_lor = crud.get_leftorright(db, name)
            if not db_lor:
                return crud.create_leftorright(db, schemas.LeftOrRight(name=name, img_url=img_url, wins=0))
            else:
                db_lor.img_url = img_url
                db.commit()
                db.refresh(db_lor)
                return db_lor
            
        @self.router.delete('/api/leftorright/remove')
        async def del_lor(name: str, *, request: Request, db: Session = Depends(get_db)):
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
            
            if not name:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing img details")
            db_lor = crud.get_leftorright(db, name)
            if not db_lor:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="img doesnt exist")
            else:
                return crud.del_leftorright(db, name)


    @commands.hybrid_command(name='embedtest', with_app_command=True)
    async def embedtest(self, ctx: commands.Context):
        """test sidebyside embed"""
        embed_1 = discord.Embed(description="description")
        embed_2 = discord.Embed()
        for embed in [embed_1, embed_2]:
            embed.url = secret.FRONT_URI
            embed.set_image(url="https://pbs.twimg.com/media/GNuSP3UbUAAcS-N?format=jpg&name=large")
        reply = await ctx.channel.send(embeds=[embed_1, embed_2])
        await reply.add_reaction("⬅️")
        await reply.add_reaction("➡️")

async def setup(bot):
	await bot.add_cog(LeftOrRight(bot))