import utils.permission_verification as verifier
import utils.json_yaml_validator as validator
import utils.template_server_deserializer as server_loader
import utils.template_server_serializer as server_serializer
import os
import asyncio

CONFIG_FILE = "main.bot_config.json"
CONFIG_SCHEMA = "bot_config_schema.json"

client = None
config = None
commands = None

def getCommands(c):
    global commands, config, client
    if not commands:
        config = validator.load(CONFIG_FILE, CONFIG_SCHEMA)
        commands = {item['ID']: item for item in config['commands']}
        print("Loaded commands: " + str(commands.keys()))
        client = c

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
    # TODO DEFAULT ARGUMENTS
    return arguments

async def callAsyncScript(code, performedResults, action, message, args):
    exec(f'async def __ex(performedResults, action, message, args): ' +
    ''.join(f'\n {l}' for l in code.split('\n'))
    )
    return await locals()['__ex'](performedResults, action, message, args)

async def performCommand(command, message, args):
    assert client != None, "Client should exist!"
    assert type(command) == dict, "Command should be a dictionary!"
    assert type(command['actions']) == list, "Command should have actions!"
    performedResults = {}
    # try:
    for action in command['actions']:
        if "python" in action.keys():
            act = "performedResults[action['name']] = " + action['python']
            if 'loop' in action.keys() and action['loop'] != None:
                # TODO ADD LOOPING OF OTHER COMMANDS BASED OFF OF SPECIAL SYNTAX
                performedResults[action['name']] = []
                # Extra indentations to always avoid syntax errors
                act = action['loop'] + ":\n\t\t\t\tperformedResults[action['name']].append(" + action['python'] + ")"
            if 'pythonConditional' in action.keys() and action['pythonConditional'] != None:
                act = "if " + action['pythonConditional'] + ":\n\t" + act
                if 'halt' in action.keys() and action['halt']:
                    act += "\n\treturn"
        elif "nested" in action.keys():
            # Must either be a loop or an if statement
            performedResults[action['name']] = []
            act = ""
            for com in action['nested']:
                if "=" in com:
                    # HACK GOD KNOWS WHAT HAPPENS HERE
                    act += com + "\n\t"
                else:
                    act += "performedResults[action['name']].append(" + com + ")\n\t"
            if 'loop' in action.keys():
                # loop
                indent = "\t\t\t\t"
                act = action['loop'] + ":\n"
                act += indent + "temp = []\n"
                for com in action['nested']:
                    if "=" in com:
                        act += indent + com + "\n"
                    else:
                        act += indent + "temp.append(" + com + ")\n"
                act += indent + "performedResults[action['name']].append(temp)"
            if 'pythonConditional' in action.keys():
                # if statement
                act = "if " + action['pythonConditional'] + ":\n\t" + act
                if 'halt' in action.keys() and action['halt']:
                    act += "\n\treturn"
        else:
            print("COMMAND COULD NOT BE PERFORMED! NO 'python' OR 'nested' KEYS!")
            return
        print(act)
        if "await" in act:
            await callAsyncScript(act, performedResults, action, message, args)
        else:
            exec(act)
    # except Exception as e:
    #     print("COMMAND ACTION ERROR! FOR COMMAND: " + str(command['ID']))
    #     print("With action: " + action['name'])
    #     print(e)
    # No need to return anything, we perform everything via the actions anyways

async def checkAndPerformCommands(message):
    assert commands != None, "Commands should exist!"
    for c in commands.keys():
        if matchesCommand(c, message):
            if not permissions(c, message):
                if 'deniedMessage' in commands[c].keys():
                    await message.channel.send(commands[c]['deniedMessage'])
                continue
            args = None
            if commands[c]['type'] == "prefixedCommand":
                args = await parseArgs(c, message)
                if type(args) == str:
                    await message.channel.send(args)
                    continue
            await performCommand(commands[c], message, args)

def permissions(command, message):
    return verifier.verifyMacroUser(command, message.author.id, message.author.roles) and message.author.id != client.user.id
