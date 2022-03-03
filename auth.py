def return_auth():
    foo = {}
    with open("auth.config") as config:
        for line in config:
            line = line.strip("\n")
            data = line.split(":")
            foo[data[0]] = data[1]
    return foo