#region ------------------------------------------------------ SETUP -------------------------------------------------

from nextcord.ext import commands
import nextcord, os, platform, json, sqlite3
from time import sleep

def read(readFilename):
    try:
        with open(readFilename) as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return None

def write(data, writeFilename):
    with open(writeFilename, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return

def query(query):
    connection = sqlite3.connect('calendar.db')
    if connection:
        exec = connection.cursor().execute(query).fetchall()
        connection.close()
        return exec
    else: 
        connection.close()
        print('Failed to establish a connection to database')
        return False

def execute(query):
    connection = sqlite3.connect('calendar.db')
    if connection:
        connection.execute(query)
        connection.commit()
    else: 
        print('Failed to establish a connection to database')
    connection.close()
    return


# Create config file
config = {}
envTypes = {
    "str": ['TOKEN', 'DEVTOKEN', 'PREFIX', 'ADMINS'],
    "bool": ['DEVMODE', 'MESSAGES', 'MEMBERS', 'GUILDS', 'VOICE_STATES']
}
# Ensure .env format
for envType in envTypes:
    for envVar in envTypes[envType]:
        envVal = os.environ[envVar]
        # Convert bool string to bools
        if envType == 'bool':
            envVal = os.environ[envVar].lower() in ['true']
        # Check for missing environment variables
        if envVar not in os.environ:
            print(f'"{envVar}" environment variable not initialised! Please ensure you have a VALID .env file')
            print('Please read the README.md file for more details.')
            exit()
        config[envVar] = envVal

intents = nextcord.Intents.default()
intents.message_content = config['MESSAGES']
intents.members = config['MEMBERS']
intents.guilds = config['GUILDS']
intents.voice_states = config['VOICE_STATES']

client = commands.Bot(command_prefix=config['PREFIX'], intents=intents)

client.read = read
client.write = write
client.token = config['TOKEN']
client.admins = config['ADMINS']
client.dev = config['DEVMODE']

client.query = query
client.execute = execute


#region ------------------------------------------------- STARTUP FUNCTIONS -------------------------------------------

def clear():
    # return
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def admin(member):
    return True if member.id in client.admins else False

@client.event
async def on_ready():
    clear()
    print(f'{client.user} has connected to Discord!')


#endregion
#region --------------------------------------------------- COMMANDS -----------------------------------------------

@client.slash_command(description='List of available commands')
async def help(interaction : nextcord.Interaction):
    embed = nextcord.Embed(
        title='Commands',
        color=nextcord.Color.blue())
    embed.add_field(name='`/availability add`', value='Add a "block" of availability to a weekday.', inline=False)
    embed.add_field(name='`/availability remove`', value='Remove a "block" of availability from a weekday.', inline=False)
    
    embed.add_field(name='`/calendar view <user>`', value='View a user\'s calendar.', inline=False)
    embed.add_field(name='`/calendar day <weekday>`', value='View the availibility for a given day.', inline=False)
    embed.add_field(name='`/calendar free <user>`', value='Check if a user/group of users are free.', inline=False)
    await interaction.send(embed=embed, ephemeral=True)
    return

#endregion
#region ----------------------------------------------------- COGS -------------------------------------------------

whitelist = ['calendar.py']
cogs = [] # So we can reload them
for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename in whitelist:
        cog = f'cogs.{filename[:-3]}'
        client.load_extension(cog)
        cogs.append(cog)
#endregion



clear()
print('Booting Up...')

while True:
    try:
        client.run(client.token)
    except Exception as error:
        print('Failed to start bot')
        print('-'*10+' Error '+'-'*10)
        print(error)
        print('-'*30)
        print('Retrying in 5 seconds...')
        sleep(5)
