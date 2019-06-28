import discord

def getPermissions(permissionsList, cl=discord.Permissions):
    assert type(permissionsList) == list
    perm = cl()
    d = {}
    for item in permissionsList:
        d[item['permissionName']] = item['allow']
    perm.update(**d)
    return perm

def getRolePermissions(perms):
    return getPermissions(perms, cl=discord.Permissions)

def getChannelPermissions(guild, perms):
    d = {}
    for item in perms:
        for r in guild.roles:
            if r.name == item['roleName']:
                d[r] = getPermissions(item['permissions'], discord.PermissionOverwrite)
    return d

def getCategory(guild, name):
    for c in guild.categories:
        if c.name == name:
            return c

async def writeRole(guild, roleJSON):
    assert type(guild) == discord.Guild
    assert type(roleJSON) == dict

    for r in guild.roles:
        if r.name == roleJSON['name']:
            try:
                await(r.edit(colour=discord.Color.from_rgb(*tuple(roleJSON['settings']['color'])), hoist=roleJSON['settings']['displaySeparate'], \
                    mentionable=roleJSON['settings']['mention'], permissions=getRolePermissions(roleJSON['permissions'])))
            except discord.Forbidden:
                print("Cannot modify role: " + roleJSON['name'] + " due to insufficient permissions!")
            return
    
    await(guild.create_role(name=roleJSON['name'], colour=discord.Color.from_rgb(*tuple(roleJSON['settings']['color'])), \
        hoist=roleJSON['settings']['displaySeparate'], mentionable=roleJSON['settings']['mention'], \
            permissions=getRolePermissions(roleJSON['permissions']), reason="Creating from template"))

async def writeCategory(guild, categoryJSON):
    assert type(guild) == discord.Guild
    assert type(categoryJSON) == dict

    for c in guild.categories:
        if c.name == categoryJSON['name']:
            try:
                await(c.edit(nsfw=categoryJSON['nsfw'], reason="Modifying from template"))
                d = getChannelPermissions(guild, categoryJSON['permissions'])
                for person in d.keys():
                    await(c.set_permissions(person, overwrite=d[person], reason="Modifying from template"))
            except discord.Forbidden:
                print("Cannot modify category: " + categoryJSON['name'] + " due to insufficient permissions!")
            return
            
    await(guild.create_category(categoryJSON['name'], overwrites=getChannelPermissions(guild, categoryJSON['permissions']), \
        reason="Creating from template"))
    for c in guild.categories:
        if c.name == categoryJSON['name']:
            await(c.edit(nsfw=categoryJSON['nsfw'], reason="Modifying from template"))

async def writeTextChannel(guild, textJSON):
    assert type(guild) == discord.Guild
    assert type(textJSON) == dict

    for t in guild.text_channels:
        if t.name == textJSON['name']:
            try:
                await(t.edit(name=textJSON['name'], topic=textJSON['topic'], position=textJSON['position'], \
                    nsfw=textJSON['nsfw'], category=getCategory(guild, textJSON['categoryName'])))
                d = getChannelPermissions(guild, textJSON['permissions'])
                for person in d.keys():
                    await(t.set_permissions(person, overwrite=d[person], reason="Modifying from template"))
                return
            except discord.Forbidden:
                print("Cannot modify text channel: " + textJSON['name'] + " due to insufficient permissions!")
    
    await(guild.create_text_channel(textJSON['name'], overwrites=getChannelPermissions(guild, textJSON['permissions']), \
            reason="Creating from template"))
    for t in guild.text_channels:
        if t.name == textJSON['name']:
            await(t.edit(name=textJSON['name'], topic=textJSON['topic'], position=textJSON['position'], \
                nsfw=textJSON['nsfw'], category=getCategory(guild, textJSON['categoryName'])))

async def writeVoiceChannel(guild, voiceJSON):
    assert type(guild) == discord.Guild
    assert type(voiceJSON) == dict

    for v in guild.voice_channels:
        try:
            if v.name == voiceJSON['name']:
                await(v.edit(name=voiceJSON['name'], bitrate=voiceJSON['bitrate'], position=voiceJSON['position'], \
                    user_limit=voiceJSON['user_limit'], category=getCategory(guild, voiceJSON['categoryName'])))
                d = getChannelPermissions(guild, voiceJSON['permissions'])
                for person in d.keys():
                    await(v.set_permissions(person, overwrite=d[person], reason="Modifying from template"))
                return
        except discord.Forbidden:
            print("Cannot modify voice channel: " + voiceJSON['name'] + " due to insufficient permissions!")
    
    await(guild.create_voice_channel(voiceJSON['name'], overwrites=getChannelPermissions(guild, voiceJSON['permissions']), \
            reason="Creating from template"))
    for v in guild.voice_channels:
        if v.name == voiceJSON['name']:
            await(v.edit(name=voiceJSON['name'], bitrate=voiceJSON['bitrate'], position=voiceJSON['position'], \
                user_limit=voiceJSON['user_limit'], category=getCategory(guild, voiceJSON['categoryName'])))

async def writeServer(guild, serverJSON):
    """
    Updates the server to follow the given template JSON
    """
    assert type(guild) == discord.Guild, "server must be discord.Guild, not: " + str(type(guild))
    assert type(serverJSON) == dict

    await(guild.edit(name=serverJSON['serverName']))
    for r in serverJSON['roles']:
        await(writeRole(guild, r))
    # cats = sorted(serverJSON['categories'], key=lambda x: x['position'])
    for c in serverJSON['categories'][::-1]:
        await(writeCategory(guild, c))
    for t in serverJSON['textChannels']:
        await(writeTextChannel(guild, t))
    for v in serverJSON['voiceChannels']:
        await(writeVoiceChannel(guild, v))
