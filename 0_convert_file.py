import csv
import json

csv_file = "DEL_final.csv"
json_file = "DEL_final.json"

data = []

with open(csv_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append(row)

with open(json_file, mode="w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
