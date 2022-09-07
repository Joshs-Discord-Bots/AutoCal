#region ------------------------------------------------------ SETUP -------------------------------------------------

from nextcord.ext import commands
import nextcord, os, platform, json

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


#region ------------------------------------------------- CUSTOM CLASSES -------------------------------------------

class Block():
    def __init__(self, blockData = {}):
        if blockData == {}: return
        self.member = blockData['member']
        self.startTime = blockData['startTime']
        self.endTime = blockData['endTime']
    
    member = None
    startTime = None
    endTime = None
    
    def toJSON(self): return {'member': self.member, 'startTime': self.startTime, 'endTime': self.endTime}


class Day():
    def __init__(self, blocks = []):
        for block in blocks:
            self.blocks.append(Block(block))
    
    blocks: Block = []

    def toJSON(self): 
        blocks = []
        for block in self.blocks:
            blocks.append(block.toJSON())
        return blocks

    def addBlock(self, member, startTime, endTime):
        tempBlock = {
            'member': member, 
            'startTime': startTime, 
            'endTime': endTime
        }
        # Check member, startTime, endTime
        block = Block(tempBlock)
        self.blocks.append(block)

class Calendar():
    def __init__(self, fileName: str):
        self.fileName = fileName
        calendar = read(fileName)
        if calendar != None: 
            for day in calendar:
                calendar[day] = Day(calendar[day])
            self.days = calendar
    
    filename = ''
    days = {
        'monday': Day(),
        'tuesday': Day(),
        'wednesday': Day(),
        'thursday': Day(),
        'friday': Day(),
        'saturday': Day(),
        'sunday': Day(),
    }

    def save(self):
        calJSON = self.days
        for day in calJSON:
            calJSON[day] = calJSON[day].toJSON()
        write(calJSON, self.fileName)



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


#endregion
clear()
print('Booting Up...')

client.run(client.token)