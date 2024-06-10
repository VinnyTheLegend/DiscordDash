import discord
from discord.ext import commands

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
        print(member.name)
        print(before)
        print(after)
        log = ''
        if before.channel == None:
            log = member.name + ' connected to ' + after.channel.name
            await self.bot.get_channel(1040851566736986193).send(log)
        else:
            if after.channel != before.channel:
                log = member.name + ' disconnected from ' + before.channel.name
                await self.bot.get_channel(1040851566736986193).send(log)
                if after.channel: 
                    log = member.name + ' connected to ' + after.channel.name
                    await self.bot.get_channel(1040851566736986193).send(log)

    @commands.hybrid_command(name='sync', with_app_command=True)
    async def sync(self, ctx):
        member = ctx.author
        if member.name == 'vinnyprime':
            await self.bot.tree.sync()
            await ctx.send('synced')

    @commands.hybrid_command(name='hello', with_app_command=True)
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