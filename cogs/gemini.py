import discord
from discord.ext import commands

from io import BytesIO
from PIL import Image

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

import secret

genai.configure(api_key=secret.google_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

safety_settings = {
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

chat = model.start_chat(history=[
    {
        "role": "user",
        "parts": [{ "text": "System prompt: You are a Discord Chat bot within the Seduction Discord server. You will mimic the speech of a mature gamer that is also sarcastic and funny. You will assert that Rocket League and Counter Strike are bad games when asked. You will identify yourself as a female Discord chat bot made by Vinny."}],
    },
    {
        "role": "model",
        "parts": [{ "text": "Understood."}],
    },])

class Gemini(commands.Cog):
    def __init__(self, bot):
        print("starting gemini")
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for mention in message.mentions:
            if mention.id == self.bot.user.id:
                image = None
                if message.attachments:
                    if message.attachments[0].filename.endswith('.mp4'):
                        image = {
                            'mime_type': 'video/mp4',
                            'data': await message.attachments[0].read()
                        }
                    else:
                        image_bytes = await message.attachments[0].read()
                        image = Image.open(BytesIO(image_bytes))
                    print('made it')
                    response = await chat.send_message_async([
                        f"from: {message.author.display_name}\n{message.content.replace('<@1040105644306472960>', '')}",
                        image
                        ], safety_settings=safety_settings)
                else:
                    response = await chat.send_message_async(f"from: {message.author.display_name}\n{message.content.replace('<@1040105644306472960>', '')}", safety_settings=safety_settings)
                await message.reply(response.text)
                return
         
    
async def setup(bot):
    await bot.add_cog(Gemini(bot))