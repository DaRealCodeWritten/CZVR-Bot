def return_auth():
    foo = {}
    with open("auth.config") as config:
        for line in config:
            line = line.strip("\n")
            data = line.split(":", 1)
            foo[data[0]] = data[1]
    return foo


def return_guild():
    guild = {}
    roles = {}
    validated = False
    frame = 1
    with open("guild.config") as file:
        for line in file:
            line = line.strip("\n")
            kv = line.split(":")
            if not validated and frame >= 2:
                raise KeyError("Missing key GUILD_SETTING in guild settings")
            if kv[0] == "GUILD_SETTING":
                guild[kv[0]] = kv[1]
                validated = True
            if kv[0].startswith(f"GUILD_{guild['GUILD_SETTING']}_RATING"):
                roles[int(kv[0].split("_")[3])] = int(kv[1])
            else:
                guild[kv[0]] = kv[1]
            frame += 1
    guild["GUILD_ROLES"] = roles
    return guild
