import requests
import json

data = {"claim": "1 gram of fentanyl is lethal", "num_articles":1}
r = requests.post("http://localhost:5000/", json=data)

print(r.status_code)
print(type(r.content))
print(r.content)
rr = r.json()
# rr = rr[8:len(rr)-4]
print(rr)
# print(type(rr))

print()


print("done")