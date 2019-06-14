import discord

READY_STATUS = "Discord Bot now online!"

client = discord.Client()

@client.event
async def on_ready():
    print("Logged into discord!")
    await client.change_presence(game=discord.Game(READY_STATUS))

@client.event
async def on_message(message):
    if message.author.id == "134482734771994624":
        await client.send_message(message.author, "I love scadman!")

if __name__ == "__main__": 
    with open("discord.key", "r") as f:
        client.run(f.readline())