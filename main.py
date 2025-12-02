import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn

from routers import oauth

import discord
from discord.ext import commands

from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import logging

import secret

from slowapi import _rate_limit_exceeded_handler
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
    await bot.load_extension("cogs.serverinfo")
    await bot.load_extension("cogs.roleselection")
    await bot.load_extension("cogs.twitch")
    await bot.load_extension("cogs.gemini")
    await bot.load_extension("cogs.leftorright")
    await bot.load_extension("cogs.gemini_image")



    asyncio.create_task(bot.start(secret.BOT_TOKEN))
    print('all cogs loaded')

    global test
    test = bot.get_cog("TestCog")
    app.include_router(test.router)

    app.include_router(bot.get_cog("DiscordLogs").router)
    app.include_router(bot.get_cog("ServerInfo").router)
    app.include_router(bot.get_cog("RoleSelection").router)
    app.include_router(bot.get_cog("Twitch").router)
    app.include_router(bot.get_cog("LeftOrRight").router)


    @app.get("/")
    async def root_redirect():
        return RedirectResponse(secret.guild_invite)

    print('routers loaded')
    print('done')
    yield
    # on shutdown

channel_botspam = secret.BOT_SPAM_CHANNEL_ID

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=secret.SESSION_MIDDLEWARE_KEY)
app.add_middleware(CORSMiddleware, 
    allow_origins=secret.ALLOW_ORIGINS, 
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS", "DELETE"],
    allow_headers=["Access-Control-Allow-Headers", "Content-Type", "Authorization", "Access-Control-Allow-Origin", "Set-Cookie"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(oauth.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=secret.BACK_PORT, reload=True, ssl_keyfile=secret.ssl_keyfile, ssl_certfile=secret.ssl_certfile)