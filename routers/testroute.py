from fastapi import APIRouter, HTTPException, Request, status, Response, Body, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from .oauth import getCookies

from discord.ext import commands

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud, models, schemas

import secret

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
        self.testrouter = APIRouter()   
        self.echorouter = APIRouter()        

        async def get_router(self):
            return self.router

        @self.testrouter.get('/api/test')
        async def test(request: Request, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])

            if db_user.admin == True:
                await self.bot.get_channel(secret.BOT_SPAM_CHANNEL_ID).send("Someone clicked a button on a website to trigger this message. Gio is gay. That is all.")
                return {"message": "sent"}
            return {"message": "not admin"}
        
        @self.echorouter.post('/api/echo')
        async def echo(request: Request, message: Message, db: Session = Depends(get_db)):
            state, token = getCookies(request)
            db_user = crud.get_user_by_token(db=db, access_token=token['access_token'])

            if db_user.admin == True:
                await self.bot.get_channel(secret.BOT_SPAM_CHANNEL_ID).send(message.message)
                return {"message": "sent"}
            return {"message": "not admin"}
        
async def setup(bot):
	await bot.add_cog(TestRoute(bot))
