import nextcord
from nextcord.ext import commands
from bot import Calendar as CreateCalendar

class Calendar(commands.Cog):
    def __init__(self, client):
        self.client = client
    def admin(self, member):
        return True if member.id in self.client.admins else False


    @nextcord.slash_command(description='Manage Calendar')
    async def calendar(self, interaction: nextcord.Interaction):
        return
    
    # Add Roles
    @calendar.subcommand(description='Manage Unavailibility')
    async def unavailibility(self, interaction: nextcord.Interaction):
        return
    
    @unavailibility.subcommand(description='Add Unavailibility')
    async def add(self, interaction: nextcord.Interaction,
    day: str = nextcord.SlashOption(name='type', choices={'Monday': 'monday', 'Tuesday': 'tuesday', 'Wednesday': 'wednesday', 'Thursday': 'thursday', 'Friday': 'friday', 'Saturday': 'saturday', 'Sunday': 'sunday'}),
    startTime: str = nextcord.SlashOption(name='test1', required=True),
    endTime: str = nextcord.SlashOption(name='test2', required=True),
    ):
        calendar = CreateCalendar('calendar.json')
        calendar.days[day].addBlock(interaction.user.id, startTime, endTime)
        calendar.save()
        await interaction.send('Block Saved!')
        return


def setup(client):
    client.add_cog(Calendar(client))