import discord
import json
from discord import *
from discord.ext import commands, tasks
from botcomm.ticket_system import Ticket_System
from botcomm.ticket_commands import Ticket_Command
from botcomm.other_commands import Other_Command

# В этом конфиге находятся все данные которые касаются того где и как работает мой бот.
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  # Токен бота
GUILD_ID = config["guild_id"] # Айдишка сервера 
CATEGORY_ID1 = config["category_id_1"] # Категория 1 в которой бот будет работать
CATEGORY_ID2 = config["category_id_2"] # Категория 2 в которой бот будет работать
ROLE_ID = config["member_id"]

# Создаем так сказать клиент бота
bot = commands.Bot(intents = discord.Intents.all())

@bot.event
async def on_member_join(member):
    # Получаем объект роли по ID
    role = member.guild.get_role(ROLE_ID)
    if role is not None:
        # Выдаем роль участнику при входе
        await member.add_roles(role)

@tasks.loop(seconds=15) # Обновление статуса бота каждые 15 минут
async def update_status():
    guild = bot.get_guild(GUILD_ID)
    if guild:
        member_count = guild.member_count
        activity = discord.Activity(name = f"{member_count} members on the server!", type = discord.ActivityType.watching)
        await bot.change_presence(status = discord.Status.idle, activity = activity)

# Если все супер пупер, выводим что бот залогинился и работает успешно.
@bot.event
async def on_ready():
    print(f'Бот зашел в фуфаечку | {bot.user.name}✅')
    await update_status()
    update_status.start() # Цикл который постоянно обновляет всё

bot.add_cog(Ticket_System(bot))
bot.add_cog(Ticket_Command(bot))
bot.add_cog(Other_Command(bot))
bot.run(BOT_TOKEN)

