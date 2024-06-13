import discord
from discord.ext import commands
from utils import logger, member_utils
from datetime import datetime

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database import crud

connected = {}

class Greetings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel is not None:
            await channel.send(f'Welcome {member.mention}.')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log = ''
        if before.channel == None:
            connected[member.id] = datetime.now()
            log = member.name + ' connected to ' + after.channel.name
            print(logger.new(log))
        else:
            if after.channel != before.channel:
                if member.id in connected:
                    connected_time = datetime.now() - connected[member.id]
                    connected_seconds = connected_time.total_seconds()
                    connected_minutes = round(connected_seconds / 60, 1)
                    del connected[member.id]
                else:
                    connected_minutes = 0

                db = SessionLocal()
                db_user = crud.get_user(db=db, user_id=member.id)
                if db_user:
                    crud.update_user_connection_time(db=db, user_id=member.id, time=connected_minutes)
                else:
                    new_user = member_utils.create_user_from_member(member)
                    new_user['connection_time'] = connected_minutes
                    crud.create_user(db=db, user=new_user)
                db.close()

                log = member.name + ' disconnected from ' + before.channel.name + f" ({connected_minutes}mins)"
                print(logger.new(log))
                if after.channel: 
                    connected[member.id] = datetime.now()
                    log = member.name + ' connected to ' + after.channel.name
                    print(logger.new(log))


    @commands.hybrid_command(name='voicelogs', with_app_command=True)
    async def voicelogs(self, ctx):
        """Show last 25 voice events"""
        logs = "## Last 25 Events\n```diff\n"
        for log in logger.last_25:
            if 'disconnected' in log:
                log = '-' + log
            if 'connected' in log and 'disconnected' not in log:
                log = '+' + log
            logs = logs + log + '\n'
        logs = logs + "```"
        await ctx.send(logs)


    @commands.hybrid_command(name='sync', with_app_command=True)
    async def sync(self, ctx):
        """Sync app commands (usually requires discord client restart)"""
        member: discord.Member = ctx.author
        if member.name == 'vinnyprime':
            sync = await self.bot.tree.sync()
            await ctx.reply(f"Synced {len(sync)} command(s)", ephemeral=True)
        else:
            await ctx.reply("Only Vinny is allowed to do that.", ephemeral=True)


    @commands.hybrid_command(name='hello', with_app_command=True)
    @discord.app_commands.describe(member='who to say hello to')
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        if self._last_member is None or self._last_member.id != member.id:
            await ctx.send(f'Hello {member.name}~')
        else:
            await ctx.send(f'Hello {member.name}... This feels familiar.')
        
        await ctx.reply("Ephemeral test", ephemeral=True)
        
        self._last_member = member

    async def test(self):
         await self.bot.get_channel(1040851566736986193).send("cog triggered")

async def setup(bot):
	await bot.add_cog(Greetings(bot))