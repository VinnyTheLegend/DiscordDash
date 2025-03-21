from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel

from random import randint
import asyncio

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
        self.bot: commands.Bot = bot
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
                return crud.create_leftorright(db, schemas.LeftOrRight(name=name, img_url=img_url, added_by=str(member.id), wins=0))
            else:
                db_lor.img_url = img_url
                db_lor.added_by = str(member.id)
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

    @commands.hybrid_command(name='lorstart', with_app_command=True)
    @discord.app_commands.describe(round_time="Round length in seconds.")
    async def lorstart(self, ctx: commands.Context, *, round_time: int):
        """Start Left or Right game."""

        member = ctx.author
        has_admin_role = not (not member.get_role(secret.general_id) and not member.get_role(secret.warlord_id))
        if not member or (not member.get_role(secret.veteran_id) and not has_admin_role):
            await ctx.reply("Unauthorized.")
            return
        
        if isinstance(round_time, int) == False:
            await ctx.reply("Invalid round time.", ephemeral=True)
            return
        

        db = SessionLocal()
        images = crud.get_leftorrights(db)
        if len(images) == 100:
            new_images = crud.get_leftorrights(db, 100)
            images = images + new_images
            skip = 100
            while len(new_images) == 100:
                skip + 100
                new_images = crud.get_leftorrights(db, skip)
                images = images + new_images
        db.close()
        if not images or images == []:
            await ctx.reply("No images.")
            return
        
        await ctx.reply("Starting game.")

        while len(images) > 1:
            num1 = randint(0, len(images)-1)
            num2 = randint(0, len(images)-1)
            while num1 == num2:
                num2 = randint(0, len(images)-1)
            image_1 = images[num1]
            image_2 = images[num2]

            embed_1 = discord.Embed(description=f"{image_1.name} vs {image_2.name}")
            embed_1.url = secret.FRONT_URI
            embed_1.set_image(url=image_1.img_url)

            embed_2 = discord.Embed()
            embed_2.url = secret.FRONT_URI
            embed_2.set_image(url=image_2.img_url)

            reply = await ctx.channel.send(embeds=[embed_1, embed_2])
            await reply.add_reaction("⬅️")
            await reply.add_reaction("➡️")
            await asyncio.sleep(int(round_time))
            await ctx.channel.send("5 seconds remaining...")
            await asyncio.sleep(5)
            message = await ctx.channel.fetch_message(reply.id)
            left_count = 0
            right_count = 0
            for reaction in message.reactions:
                if reaction.emoji == "⬅️":
                    left_count = reaction.count
                if reaction.emoji == "➡️":
                    right_count = reaction.count
            if left_count > right_count:
                await ctx.channel.send(f"{image_1.name} wins the round.")
                del images[num2]
            else:
                await ctx.channel.send(f"{image_2.name} wins the round.")
                del images[num1]
        db = SessionLocal()
        new_lor = crud.leftorright_add_win(db, images[0].name)
        db.close()
        await ctx.channel.send(f"{new_lor.name} wins! ({new_lor.wins} total wins)")

async def setup(bot):
	await bot.add_cog(LeftOrRight(bot))