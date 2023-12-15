import json
import os

if os.name == "nt":
    path = os.sep.join(["C:", "users", "Andrei", "vault.json"])
elif os.name == "posix":
    path = os.sep.join(
        ["/", "home", "menajerulrobotilor", "key", "vault.json"])

# open file
f = open(path)
# load it as json
j = json.load(f)

KEY_BOT = str(j["lord_skillet"]["key"])
