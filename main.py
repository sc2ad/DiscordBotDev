import discord
from discord.ext import commands

@bot.command(name="My Command")
async def test(context, *, arg):
    await context.send(arg)
