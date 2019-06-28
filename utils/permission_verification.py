import utils.json_yaml_validator as loader
import os

PERMISISON_DATA = None
PERMISSION_FILE = "main.permissions.json"
PERMISSION_SCHEMA = "command_permissions_schema.json"

def addUser(userId, userName, commands):
    data = getData()

    data['users'].append({
        'name': userName,
        'id': userId,
        'commands': commands
    })
    loader.save(data, PERMISSION_FILE)

def getUser(userID):
    data = getData()
    for u in data['users']:
        if u['id'] == userID:
            return u
    return None

def getRole(roleID):
    data = getData()
    for r in data['roles']:
        if r['id'] == roleID:
            return r
    return None

def addCommandToUser(commandID, userID, allow=True):
    data = getData()
    user = getUser(userID)
    if not user:
        return
    for c in user['commands']:
        if c['ID'] == commandID:
            c['allow'] = allow
            loader.save(data, PERMISSION_FILE)
            return
    user['commands'].append({
        "ID": commandID,
        "allow": allow
    })
    loader.save(data, PERMISSION_FILE)

def addRole(roleId, roleName, commands):
    data = getData()
    data['roles'].append({
        'name': roleName,
        'id': roleId,
        'commands': commands
    })
    loader.save(data, PERMISSION_FILE)

def getData():
    global PERMISISON_DATA
    if not PERMISISON_DATA:
        if not os.path.exists(PERMISSION_FILE):
            PERMISISON_DATA = {}
        else:
            PERMISISON_DATA = loader.load(PERMISSION_FILE, PERMISSION_SCHEMA)
    return PERMISISON_DATA

def verifyMacroUser(command, messageUserId, messageRoles=None):
    data = getData()
    user = getUser(messageUserId)
    if user:
        for c in user['commands']:
            if c['ID'] == command:
                return c['allow']
        # User exists but doesn't have permission for this command
    if not messageRoles:
        return False
    for messageRole in messageRoles:
        role = getRole(messageRole)
        if role:
            for c in role['commands']:
                if c['ID'] == command:
                    return c['allow']
            # Role exists, but this command is not permitted
    return False
    