import discord
import aiosqlite
import datetime
import yaml
from discord import app_commands
from discord.ext import commands, tasks

with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)

guild_id = data["General"]["GUILD_ID"]
embed_color = data["General"]["EMBED_COLOR"]
added_roles = data["Tickets"]["ADDED_ROLES"]
english_ticket_category_id = data["Tickets"]["ENGLISH_TICKET_CATEGORY_ID"]
spanish_ticket_category_id = data["Tickets"]["SPANISH_TICKET_CATEGORY_ID"]

class EnglishEmail(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Find Email', url="https://billing.cookie.host/clientarea.php?action=details"))

class EnglishURL(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='Find URL', url="https://game.cookie.host"))

class Tickets(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(emoji='✉', label='English', style=discord.ButtonStyle.blurple, custom_id='tickets:1')
    async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description="Creating...", color=discord.Color.from_str(embed_color))
        await interaction.response.send_message(embed=embed, ephemeral=True)
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT * FROM counter')
        a = await cursor.fetchone()
        await db.execute('UPDATE counter SET number=number + ?', (1,))

        category = interaction.guild.get_channel(english_ticket_category_id)
        ticket_channel = await category.create_text_channel(f"english-7{a[1]:03}")
        await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id),
            send_messages=False,
            read_messages=False)
        await db.commit()
        await db.close()

        embed = discord.Embed(description=f"Ticket created at {ticket_channel.mention}!", color=discord.Color.from_str(embed_color))
        await interaction.edit_original_response(embed=embed)

        for x in added_roles:

            role = interaction.guild.get_role(x)
            
            await ticket_channel.set_permissions(role,
                send_messages=True,
                read_messages=True,
                add_reactions=True,
                embed_links=True,
                read_message_history=True,
                external_emojis=True)
        
        await ticket_channel.set_permissions(interaction.user,
            send_messages=True,
            read_messages=True,
            add_reactions=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            external_emojis=True)

        def check(message):
            return message.channel == ticket_channel and message.author == interaction.user

        f = discord.File("imgs/email.png", filename="email.png")
        a = discord.Embed(title="What is your billing email?", description="Image given below is an example:", color=discord.Color.from_str(embed_color))
        a.set_image(url="attachment://email.png")
        await ticket_channel.send(content=interaction.user.mention, embed=a, file=f, view=EnglishEmail())
        question1 = await self.bot.wait_for('message', check=check)

        f = discord.File("imgs/url.png", filename="url.png")
        b = discord.Embed(title=f"""Paste the URL of the server that you are facing issues with. Type "none" if you don't have a server.""", description="Image given below is an example:", color=discord.Color.from_str(embed_color))
        b.set_image(url="attachment://url.png")
        await ticket_channel.send(content=interaction.user.mention, embed=b, file=f, view=EnglishURL())
        question2 = await self.bot.wait_for('message', check=check)

        c = discord.Embed(title="What is the issue you're facing?", color=discord.Color.from_str(embed_color))
        await ticket_channel.send(content=interaction.user.mention, embed=c)
        question3 = await self.bot.wait_for('message', check=check)

        embed = discord.Embed(title="Ticket Created", description=f"A support team member will be with you shortly! \n\n**Email:** \n{question1.content} \n\n**URL:** \n{question2.content} \n\n**Issue:** \n{question3.content}", color=discord.Color.from_str(embed_color))
        await ticket_channel.send(embed=embed)

    @discord.ui.button(emoji='✉', label='Español', style=discord.ButtonStyle.blurple, custom_id='tickets:2')
    async def spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(description="Creando...", color=discord.Color.from_str(embed_color))
        await interaction.response.send_message(embed=embed, ephemeral=True)

class TicketsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.add_view(Tickets(bot))

    def cog_load(self):
        self.ticketcloseLoop.start()

    @tasks.loop(seconds = 5)
    async def ticketcloseLoop(self):
        db = await aiosqlite.connect('database.db')
        cursor = await db.execute('SELECT * FROM counter')
        a = await cursor.fetchone()
        month = datetime.date.today().month
        if a[0] == month:
            pass
        else:
            await db.execute('UPDATE counter SET month=?, number=?', (month, 000))
        await db.commit()
        await db.close()

    @ticketcloseLoop.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="panel", description="Sends the ticket panel!")
    @app_commands.default_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction) -> None:
        view = Tickets(self.bot)
        embed = discord.Embed(title="Support Tickets",description=f"Click below to open a support ticket. \n\nPlease select what language you want the support ticket to be in:", color=discord.Color.from_str(embed_color))
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message('Sent!', ephemeral=True)

    @app_commands.command(name="add", description="Adds someone to a ticket!")
    @app_commands.describe(member="Who do you want to add to the ticket?")
    async def add(self, interaction: discord.Interaction, member: discord.Member) -> None:
        valid_channels = ("service", "report", "rule", "other", "submission", "translator")
        if any(thing in interaction.channel.name for thing in valid_channels):
            await interaction.channel.set_permissions(member,
                send_messages=True,
                read_messages=True,
                add_reactions=True,
                embed_links=True,
                read_message_history=True,
                external_emojis=True)
            await interaction.response.send_message(f"Added {member.mention}!")
        else:
            await interaction.response.send_message("This is not a valid ticket channel!", ephemeral=True)

    @app_commands.command(name="remove", description="Removes someone from a ticket!")
    @app_commands.describe(member="Who do you want to remove from the ticket?")
    async def remove(self, interaction: discord.Interaction, member: discord.Member) -> None:
        valid_channels = ("service", "report", "rule", "other", "submission", "translator")
        if any(thing in interaction.channel.name for thing in valid_channels):
            await interaction.channel.set_permissions(member,
                send_messages=False,
                read_messages=False,
                add_reactions=False,
                embed_links=False,
                read_message_history=False,
                external_emojis=False)
            await interaction.response.send_message(f"Removed {member.mention}!")
        else:
            await interaction.response.send_message("This is not a valid ticket channel!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketsCog(bot), guilds=[discord.Object(id=guild_id)])