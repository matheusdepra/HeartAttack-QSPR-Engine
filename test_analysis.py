import requests

res = requests.post("http://127.0.0.1:8000/api/analyses", json={
    "name": "Test Report",
    "description": "testing",
    "drug_ids": [1, 2, 3, 4, 5, 6, 7]
})
aid = res.json()["id"]
print("Created analysis", aid)
res = requests.post(f"http://127.0.0.1:8000/api/analyses/{aid}/run")
print("Run result:", res.status_code)
if res.status_code != 200:
    print(res.text)
report = requests.get(f"http://127.0.0.1:8000/api/analyses/{aid}/report")
print("Report characters:", len(report.json()["content"]))
