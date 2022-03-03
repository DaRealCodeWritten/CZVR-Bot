def return_auth():
    foo = {}
    with open("auth.config") as config:
        for line in config:
            data = line.split(":")
            foo[data[0]] = data[1]
    return foo