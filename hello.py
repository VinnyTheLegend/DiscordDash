import discord
from discord.ext import commands
from utils import logger

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
            log = member.name + ' connected to ' + after.channel.name
        else:
            if after.channel != before.channel:
                log = member.name + ' disconnected from ' + before.channel.name
                print(logger.new(log))
                if after.channel: 
                    log = member.name + ' connected to ' + after.channel.name
                    print(logger.new(log))

    @commands.hybrid_command(name='voicelogs', with_app_command=True)
    async def voicelogs(self, ctx):
        """Show last 10 voice events"""
        logs = "## Last 10 Events\n```diff\n"
        for log in logger.last_10:
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