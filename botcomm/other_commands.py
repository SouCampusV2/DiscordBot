import discord
import json
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from botcomm.ticket_system import MyView

# Подгружаем айдишки всех нужных категорий, чатов и тд
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

RULES_CHANNEL = config["rules_channel_id"] # Канал в котором мы юзаем команду рулс
GUILD_ID = config["guild_id"] # Айдишка сервера  

class Other_Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Бот подгрузил другие командочки | {self.bot.user.name} ✅')

    # Слэш команда тикет, один раз заюзать и всё
    @commands.slash_command(name = "rules")
    @has_permissions(administrator = True)
    async def ticket(self, ctx):
        # Создать может только СЕО
        for role in ctx.user.roles:
            if role.name == "CEO":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
                
        if ticket_continue is True:         
            self.channel = self.bot.get_channel(RULES_CHANNEL)
            embed = discord.Embed(title = "Rules and terms<:2759floweremote:1233454904291627101>", 
                                color = 0xffc0cb, 
                                description = "Rules text example" * 100, # Добавить правила с отдельно написаного файла
                                )
            embed.set_image(url = "https://optim.tildacdn.pub/tild6430-3230-4664-b464-623339343434/-/format/webp/TrialSenior2.png")
            await self.channel.send(embed = embed) 
            await ctx.respond("Thank you for using us, rules was send!", ephemeral=True)
        else:
            self.embed = discord.Embed(title = f"You cannot create rules message, you don't have permission.", color = 0xffc0cb)
            await ctx.respond(embed = self.embed)  
