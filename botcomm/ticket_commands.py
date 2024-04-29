import discord
import json
import chat_exporter
import io
import sqlite3
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from botcomm.ticket_system import MyView

# Подгружаем айдишки всех нужных категорий, чатов и тд
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

TICKET_CHANNEL = config["ticket_channel_id"] # Канал в котором менюшка
GUILD_ID = config["guild_id"] # Айдишка сервера  

LOG_CHANNEL = config["log_channel_id"] # Канал куда логи закидывать
TIMEZONE = config["timezone"] # Таймзона

# Создание и подключение к дбшке
conn = sqlite3.connect('user.db')
cur = conn.cursor()

# Создаст таблицу если нету
cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Бот подгрузил командочки | {self.bot.user.name} ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

    # Слэш команда тикет, один раз заюзать и всё
    @commands.slash_command(name = "ticket")
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
            self.channel = self.bot.get_channel(TICKET_CHANNEL)
            embed = discord.Embed(title = "SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                                color = 0xffc0cb, 
                                description = "If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.",
                                )
            embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
            await self.channel.send(embed = embed, view = MyView(self.bot))
            await ctx.respond("Ticket Menu was send!", ephemeral=True)
        else:
            self.embed = discord.Embed(title = f"You cannot create ticket menu, you don't have permission.", color = 0xffc0cb)
            await ctx.respond(embed = self.embed)            

    # Добавить челикса в тикет
    @commands.slash_command(name = "add", description = "Add a Member to the Ticket")
    async def add(self, ctx, member: Option(discord.Member, description = "Which Member you want to add to the Ticket", required = True)): # type: ignore
        for role in member.roles:
            if role.name == "CEO" or "Moderator":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
                
        if ticket_continue is True:           
            if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
                await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                                    embed_links=True, attach_files=True, read_message_history=True,
                                                    external_emojis=True)
                self.embed = discord.Embed(description=f'Added {member.mention} to this Ticket <#{ctx.channel.id}>! \n Use /remove to remove a User.', color = 0xffc0cb)
                await ctx.respond(embed = self.embed)
            else:
                self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color = discord.colour.Color.red())
                await ctx.respond(embed = self.embed)
        else:
            self.embed = discord.Embed(title = f"You cannot add, you don't have permission.", color = 0xffc0cb)
            await ctx.respond(embed = self.embed)

    # Очистка сообщений
    @commands.slash_command(name = "clear", description = "Clear messages.")
    async def clear_messages(self, ctx, member: Option(discord.Member, description = "Whose messages to clear.", required = True), amount: int): # type: ignore  
        for role in member.roles:
            if role.name == "CEO" or "Moderator":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
                
        if ticket_continue is True:
            await ctx.channel.set_permissions(member,    send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True)
            if isinstance(amount, int):
                await ctx.channel.purge(limit = amount)
                await ctx.respond(f"Messages was cleared {member.mention}, thank you for using us!", ephemeral=True)    
        else:
            await ctx.respond(f"You cannot clear {member.mention}, you don't have permission!", ephemeral=True)   


    # Убрать челикса с тикета
    @commands.slash_command(name = "remove", description = "Remove a Member from the Ticket")
    async def remove(self, ctx, member: Option(discord.Member, description = "Which Member you want to remove from the Ticket", required = True)): # type: ignore
        for role in member.roles:
            if role.name == "CEO" or "Moderator":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
                
        if ticket_continue is True:
            if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
                await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                                    embed_links=False, attach_files=False, read_message_history=False,
                                                    external_emojis=False)
                self.embed = discord.Embed(description = f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use /add to add a User.', color = 0xffc0cb)
                await ctx.respond(embed=self.embed)
            else:
                self.embed = discord.Embed(description = f'You can only use this command in a Ticket!', color = discord.colour.Color.red())
                await ctx.respond(embed=self.embed)
        else:
            self.embed = discord.Embed(title = f"You cannot remove, you don't have permission.", color = 0xffc0cb)
            await ctx.respond(embed = self.embed)

    # Удаляем тикет пупупу
    @commands.slash_command(name = "delete", description = "Delete the Ticket")
    async def delete_ticket(self, ctx):
        for role in member.roles:
            if role.name == "CEO" or "Moderator":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
                
        if ticket_continue is True:        
            guild = self.bot.get_guild(GUILD_ID)
            channel = self.bot.get_channel(LOG_CHANNEL)
            ticket_creator = int(ctx.channel.topic)

            cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,))
            conn.commit()

            # Транскрипт
            military_time: bool = True
            transcript = await chat_exporter.export(
                ctx.channel,
                limit=200,
                tz_info=TIMEZONE,
                military_time=military_time,
                bot=self.bot,
            )       
            if transcript is None:
                return
            
            transcript_file = discord.File(
                io.BytesIO(transcript.encode()),
                filename = f"transcript-{ctx.channel.name}.html")
            transcript_file2 = discord.File(
                io.BytesIO(transcript.encode()),
                filename = f"transcript-{ctx.channel.name}.html")
            
            ticket_creator = guild.get_member(ticket_creator)
            embed = discord.Embed(description = f'Ticket is deliting in 5 seconds.', color = 0xffc0cb)
            transcript_info = discord.Embed(title = f"Ticket Deleting | {ctx.channel.name}", description = f"Ticket from: {ticket_creator.mention}\nTicket Name: {ctx.channel.name} \n Closed from: {ctx.author.mention}", color = discord.colour.Color.blue())

            await ctx.reply(embed = embed)
            # Вкл или выкл лс
            try:
                await ticket_creator.send(embed = transcript_info, file = transcript_file)
            except:
                transcript_info.add_field(name = "Error", value = "Couldn't send the Transcript to the User because he has his DMs disabled!", inline = True)
            await channel.send(embed = transcript_info, file = transcript_file2)
            await asyncio.sleep(3)
            await ctx.channel.delete(reason = "Ticket got Deleted!")
        else:
            self.embed = discord.Embed(title = f"You cannot delete, you don't have permission.", color = 0xffc0cb)
            await ctx.respond(embed = self.embed)