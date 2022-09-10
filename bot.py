#region ------------------------------------------------------ SETUP -------------------------------------------------

from email.mime import image
from nextcord.ext import commands
import nextcord, os, platform, json, sqlite3

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

if not os.path.isfile('config.json'):
    def_config = {
        'token': 'TOKEN',
        'intents': {'messages': False, 'members': False, 'guilds': False},
        'prefix': '-',
        'admins': []
    }
    write(def_config, 'config.json')

config = read('config.json')

intents = nextcord.Intents.default()
intents.message_content = config['intents']['messages']
intents.members = config['intents']['members']
intents.guilds = config['intents']['guilds']

prefix = config['prefix']

client = commands.Bot(command_prefix=prefix, intents=intents)
client.token = config['token']
client.admins = config['admins']
client.query = query
client.execute = execute


#region ------------------------------------------------- CUSTOM CLASSES -------------------------------------------



#endregion

#region ------------------------------------------------- STARTUP FUNCTIONS -------------------------------------------

def clear():
    return
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
#region ----------------------------------------------------- COGS -------------------------------------------------

whitelist = ['calendar.py']
cogs = [] # So we can reload them
for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename in whitelist:
        cog = f'cogs.{filename[:-3]}'
        client.load_extension(cog)
        cogs.append(cog)

@client.slash_command()
async def test(interaction : nextcord.Interaction):
    embed = nextcord.Embed(
        title='Title',
        description='Description',
        color=nextcord.Color.orange())
    # embed.set_image(interaction.user.avatar)
    embed.set_thumbnail(interaction.user.avatar)
    await interaction.send(embed=embed)
    return

#endregion
clear()
print('Booting Up...')

client.run(client.token)