import discord
import dbl

READY_STATUS = "Discord Bot now online!"

client = discord.Client()

@client.event
async def on_ready():
    print("Logged into discord!")

@client.event
async def on_message(message):
    print(message.content)
    if 'hot' in message.content:
        channel = message.channel
        await channel.send('HOT STUFF IS COMING')

if __name__ == "__main__":
    with open("discord.key", "r") as f:
        client.run(f.readline())
