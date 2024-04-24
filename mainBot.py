import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

# Comment
# Пока что работает так, что мне каждый раз нужно вызывать команду чтобы юзать ее.
# Нужно сделать так чтобы кнопка была статична, и всега существовала и на нее откликалось создание.

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.create_ticket_button = None

    @discord.ui.button(label="Create Ticket", row=0, style=discord.ButtonStyle.primary, custom_id = "create_ticket_button")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        print("1")
        member = interaction.user
        guild = interaction.guild

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.get_role(1232373808527048854): discord.PermissionOverwrite(read_messages=True),
            guild.get_role(1232373606273777754): discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=True),
        }
        channel = await guild.create_text_channel(f"ticket-{member.name}", overwrites=overwrites)
        await interaction.response.send_message(f"Ticket channel created: {channel.mention}")

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")



intents = discord.Intents.all()
intents.message_content = True


bot = commands.Bot(command_prefix=".", help_command=None, intents=intents)

@bot.event
async def on_ready():
    print("Bot bo")
    view = MyView()

    button_exists = any(button.custom_id == "create_ticket_button" for button in view.children)
    if button_exists:
        print("Кнопка с custom_id 'create_ticket_button' уже была создана")
    else:
        print("Кнопка с custom_id 'create_ticket_button' еще не создана")
    await bot.tree.sync()


@bot.command()
async def ticket(ctx):
    await ctx.send("Click to create a ticket:", view=MyView())

# Просто команда если прописать префикс и !название
@bot.command()
async def hello(ctx):
    await ctx.send("Hii There! I am BoCampus!")

# Команда которая покажет аватарку пользователя
@bot.command()
async def av(ctx,member: discord.Member):
    await ctx.send(member.display_avatar)

# Слэш команда которая просто выводит что-то
@bot.tree.command(name = "bocampus", description = "Hello, I'm BoCampus, and I was built in 2024, 23.04 at 2:14")
async def slash_command(interaction:discord.Interaction):
    await interaction.response.send_message("Getting some info")

def main() -> None:
    bot.run(TOKEN)

if __name__ == "__main__":
    main()


