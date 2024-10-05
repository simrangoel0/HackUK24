import requests
import json

data = {"claim": "1 gram of fentanyl is lethal"}
r = requests.post("http://localhost:5000/", json=data)

print(r.status_code)
print(type(r.content))
print(r.content)
rr = r.json()
print(rr)


print("done")