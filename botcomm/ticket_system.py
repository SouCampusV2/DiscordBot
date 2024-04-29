import discord
import asyncio
import json
import sqlite3
import chat_exporter
import io
from discord.ext import commands

# Берем все айдишки с конфига
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

GUILD_ID = config["guild_id"] # Айдишка сервера ака гуилд
TICKET_CHANNEL = config["ticket_channel_id"] # Канал в котором менюшка тикетов

CATEGORY_ID1 = config["category_id_1"] # Категория 1 (ордер)
CATEGORY_ID2 = config["category_id_2"] # Категория 2 (апплай)
CATEGORY_ID3 = config["category_id_3"] # Категория 3 (хелп)

TEAM_ROLE1 = config["team_role_id_1"] # Роль которая будет в тикете 1
TEAM_ROLE2 = config["team_role_id_2"] # Роль которая будет в тикете 2

LOG_CHANNEL = config["log_channel_id"] # Куда будет бот логи закидывать 
TIMEZONE = config["timezone"] # Таймзона

# Подключаемся к дбшке
conn = sqlite3.connect('user.db')
cur = conn.cursor()

# Создаем дбшку если ее нету
cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Бот подгрузил системочку | {self.bot.user.name} ✅')
        self.bot.add_view(MyView(bot=self.bot))
        self.bot.add_view(CloseButton(bot=self.bot))
        self.bot.add_view(TicketOptions(bot=self.bot))

    # После того как бот умирает закрываем дбшку
    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

class MyView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)



    # Менюшка выпадающая с выбором тикета
    @discord.ui.select(
        custom_id = "support",
        placeholder = "Choose a Ticket option",
        options = [
            discord.SelectOption(
                label = "Order", # Имя первой кнопки
                description = "You can ask us to build your order!", # Описание
                emoji = "<:2759floweremote:1233454904291627101>", # Эмоджи
                value = "support1" # Значение
            ),
            discord.SelectOption(
                label = "Apply", # Имя первой кнопки
                description = "Apply to our team!", # Описание
                emoji = "<:9615partnernoteligible:1233454989985316925>", # Эмоджи
                value = "support2" # Значение
            ),
            discord.SelectOption(
                label = "Support",# Имя первой кнопки
                description = "Ask questions here!", # Описание
                emoji = "<:1919_blobhelp_zoom:1233455197032808610>", # Эмоджи
                value = "support3" # Значение
            )
        ]
    )

    async def callback(self, select, interaction):
        if "support1" in interaction.data['values']: 
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT * FROM ticket WHERE discord_id=?", (member_id,)) # Чекаем сколько есть тикетов
                existing_ticket = cur.fetchall()
                print(len(existing_ticket))
                print(existing_ticket)

                if (len(existing_ticket) < 4):
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) # Если нету вставляем челикса еще в бдшку
                    category = self.bot.get_channel(CATEGORY_ID1)
                    ticket_channel = await guild.create_text_channel(f"ticket-{member_name}", category = category,
                                                                    topic = f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True, add_reactions=False, # Добавляем разрешенные роли
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, # Добавляем того кто создал в тикет
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False) # Для всех остальных убираем  разрешенние смотреть канал
                    embed = discord.Embed(title = "SouCampus order<:2759floweremote:1233454904291627101>", 
                                            description = f'**Describe your commission:\n**\[Please, provide us all details of what you want.\]\n\n**Deadline:**\n[Please, write approximate dates when you need to complete your order or how much time you have.\]\n\n**References/Examples:**\n[Please, provide us an idea and an image of what you want.\]\n\n**Size:**\n[Please, write approximate size of your building.\]\n\n**Theme/Style:**\n[Please, write what style do you prefer.\]\n\n**Version:**\n[Please, write version of Minecraft that you need.\]\n\n**Anymore details:**\n[Please, write some more details, any special spots, portals, etc...\]\n\n**Budget:**\n[Please, write approximate budget that you can spend on your commission.\]',
                                            color = 0xffc0cb)
                    await ticket_channel.send(embed = embed, view = CloseButton(bot = self.bot)) # Кнопка чтобы закрыть тикет если что
                    await ticket_channel.send

                    embed = discord.Embed(description = f'📬 Ticket was Created! Look here --> {ticket_channel.mention}', 
                                            color = 0xffc0cb)
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title = "SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                              color = 0xffc0cb, 
                              description = "If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.", 
                              )
                    embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
                    await interaction.message.edit(embed = embed, view = MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
                else:
                    embed = discord.Embed(title = f"You already have a lot of opened Ticket", color = 0xffc0cb)
                    await interaction.response.send_message(embed = embed, ephemeral = True) #This will tell the User that he already has a Ticket open
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                              color = 0xffc0cb, 
                              description="If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.", 
                              )
                    embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
                    await interaction.message.edit(embed = embed, view = MyView(bot = self.bot)) #This will reset the SelectMenu in the Ticket Channel
        
        elif "support2" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchall()
                print(len(existing_ticket))
                print(existing_ticket)
                if (len(existing_ticket) < 4):
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID2)
                    ticket_channel = await guild.create_text_channel(f"ticket-{member_name}", category = category,
                                                                    topic = f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False) #Set the Permissions for the @everyone role
                    embed = discord.Embed(description = f'Welcome {interaction.user.mention},\n' #Ticket Welcome message
                                                       'You can apply here, thank you for hiring us!',
                                                    color = 0xffc0cb)
                    await ticket_channel.send(embed = embed, view = CloseButton(bot = self.bot))

                    embed = discord.Embed(description = f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color = 0xffc0cb)
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title = "SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                              color = 0xffc0cb, 
                              description = "If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.", )
                    embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
                    await interaction.message.edit(embed = embed, view = MyView(bot = self.bot)) #This will reset the SelectMenu in the Ticket Channel

        elif "support3" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchall()
                print(len(existing_ticket))
                print(existing_ticket)
                if (len(existing_ticket) < 4):
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID3)
                    ticket_channel = await guild.create_text_channel(f"ticket-{member_name}", category = category,
                                                                    topic = f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False) #Set the Permissions for the @everyone role
                    embed = discord.Embed(description = f'Welcome {interaction.user.mention},\n' #Ticket Welcome message
                                                       'How can we help you, describe the problem!',
                                                    color = 0xffc0cb)
                    await ticket_channel.send(embed = embed, view = CloseButton(bot = self.bot))

                    embed = discord.Embed(description = f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color = 0xffc0cb)
                    await interaction.response.send_message(embed = embed, ephemeral = True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title = "SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                              color = 0xffc0cb, 
                              description = "If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.", 
                              )
                    embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
                    await interaction.message.edit(embed = embed, view = MyView(bot = self.bot)) #This will reset the SelectMenu in the Ticket Channel

                else:
                    embed = discord.Embed(title = f"You already have a lot of opened Tickets", color = 0xffc0cb)
                    await interaction.response.send_message(embed = embed, ephemeral = True) #This will tell the User that he already has a Ticket open
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="SouCampus Tickets<:2759floweremote:1233454904291627101>", 
                              color = 0xffc0cb, 
                              description = "If you need help or have a question, click one of the buttons below to open a support ticket. Please be aware that any abuse of the ticketing system, including troll messages, will result in repercussions.", 
                              )
                    embed.set_image(url = "https://optim.tildacdn.pub/tild3333-3564-4366-b739-376366633936/-/format/webp/HeavenKeyStone.png")
                    await interaction.message.edit(embed = embed, view = MyView(bot = self.bot)) #This will reset the SelectMenu in the Ticket Channel
        return

#First Button for the Ticket 
class CloseButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label = "Close Ticket🌸", style = discord.ButtonStyle.blurple, custom_id = "close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        ticket_creator = guild.get_member(ticket_creator)
        member = interaction.user

        for role in member.roles:
            if role.name == "CM team" or "Moderator" or "CEO":
                ticket_continue = True
                continue
            else:
                ticket_continue = False
            
        if ticket_continue:
            embed = discord.Embed(title = "Ticket Closed🌸", description = "Press Reopen to open the Ticket again or Delete to delete the Ticket!", color = 0xffc0cb)
            await interaction.channel.set_permissions(ticket_creator, send_messages=False, read_messages=False, add_reactions=False,
                                                            embed_links=False, attach_files=False, read_message_history=False, # Права кто может єто делать
                                                            external_emojis=False)
            await interaction.channel.edit(name = f"ticket-closed-{ticket_creator.name}")
            await interaction.response.send_message(embed = embed, view=TicketOptions(bot = self.bot)) # Варианты покажет
            button.disabled = True
            await interaction.message.edit(view=self)
        else: 
            print("Siis sa ei ole admin.")

# Кнопочки чтобы удалить или открыть еще раз тикет
class TicketOptions(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label = "Reopen Ticket🌸", style = discord.ButtonStyle.green, custom_id = "reopen")
    async def reopen_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        embed = discord.Embed(title = "Ticket Reopened 🎫", description = "Press Delete Ticket to delete the Ticket!", color = 0xffc0cb) 
        ticket_creator = guild.get_member(ticket_creator)
        await interaction.channel.set_permissions(ticket_creator, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=False)
        await interaction.channel.edit(name = f"ticket-{ticket_creator.name}") 
        await interaction.response.send_message(embed = embed)

    @discord.ui.button(label = "Delete Ticket🌸", style = discord.ButtonStyle.blurple, custom_id = "delete")
    async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_creator = int(interaction.channel.topic)

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,)) # Удаляем с дбшки тикет
        conn.commit()

        # Транскрипт
        military_time: bool = True
        transcript = await chat_exporter.export(
            interaction.channel,
            limit = 200,
            tz_info = TIMEZONE,
            military_time = military_time,
            bot=self.bot,
        )       
        if transcript is None:
            return
        
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        
        ticket_creator = guild.get_member(ticket_creator)
        embed = discord.Embed(description = f'Ticket is deliting in 5 seconds.', color = 0xffc0cb)
        transcript_info = discord.Embed(title = f"Ticket Deleting | {interaction.channel.name}", description = f"Ticket from: {ticket_creator.mention}\nTicket Name: {interaction.channel.name} \n Closed from: {interaction.user.mention}", color = 0xffc0cb)

        await interaction.response.send_message(embed = embed)
        # Чекаем включен ли лс
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name = "Error", value = "Couldn't send the Transcript to the User because he has his DMs disabled!", inline = True)
        await channel.send(embed = transcript_info, file = transcript_file2)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason = "Ticket got Deleted!")