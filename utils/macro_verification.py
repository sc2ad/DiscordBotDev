import json

def addUser(userId, userName):
    if verifyMacroUser(userId, 124234):
        return
    with open('macroAccess.json', 'r') as access:
        data = json.load(access)
    data['users'].append({
        'name': userName,
        'id': userId
    })
    with open('macroAccess.json', 'w') as outfile:
        json.dump(data, outfile)

def addRole(roleId, roleName):
    with open('macroAccess.json', 'r') as access:
        data = json.load(access)
    data['roles'].append({
        'name': roleName,
        'id': roleId
    })
    with open('macroAccess.json', 'w') as outfile:
        json.dump(data, outfile)

def verifyMacroUser(messageUserId, messageRoles):
    with open('macroAccess.json', 'r') as access:
        data = json.load(access)
    for user in data['users']:
        if user.get('id') == messageUserId:
            return True
    for role in data['roles']:
        for messageRole in messageRoles:
            if role.get('id') == messageRole:
                return True
    return False
    