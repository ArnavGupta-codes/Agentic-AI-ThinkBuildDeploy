import json

data = {"name": "Arihant", "id": 7}
with open("file_handling/data.json", "w") as f:
    json.dump(data, f)

with open("file_handling/data.json", "r") as f:
    new_data = json.load(f)
    print(new_data)

f = open("file_handling/data.json", "r")
blah = json.load(f)
print(blah)
f.close()