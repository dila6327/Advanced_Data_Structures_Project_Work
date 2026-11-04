# ==============================================================
#  PERSON 2: Dilruba Guliyeva
#  Pictures from results.csv.   Run AFTER person2_experiment.py
#  Needs matplotlib:  pip3 install matplotlib
# ==============================================================
import matplotlib.pyplot as plt

# read the results file into a list of rows
rows = []
file = open("results.csv")
header = file.readline().strip().split(",")
for line in file:
    values = line.strip().split(",")
    rows.append(dict(zip(header, values)))
file.close()

# ---------- picture 1: tree heights on the full graph ----------
full = [r for r in rows if r["edges"] == "13838"]
orders = [r["order"] for r in full if r["tree"] == "BST"]
bst_heights = [int(r["max_height"]) for r in full if r["tree"] == "BST"]
avl_heights = [int(r["max_height"]) for r in full if r["tree"] == "AVL"]

positions = range(len(orders))
plt.figure(figsize=(8, 4))
plt.bar([p - 0.2 for p in positions], bst_heights, width=0.4, label="BST", color="#B4531B")
plt.bar([p + 0.2 for p in positions], avl_heights, width=0.4, label="AVL", color="#2266A0")
plt.xticks(list(positions), orders, rotation=20)
plt.ylabel("tallest tree (levels)")
plt.title("Tree height for each arrival order (13,838 edges)")
plt.legend()
plt.tight_layout()
plt.savefig("heights.png", dpi=150)

# ---------- picture 2: BST time / AVL time ----------
plt.figure(figsize=(7, 4.5))
for size, style in [("3459", ":"), ("6919", "--"), ("13838", "-")]:
    points = []
    for r in rows:
        if r["edges"] == size and r["tree"] == "BST":
            avl = [x for x in rows if x["edges"] == size and x["order"] == r["order"] and x["tree"] == "AVL"][0]
            points.append((float(r["sortedness"]), float(r["total_ms"]) / float(avl["total_ms"]), r["order"]))
    points.sort()
    plt.plot([p[0] for p in points], [p[1] for p in points], style, marker="o", color="black", label=size + " edges")
    for p in points:
        if p[2] == "real":
            plt.plot(p[0], p[1], "*", markersize=15, color="green")
plt.plot([], [], "*", markersize=15, color="green", label="real order")
plt.axhline(1, color="grey")
plt.xlabel("sortedness (0 = sorted, 0.5 = random)")
plt.ylabel("BST time / AVL time")
plt.title("Above 1 = AVL is faster")
plt.legend()
plt.tight_layout()
plt.savefig("time_ratio.png", dpi=150)

print("Saved: heights.png, time_ratio.png")
