import discord
import dbl
import utils.macro_verification as verifier

READY_STATUS = "Discord Bot now online!"

client = discord.Client()

@client.event
async def on_ready():
    print("Logged into discord!")

@client.event
async def on_message(message):
    print(message.content)
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

if __name__ == "__main__":
    with open("discord.key", "r") as f:
        client.run(f.readline())
