import asyncio

from fastapi import FastAPI

from routers import oauth

import discord
from discord.ext import commands

from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import logging

import secret

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from utils.limiter import limiter

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
discord.utils.setup_logging(level=logging.INFO, root=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    print("starting discord bot")
    await bot.load_extension("cogs.testcog")
    await bot.load_extension("cogs.discordlogs")
    asyncio.create_task(bot.start(secret.BOT_TOKEN))

    global test
    test = bot.get_cog("TestCog")
    app.include_router(test.router)

    app.include_router(bot.get_cog("DiscordLogs").router)

    yield
    # on shutdown

channel_botspam = 1040851566736986193

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=secret.SESSION_MIDDLEWARE_KEY)
app.add_middleware(CORSMiddleware, 
    allow_origins=secret.ALLOW_ORIGINS, 
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
    allow_headers=["Access-Control-Allow-Headers", "Content-Type", "Authorization", "Access-Control-Allow-Origin", "Set-Cookie"],
)

app.state.limiter = Limiter.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(oauth.router)