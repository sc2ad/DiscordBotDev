import discord
import json
import template_server_serializer
import template_server_deserializer
import utils.json_yaml_validator as validator
import os
# import dbl
import utils.macro_verification as verifier

READY_STATUS = "Discord Bot now online!"

client = discord.Client()

def printMessage(message):
    print("Message Received from Author: (" + str(message.author) + ", " + str(message.author.id) + ") with content: " + message.content)

@client.event
async def on_ready():
    print("Logged into discord!")

@client.event
async def on_message(message):
    printMessage(message)
    channel = message.channel
    if 'hot' in message.content:
        if verifier.verifyMacroUser(message.author.id, message.author.roles):
            await channel.send('HOT STUFF IS COMING')
        else:
            await channel.send(message.author.name + ' does not have access to macros. feelssadman :(')
    if message.content.startswith('!addMacros'):
        if verifier.verifyMacroUser(message.author.id, message.author.roles):
            for user in message.mentions:
                verifier.addUser(user.id, user.name)
                await channel.send(user.name + ' was given macros! AHH THATS HOT')
            #for role in message.mention_roles:
                #verifier.addRole(role.id, role.name)
                #await channel.send(role.name + ' role now has macros! AHH THATS HOT')
        else:
            await channel.send(message.author.name + ' does not have access to macros. feelssadman :(')
    if message.content.startswith("!save-template"):
        if verifier.verifyMacroUser(message.author.id, message.author.roles):
            path = message.content.split(" ")[1]
            if not path.endswith(".server.json"):
                lst = path.split(".")
                lst = lst[:len(lst) - 1]
                path = ".".join(lst)
                path += ".server.json"
            with open(path, 'w') as fp:
                json.dump(template_server_serializer.getServerJson(message.guild), fp, indent=4)
            await message.channel.send("Saved template to file: " + path)
        else:
            await channel.send(message.author.name + ' does not have access to macros. feelssadman :(')
    if message.content.startswith("!load-template"):
        if verifier.verifyMacroUser(message.author.id, message.author.roles):
            path = message.content.split(" ")[1]
            serverJSON = validator.load(path, "template_server_schema.json")
            await(template_server_deserializer.writeServer(message.guild, serverJSON))
            await(message.channel.send("Wrote template from: " + path + " to current server!"))
        else:
            await channel.send(message.author.name + ' does not have access to macros. feelssadman :(')

if __name__ == "__main__":
    with open("discord.key", "r") as f:
        client.run(f.readline())
