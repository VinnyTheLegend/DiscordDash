from fastapi import APIRouter, HTTPException, Request, status, Response, Body, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .oauth import getCookies

from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud, models, schemas

import secret
from utils import logger

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Message(BaseModel):
    message: str

class TestRoute(commands.Cog):
    def __init__(self, bot):
        print("starting testroute")
        self.bot = bot
        self._last_member = None
        self.router = APIRouter()   

        async def get_router(self):
            return self.router

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
        
        @self.router.get('/api/logs')
        async def logs(request: Request, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True:
                return FileResponse(logger.path)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")
        
        @self.router.get('/api/logs/10')
        async def logs(request: Request, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            if not token or not state:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="state or token not provided")
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])
            if not db_user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user not found")

            if db_user.member == True:
                return logger.last_25
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not a member")


        
async def setup(bot):
	await bot.add_cog(TestRoute(bot))
