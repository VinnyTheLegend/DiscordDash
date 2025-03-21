import discord
from discord.ext import commands

import secret

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64


class GeminiImage(commands.Cog):

    def __init__(self, bot):
        print("starting gemini_image")
        self.bot: commands.Bot = bot
        self.gemini_client = genai.Client(api_key=secret.google_api_key)


        
    @commands.hybrid_command(name='genimage', with_app_command=True)
    @discord.app_commands.describe(prompt='Image generation prompt.')
    async def genimage(self, ctx: commands.Context, *, prompt):
        """asd"""
        print(prompt)
        contents = prompt
        await ctx.defer()
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=contents,
                config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
                )
            )
        except:
            await ctx.reply("Request failed. Probably too many requests.")
            return
        for part in response.candidates[0].content.parts:
            if part.text is not None and part.inline_data is None:
                for i in range(0, len(part.text), 2000):
                    await ctx.reply(part.text[i:i + 2000]) 
                return
            elif part.inline_data is not None:
                image_data = base64.b64decode(part.inline_data.data)
                image = BytesIO(image_data)
                image.seek(0)
                file = discord.File(fp = image, filename = "image.png")
                await ctx.reply(file = file)


async def setup(bot):
    await bot.add_cog(GeminiImage(bot))