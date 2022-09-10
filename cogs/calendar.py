from time import time
import nextcord
from nextcord.ext import commands
from datetime import datetime

def parse_time(time):
    patterns = [
        # 24-hour
        '%-H%M', # 900
        '%-H:%M', # 9:00
        '%H%M', # 0900
        '%H:%M', # 09:00
        # 12-hour
        '%-I%p', # 1pm
        '%I%p', # 01pm
        '%-I%M%p', # 130pm
        '%I%M%p', # 0130pm
        '%-I:%M%p', # 1:00pm
        '%I:%M%p', # 01:00pm
    ]
    for pattern in patterns:
        try:
            return datetime.strptime(time, pattern).time()
        except:
            pass
    return False

def clean_time(time):
    formated = datetime.strptime(time, '%H:%M:%S')
    if formated.minute > 0:
        cleaned = datetime.strftime(formated, '%I:%M%p')
    else:
        cleaned = datetime.strftime(formated, '%I%p')
    if cleaned[0] == '0': cleaned = cleaned[1:]
    return cleaned.lower()

class Calendar(commands.Cog):
    def __init__(self, client):
        self.client = client
    def admin(self, member):
        return True if member.id in self.client.admins else False

    @nextcord.slash_command(description='Manage Calendar')
    async def calendar(self, interaction: nextcord.Interaction):
        return
    
    # Add Roles
    @nextcord.slash_command(description='Manage Unavailability')
    async def unavailability(self, interaction: nextcord.Interaction):
        return
    
    @unavailability.subcommand(description='Add Unavailability')
    async def add(self, interaction: nextcord.Interaction,
    day: str = nextcord.SlashOption(name='weekday', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}),
    startTime: str = nextcord.SlashOption(name='begin', description='Start of your unavailability block'),
    endTime: str = nextcord.SlashOption(name='end', description='End of your unavailability block'),
    ):
        startTime = parse_time(startTime)
        endTime = parse_time(endTime)
        if not startTime or not endTime:
            embed = nextcord.Embed(title='Error', description='**Please enter a valid time!**', colour=nextcord.Colour.red())
            await interaction.send(embed=embed, ephemeral=True)
            return
        
        self.client.execute(f"INSERT INTO CALENDAR(USER_ID, WEEKDAY, START_TIME, END_TIME) VALUES ({interaction.user.id}, '{day}', '{startTime}', '{endTime}')")
        
        await interaction.send('Block Saved!', ephemeral=True)
        return

    @unavailability.subcommand(description='Add Unavailability')
    async def remove(self, interaction: nextcord.Interaction,
    # day: str = nextcord.SlashOption(name='weekday', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'})
    ):

        # create dropdown with blocks

        # self.client.execute(f"DELETE FROM CALENDAR WHERE USER_ID={userToSearch}")
        
        # await interaction.send('Block Saved!', ephemeral=True)
        await interaction.send('Not implemented yet!', ephemeral=True)
        return


    @calendar.subcommand(description='Add Unavailability')
    async def check(self, interaction: nextcord.Interaction,
    userChoice: nextcord.Member = nextcord.SlashOption(name='user', required=False)
    ):
        userToSearch = userChoice.id if userChoice else interaction.user.id
        blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE USER_ID={userToSearch}")
        
        embed = nextcord.Embed(title=f"{interaction.guild.get_member(userToSearch).name}'s Unavailability", colour=nextcord.Colour.red())
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            dayBlocks = ''
            for block in blocks:
                if block[2] == day:
                    dayBlocks+=f'{clean_time(block[3])}-{clean_time(block[4])}\n'
            if dayBlocks == '': dayBlocks = 'No Blocks'
            embed.add_field(name=day.capitalize(), value=dayBlocks, inline=True)
        
        await interaction.send(embed=embed, ephemeral=True)
        return
    
    @calendar.subcommand(description='Check unavailability for Day')
    async def day(self, interaction: nextcord.Interaction,
    dayChoice: str = nextcord.SlashOption(name='weekday', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'})
    ):
        blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE WEEKDAY='{dayChoice}'")
        
        embed = nextcord.Embed(title=f"{dayChoice.capitalize()} Unavailability", colour=nextcord.Colour.red())
        for block in blocks:
            blockEntry = ''
            for block in blocks:
                blockEntry+=f'**{interaction.guild.get_member(block[1]).name}:** {block[3]}-{block[4]}\n'
        embed.add_field(name='Results', value=blockEntry, inline=True)
        
        await interaction.send(embed=embed, ephemeral=True)
        return


def setup(client):
    client.add_cog(Calendar(client))