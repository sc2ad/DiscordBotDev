import discord
# from discord.ext import commands as discord_cmds
import json
import template_server_serializer
import template_server_deserializer
import utils.json_yaml_validator as validator
import os
import utils.permission_verification as verifier

READY_STATUS = "Discord Bot now online!"
CONFIG_FILE = "main.bot_config.json"
CONFIG_SCHEMA = "bot_config_schema.json"

client = discord.Client()
config = None
commands = None

def printMessage(message):
    print("Message Received from Author: (" + str(message.author) + ", " + str(message.author.id) + ") with content: " + message.content)

def getCommands():
    global commands, config
    if not commands:
        config = validator.load(CONFIG_FILE, CONFIG_SCHEMA)
        commands = {item['ID']: item for item in config['commands']}
        print("Loaded commands: " + str(commands.keys()))

def isCommand(message):
    assert commands != None, "Commands should exist!"
    # Checks to see if the given message is a command of the bot.
    # This should instead be swapped for using ACTUAL discord.exts.commads (see main.py)
    for k in commands.keys():
        if matchesCommand(k, message):
            return True
    return False

def getCommand(key):
    assert commands != None, "Commands should exist!"
    if not key in commands.keys():
        return None
    return commands[key]

def matchesCommand(key, message):
    c = getCommand(key)
    if not c:
        return False
    if c['type'] == "prefixedCommand":
        if message.content.startswith(config['prefix'] + c['usage']):
            return True
    elif c['type'] == "macro":
        if c['usage'] in message.content:
            return True
    return False

def getUIDFromMention(mention):
    return int(mention.replace("<", "").replace(">", "").replace("@", "").replace("!", ""))

async def parseArg(real_arg, match_arg):
    try:
        if match_arg['type'] == "string":
            return real_arg
        if match_arg['type'] == "command":
            return getCommand(real_arg) if getCommand(real_arg) != None else None
        elif match_arg['type'] == "mention":
            return real_arg if real_arg.startswith("<") and real_arg.endswith(">") and not "#" in real_arg else None
        elif match_arg['type'] == "user":
            if real_arg.startswith("<") and real_arg.endswith(">") and not "#" in real_arg:
                return await client.fetch_user(getUIDFromMention(real_arg))
            return None
        elif match_arg['type'] == "int":
            return int(real_arg)
        elif match_arg['type'] == "number":
            return float(real_arg)
        elif match_arg['type'].startswith("file"):
            ext = '.'.join(match_arg['type'].split(".")[1:])
            return real_arg if real_arg.endswith(ext) else None
        elif match_arg['type'].startswith("existingFile"):
            ext = '.'.join(match_arg['type'].split(".")[1:])
            return real_arg if real_arg.endswith(ext) and os.path.exists(real_arg) else None
    except:
        return None

async def parseArgs(key, message):
    assert commands != None, "Commands should exist!"
    if not key in commands.keys():
        # INVALID!
        return "INVALID COMMAND!"
    if commands[key]['type'] == 'macro':
        # INVALID!
        return "Cannot parse commands of macros!"
    argOptions = message.content.split(" ")[1:] # Ignore actual command call
    if len(argOptions) < len(commands[key]['arguments']):
        return "Not enough arguments! Expected: " + str(len(commands[key]['arguments'])) + " but got: " + str(len(argOptions))
    arguments = {}
    realArgIndex = 0
    for i in range(len(commands[key]['arguments'])):
        argument = commands[key]['arguments'][i]
        if i == 0:
            # Only check the first argument to see if it matches
            if argument['type'].startswith('_self'):
                # Special argument, refers to the self of the message.
                # Doesn't actually count as an argument.
                if argument['type'] == '_selfMention':
                    arguments[argument['name']] = message.author.mention
                continue
        arguments[argument['name']] = await parseArg(argOptions[realArgIndex], argument)
        if arguments[argument['name']] == None:
            return "Could not convert to argument type: " + argument['type'] + " with argument: " + argOptions[realArgIndex]
        realArgIndex += 1
    if 'lastArgumentMultiple' in commands[key].keys() and commands[key]['lastArgumentMultiple']:
        arguments[argument['name']] = [arguments[argument['name']]]
        for i in range(realArgIndex + 1, len(argOptions)):
            # Will add all extraneous arguments until reaching an arg it can't parse, then returns
            arg = await parseArg(argOptions[i], commands[key]['arguments'][:-1])
            if arg == None:
                return arguments
            arguments[argument['name']].append(arg)
    # TODO ADD OPTIONAL ARGUMENTS
    return arguments

def permissions(command, message):
    return verifier.verifyMacroUser(command, message.author.id, message.author.roles) and message.author.id != client.user.id

@client.event
async def on_ready():
    print("Logged into discord!")
    getCommands()

@client.event
async def on_message(message):
    printMessage(message)
    channel = message.channel
    if not isCommand(message):
        return
    # TODO ADD HELP
    if matchesCommand('hot_macro', message):
        if not permissions('hot_macro', message):
            # Not allowed to perform commands.
            await channel.send(message.author.name + ' does not have access to this command. feelssadman :(')
            return
        await channel.send('HOT STUFF IS COMING')
    if matchesCommand('addPermissions_command', message):
        if not permissions('addPermissions_command', message):
            # Not allowed to perform commands.
            await channel.send(message.author.name + ' does not have access to this command. feelssadman :(')
            return
        args = await parseArgs('addPermissions_command', message)
        if type(args) == str:
            await channel.send(args)
        else:
            command = args['command']
            users = args['mentions']
            for user in users:
                verifier.addUser(user.id, user.name, command)
                await channel.send(user.name + ' was given permissions to command: ' + command['name'] + '! AHH THATS HOT')
        #for role in message.mention_roles:
            #verifier.addRole(role.id, role.name)
            #await channel.send(role.name + ' role now has macros! AHH THATS HOT')
    if matchesCommand("save-template_command", message):
        if not permissions('save-template_command', message):
            # Not allowed to perform commands.
            await channel.send(message.author.name + ' does not have access to this command. feelssadman :(')
            return
        args = await parseArgs("save-template_command", message)
        if type(args) == str:
            await channel.send(args)
        else:
            path = args['templateFile']
            if not path.endswith(".server.json"):
                lst = path.split(".")
                lst = lst[:len(lst) - 1]
                path = ".".join(lst)
                path += ".server.json"
            validator.save(template_server_serializer.getServerJson(message.guild), path)
    if matchesCommand("load-template_command", message):
        if not permissions('load-template_command', message):
            # Not allowed to perform commands.
            await channel.send(message.author.name + ' does not have access to this command. feelssadman :(')
            return
        args = await parseArgs("load-template_command", message)
        if type(args) == str:
            await channel.send(args)
        else:
            path = args["templateFile"]
            serverJSON = validator.load(path, "template_server_schema.json")
            await(template_server_deserializer.writeServer(message.guild, serverJSON))
            await(message.channel.send("Wrote template from: " + path + " to current server!"))

if __name__ == "__main__":
    with open("discord.key", "r") as f:
        client.run(f.readline())
