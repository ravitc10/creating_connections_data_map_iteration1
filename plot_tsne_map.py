import json
import matplotlib.pyplot as plt
from pathlib import Path


# =========================
# CONFIG
# =========================
INPUT_COORDS = Path("comments_1_tsne.json")
OUTPUT_PNG = Path("comments_1_tsne_map.png")

FIGSIZE = (12, 9)
POINT_SIZE = 40
LABEL_EVERY_N = 2
ALPHA = 0.75


# =========================
# LOAD COORDS
# =========================
if not INPUT_COORDS.exists():
    raise FileNotFoundError(f"Could not find {INPUT_COORDS.resolve()}")

with open(INPUT_COORDS, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list) or len(data) == 0:
    raise ValueError("Coordinate file is empty or malformed")

xs = [d["x"] for d in data]
ys = [d["y"] for d in data]

names = [d.get("name", "") for d in data]

labels = [
    d.get("label")
    or f"{d.get('name','')}: {d.get('comment','')[:50]}..."
    for d in data
]

print(f"Loaded {len(xs)} points")


# =========================
# COLOR BY SPEAKER
# =========================
unique_names = sorted(set(names))
name_to_idx = {name: i for i, name in enumerate(unique_names)}

colors = [name_to_idx[name] for name in names]


# =========================
# PLOT
# =========================
plt.figure(figsize=FIGSIZE)

scatter = plt.scatter(xs, ys, s=POINT_SIZE, alpha=ALPHA, c=colors)

# Label subset
for i, label in enumerate(labels):
    if LABEL_EVERY_N > 0 and i % LABEL_EVERY_N != 0:
        continue
    if not label:
        continue
    plt.text(xs[i], ys[i], label, fontsize=8, alpha=0.8)

plt.title("Discussion Comments — t-SNE Map (Colored by Speaker)")
plt.xlabel("t-SNE dimension 1")
plt.ylabel("t-SNE dimension 2")


# =========================
# LEGEND (Speaker Names)
# =========================
# Create a legend manually
handles = []
for name, idx in name_to_idx.items():
    handles.append(
        plt.Line2D(
            [], [], marker='o', linestyle='',
            label=name,
            markersize=6,
            alpha=ALPHA
        )
    )

plt.legend(handles=handles, title="Speaker", bbox_to_anchor=(1.05, 1), loc='upper left')


plt.tight_layout()
plt.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight")
plt.show()

print(f"Saved plot → {OUTPUT_PNG.resolve()}")
