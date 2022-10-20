import nextcord
from nextcord.ext import commands
from datetime import datetime

# Create Dropdown
class BlockDropdown(nextcord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder='Select an Option', min_values=0, max_values=len(options), options=options)
    
    async def callback(self, interaction: nextcord.Interaction):
        if interaction.response.is_done():
            await interaction.response.send_message(embed=error('**You have already used this menu!**\nUse `/availability remove <weekday>` to remove more blocks.'), ephemeral=True)
            return
        
        if len(self.values) == 0: return
        
        for block in self.values:
            interaction.client.execute(f"DELETE FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND USER_ID='{interaction.user.id}' AND BLOCK_ID='{block}'")
        embed = nextcord.Embed(title='Success', description=f'**{len(self.values)} Block(s) removed!**', colour=nextcord.Colour.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


# Asign to view
class BlockDropdownView(nextcord.ui.View):
    def __init__(self, options):
        super().__init__()
        self.add_item(BlockDropdown(options))


def error(message, title='Error'):
    return nextcord.Embed(title=title, description=message, colour=nextcord.Colour.red())


def parse_time(time):
    patterns = [
        # 24-hour
        '%-H%M', # 900
        '%-H:%M', # 9:00
        '%H%M', # 0900
        '%H:%M', # 09:00
        '%H:%M:%S', # 09:00:00
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
    async def availability(self, interaction: nextcord.Interaction):
        return
    


    @availability.subcommand(description='Add a "block" of availability to a weekday.')
    async def add(self, interaction: nextcord.Interaction,
    day: str = nextcord.SlashOption(name='weekday', description='Day to add availability to', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}),
    startTime: str = nextcord.SlashOption(name='begin', description='Start of your availability block'),
    endTime: str = nextcord.SlashOption(name='end', description='End of your availability block'),
    ):
        startTime = parse_time(startTime)
        endTime = parse_time(endTime)
        if not startTime or not endTime:
            await interaction.send(embed=error('Please enter a valid time!'), ephemeral=True)
            return
        elif startTime > endTime:
            await interaction.send(embed=error('End time can not occur before start time!'), ephemeral=True)
            return
        
        self.client.execute(f"INSERT INTO CALENDAR(GUILD_ID, USER_ID, WEEKDAY, START_TIME, END_TIME) VALUES ('{interaction.guild_id}', '{interaction.user.id}', '{day}', '{startTime}', '{endTime}')")
        
        embed = nextcord.Embed(title='Block Saved!', color=nextcord.Color.green())
        embed.add_field(name=day.capitalize(), value=f'{startTime} - {endTime}')
        await interaction.send(embed=embed, ephemeral=True)
        return



    @availability.subcommand(description='Remove a "block" of availability from a weekday.')
    async def remove(self, interaction: nextcord.Interaction,
    day: str = nextcord.SlashOption(name='weekday', description='Day to remove availability to', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}, required=False)
    ):
        if day:
            blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND USER_ID='{interaction.user.id}' AND WEEKDAY='{day}'")
        else:
            blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND USER_ID='{interaction.user.id}'")
        options = []
        for block in blocks:
            options.append(nextcord.SelectOption(
                label=f'{clean_time(block[4])} - {clean_time(block[5])}',
                description=f'{block[3].capitalize()}',
                emoji='❌',
                value=block[0]
            ))
        
        blockDropdown = BlockDropdownView(options)
        embed = nextcord.Embed(title='Delete Blocks', description='Select an availibilty block(s) that you wish to remove!', colour=nextcord.Colour.red())
        await interaction.send(view=blockDropdown, embed=embed, ephemeral=False)
        return



    @calendar.subcommand(description='View a user\'s calendar.')
    async def view(self, interaction: nextcord.Interaction,
    userChoice: nextcord.Member = nextcord.SlashOption(name='user', description='User who\'s calendar to check', required=False)
    ):
        userToSearch = userChoice.id if userChoice else interaction.user.id
        blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND USER_ID='{userToSearch}'")
        
        embed = nextcord.Embed(title=f"{interaction.guild.get_member(userToSearch).name}'s Availability", colour=nextcord.Colour.green())
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            dayBlocks = ''
            for block in blocks:
                if block[3] == day:
                    dayBlocks+=f'{clean_time(block[4])} - {clean_time(block[5])}\n'
            if dayBlocks == '': dayBlocks = 'Not Free'
            embed.add_field(name=day.capitalize(), value=dayBlocks, inline=True)
        
        await interaction.send(embed=embed, ephemeral=True)
        return
    


    @calendar.subcommand(description='View the availibility for a given day.')
    async def day(self, interaction: nextcord.Interaction,
    dayChoice: str = nextcord.SlashOption(name='weekday', description='Day to check availability', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}, default=datetime.now().strftime('%A').lower())
    ):
        blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND WEEKDAY='{dayChoice}'")
        categorised_blocks = {}
        for block in blocks:
            if block[2] not in categorised_blocks:
                categorised_blocks[block[2]] = []
            categorised_blocks[block[2]].append(block)

        embed = nextcord.Embed(title=f"{dayChoice.capitalize()} Availability", colour=nextcord.Colour.green())
        if blocks == []:
            embed.description = '**No blocks on this day!**'
        else:
            for user in categorised_blocks:
                blockEntry = ''
                for block in categorised_blocks[user]:
                    blockEntry+=f'• {clean_time(block[4])} - {clean_time(block[5])}\n'
                embed.add_field(name=interaction.guild.get_member(int(user)).name, value=blockEntry, inline=True)
        
        await interaction.send(embed=embed)
        return



    @calendar.subcommand(description='Check if a user/group of users are free "right now".')
    async def free(self, interaction: nextcord.Interaction,
    userChoice: nextcord.Member = nextcord.SlashOption(name='user', description='Check if user is free', required=False),
    roleChoice: nextcord.Role = nextcord.SlashOption(name='role', description='Start typing the name of the role for more options', required=False),
    dayChoice: str = nextcord.SlashOption(name='weekday', description='Day to check availability', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}, default=datetime.now().strftime('%A').lower())
    ):
        users: nextcord.User = []
        if userChoice: users.append(userChoice)
        if roleChoice: users+=roleChoice.members

        if len(users) == 0:
            await interaction.response.send_message(embed=error('Please select either a user or a role!.'), ephemeral=True)
            return

        embed = nextcord.Embed(title=f"Availability", colour=nextcord.Colour.green())
        embedList = ''
        now = datetime.now().time()
        for user in users:
            if user.bot: continue
            blocks = self.client.query(f"SELECT * FROM CALENDAR WHERE GUILD_ID='{interaction.guild_id}' AND USER_ID='{user.id}' AND WEEKDAY='{dayChoice}'")
            busy = False
            for block in blocks:
                if parse_time(block[4]) < now and parse_time(block[5]) > now:
                    embedList+=f'\ud83d\udfe2 **{user.name}** (until {clean_time(block[5])})\n'
                    busy = True
                    break
            if not busy: embedList+=f'\ud83d\udd34 **{user.name}**\n'
        embed.description = embedList
        await interaction.send(embed=embed)
        return



def setup(client):
    client.add_cog(Calendar(client))