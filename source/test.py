import json

with open("Data/dataset.json",'r') as f:
    dataset = json.load(f)

wrong_ids = []
copy = dataset.copy()

print(copy.keys())
for i in range(len(dataset["playlist"])-1,-1,-1):
    if len(copy["playlist"][i]) > 10:
        print(True)
        copy["playlist"].pop(i)
        copy["clf"].pop(i)

print('---------------------------')
print(len(copy["playlist"]))
print("---------------------------------------")

for c in copy["playlist"]:
    if len(c) > 10:
        print(True)

dataset = copy.copy()
with open("Data/dataset.json",'w') as f:
    json.dump(dataset,f,indent=4)