import discord

def getPermissionJson(name, value):
    return {
        "permissionName": name,
        "allow": value
    }

def getCategoryJson(category):
    return {
        "name": category.name,
        "type": str(category.type),
        "nsfw": category.is_nsfw(),
        "permissions": [getChannelPermissionJson(role, category.overwrites[role]) for role in category.overwrites.keys()]
    }

def getChannelPermissionJson(role, perms):
    return {
        "roleName": role.name,
        "permissions": [getPermissionJson(perm, value) for (perm, value) in iter(perms) if value != None]
    }

def getRoleJson(role):
    assert type(role) == discord.Role
    permissions = role.permissions
    return {
        "name": role.name,
        "permissions": [getPermissionJson(perm, value) for (perm, value) in iter(role.permissions)],
        "settings": {
            "color": list(role.color.to_rgb()),
            "mention": role.mentionable,
            "displaySeparate": role.hoist
        }
    }

def getTextChannelJson(text_channel):
    assert type(text_channel) == discord.TextChannel
    return {
        "name": text_channel.name,
        "topic": text_channel.topic,
        "position": text_channel.position,
        "nsfw": text_channel.is_nsfw(),
        "slowmode_delay": text_channel.slowmode_delay,
        "permissions": [getChannelPermissionJson(role, text_channel.overwrites[role]) for role in text_channel.overwrites.keys()],
        "categoryName": text_channel.category.name if text_channel.category else None
    }

def getVoiceChannelJson(voice_channel):
    assert type(voice_channel) == discord.VoiceChannel
    return {
        "name": voice_channel.name,
        "position": voice_channel.position,
        "bitrate": voice_channel.bitrate,
        "user_limit": voice_channel.user_limit,
        "permissions": [getChannelPermissionJson(role, voice_channel.overwrites[role]) for role in voice_channel.overwrites.keys()],
        "categoryName": voice_channel.category.name if voice_channel.category else None
    }

def getServerJson(server):
    """
    Converts the given server into a template JSON following the template_server_schema.json format.
    """
    assert type(server) == discord.Guild, "server must be discord.Guild, not: " + str(type(server))
    d = {}
    d['serverName'] = server.name
    d['roles'] = []
    for r in server.roles:
        d['roles'].append(getRoleJson(r))
    d['categories'] = []
    for c in server.categories:
        d['categories'].append(getCategoryJson(c))
    d['textChannels'] = []
    for t in server.text_channels:
        d['textChannels'].append(getTextChannelJson(t))
    d['voiceChannels'] = []
    for v in server.voice_channels:
        d['voiceChannels'].append(getVoiceChannelJson(v))
    return d
