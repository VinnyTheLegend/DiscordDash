
import httpx
import asyncio

import os
import random
import datetime

import discord
from discord.ext import commands

import secret
import httpx
from bs4 import BeautifulSoup
import asyncio

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none"
}

async def scrape(url):
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        response = await client.get(url)
        body = response.text
        soup = BeautifulSoup(body, 'html.parser')
        print("poe: ", response.status_code)
        entries = soup.find_all("tr", class_="entry")
        return entries

async def main(bot: commands.Bot):
    while True:
        entries = await scrape(secret.poe_league_url)
        characters = ""
        poe_classes = ""
        levels = ""

        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.blue())

        for i, entry in enumerate(entries):
            acc_name = entry.find("td", class_="account").text
            character = entry.find("td", class_="character").text
            poe_class = entry.find("td", class_="class").text
            level = entry.find("td", class_="level").text

            characters += character.strip() + "\n"
            poe_classes += poe_class.strip() + "\n"
            levels += level.strip() + "\n"

        
        embed.add_field(name="Character", value=characters, inline=True)
        embed.add_field(name="Class", value=poe_classes, inline=True)
        embed.add_field(name="Level", value=levels, inline=True)
        embed.timestamp = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=-4.0)))
        embed.set_footer(text=f"Last Updated ")
        

        channel = bot.get_channel(secret.poe_leaderboard_channel)
        message = None
        history = [message async for message in channel.history()]
        
        for old_message in history:
            if old_message.author.id == bot.user.id:
                message = old_message


        if not message:
            await channel.send(embed=embed)
        else:
            await message.edit(content="", embed=embed)

        await asyncio.sleep(random.randrange(45, 60)*60)

class Poe(commands.Cog):
    def __init__(self, bot):
        print("starting poe")
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await main(self.bot)
    
async def setup(bot):
	await bot.add_cog(Poe(bot))