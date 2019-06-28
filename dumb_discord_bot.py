import discord
# from discord.ext import commands as discord_cmds
import json
import utils.template_server_serializer as server_serializer
import utils.template_server_deserializer as server_loader
import utils.json_yaml_validator as validator
import os
import utils.permission_verification as verifier

from utils.commands import *

READY_STATUS = "Discord Bot now online!"

client = discord.Client()

def printMessage(message):
    print("Message Received from Author: (" + str(message.author) + ", " + str(message.author.id) + ") with content: " + message.content)

@client.event
async def on_ready():
    print("Logged into discord!")
    getCommands(client)

@client.event
async def on_message(message):
    printMessage(message)
    await checkAndPerformCommands(message)

if __name__ == "__main__":
    with open("discord.key", "r") as f:
        client.run(f.readline())
