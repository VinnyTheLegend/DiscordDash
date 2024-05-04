from fastapi import APIRouter, HTTPException, Request, status, Response, Body
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

from discord.ext import commands

from routers.oauth import IsAdmin


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
        async def test(request: Request):
            if await IsAdmin(request) == True:
                await self.bot.get_channel(1040851566736986193).send("Someone clicked a button on a website to trigger this message. Gio is gay. That is all.")
                return {"message": "sent"}
            return {"message": "not admin"}
        
        @self.echorouter.post('/api/echo')
        async def echo(request: Request, message: Message):
            if await IsAdmin(request) == True:
                await self.bot.get_channel(1040851566736986193).send(message.message)
                return {"message": "sent"}
            return {"message": "not admin"}
        
async def setup(bot):
	await bot.add_cog(TestRoute(bot))
