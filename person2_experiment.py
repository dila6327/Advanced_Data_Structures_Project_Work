# ==============================================================
#  PERSON 2: Dilruba Guliyeva
#  The real graph and the experiment.
#  Run:   python3 person2_experiment.py
# ==============================================================
import gzip
import random
import statistics
import time

from person1_trees import BST, AVL

DATA_FILE = "data/collegemsg.csv.gz"
REPEATS = 3                      # timed runs per tree; we keep the middle one (median)


# --------------------------------------------------------------
# STEP 1: read the real graph
# Each line of the file: sender, receiver, time.
# An edge = the FIRST message between two students.
# --------------------------------------------------------------
def load_edges():
    edges = []
    seen = set()
    file = gzip.open(DATA_FILE, "rt")
    file.readline()                          # skip the header line
    for line in file:
        parts = line.strip().split(",")
        u = int(parts[0])
        v = int(parts[1])
        if u == v:                           # a message to yourself is not an edge
            continue
        if u > v:                            # (7, 3) and (3, 7) are the same edge
            u, v = v, u
        if (u, v) not in seen:               # keep only the first message
            seen.add((u, v))
            edges.append((u, v))
    file.close()
    return edges                             # already in time order


# --------------------------------------------------------------
# STEP 2: four arrival orders
# --------------------------------------------------------------
def nearly_sorted(edges, share):
    result = sorted(edges)
    random.seed(1)
    swaps = int(share * len(result))
    for k in range(swaps):                   # swap a few random pairs
        i = random.randrange(len(result))
        j = random.randrange(len(result))
        result[i], result[j] = result[j], result[i]
    return result


def make_orders(edges):
    random_order = list(edges)
    random.seed(1)
    random.shuffle(random_order)
    return {
        "real": edges,
        "sorted": sorted(edges),
        "nearly sorted 5%": nearly_sorted(edges, 0.05),
        "nearly sorted 20%": nearly_sorted(edges, 0.20),
        "random": random_order,
    }


# --------------------------------------------------------------
# STEP 3: how sorted is an order?
# For every student we look at the order in which their friends
# arrive. A "wrong pair" = a bigger number before a smaller one.
#   sortedness = wrong pairs / all pairs
#   0 = perfectly sorted, 0.5 = random
# --------------------------------------------------------------
def sortedness(order):
    arrivals = {}
    for u, v in order:
        arrivals.setdefault(u, []).append(v)
        arrivals.setdefault(v, []).append(u)
    wrong = 0
    total = 0
    for friends in arrivals.values():
        for i in range(len(friends)):
            for j in range(i + 1, len(friends)):
                total += 1
                if friends[i] > friends[j]:
                    wrong += 1
    return wrong / total


# --------------------------------------------------------------
# STEP 4: build the adjacency structure
# adj[u] is the tree that holds all friends of student u.
# --------------------------------------------------------------
def build(order, TreeClass):
    adj = {}
    for u, v in order:
        if u not in adj:
            adj[u] = TreeClass()
        if v not in adj:
            adj[v] = TreeClass()
        adj[u].insert(v)
        adj[v].insert(u)
    return adj


# --------------------------------------------------------------
# STEP 5: the graph algorithm = counting triangles
# For every edge (u, v) and every friend w of u we ask the tree:
# "is v also a friend of w?"  If yes: u, v, w is a triangle.
# Every triangle is found 3 times.
# --------------------------------------------------------------
def friend_lists(edges):
    friends = {}
    for u, v in edges:
        friends.setdefault(u, []).append(v)
        friends.setdefault(v, []).append(u)
    return friends


def count_triangles(adj, edges, friends):
    found = 0
    for u, v in edges:
        for w in friends[u]:
            if w != v and adj[v].search(w):
                found += 1
    return found // 3


def count_triangles_with_sets(edges, friends):
    # a second, independent way (only Python sets) to check our answer
    found = 0
    for u, v in edges:
        found += len(set(friends[u]) & set(friends[v]))
    return found // 3


# --------------------------------------------------------------
# STEP 6: measure one tree type on one order
# --------------------------------------------------------------
def measure(order, TreeClass, edges, friends, correct_triangles):
    # warm-up run (not timed) + correctness check
    adj = build(order, TreeClass)
    assert count_triangles(adj, edges, friends) == correct_triangles

    build_times = []
    query_times = []
    for r in range(REPEATS):
        start = time.perf_counter()
        adj = build(order, TreeClass)
        middle = time.perf_counter()
        count_triangles(adj, edges, friends)
        end = time.perf_counter()
        build_times.append(middle - start)
        query_times.append(end - middle)

    # numbers from one extra run, with the step counters
    adj = build(order, TreeClass)
    build_steps = sum(tree.steps for tree in adj.values())
    count_triangles(adj, edges, friends)
    all_steps = sum(tree.steps for tree in adj.values())
    questions = sum(len(friends[u]) - 1 for u, v in edges)
    rotations = 0
    if TreeClass == AVL:
        rotations = sum(tree.rotations for tree in adj.values())

    return {
        "max height": max(tree.tree_height() for tree in adj.values()),
        "steps per question": (all_steps - build_steps) / questions,
        "rotations": rotations,
        "build ms": statistics.median(build_times) * 1000,
        "query ms": statistics.median(query_times) * 1000,
        "total ms": (statistics.median(build_times) + statistics.median(query_times)) * 1000,
    }


# --------------------------------------------------------------
# STEP 7: the main experiment
# --------------------------------------------------------------
def main():
    all_edges = load_edges()
    print("Real graph:", len(all_edges), "edges")

    out = open("results.csv", "w")
    out.write("edges,order,sortedness,tree,max_height,steps_per_question,rotations,build_ms,query_ms,total_ms\n")

    for share in [0.25, 0.50, 1.00]:
        edges = all_edges[: int(share * len(all_edges))]      # the first part, in time order
        friends = friend_lists(edges)
        correct = count_triangles_with_sets(edges, friends)
        print("\n===", len(edges), "edges,", correct, "triangles ===")
        print(f"{'order':20s} {'sorted':>6s} {'height BST/AVL':>15s} {'steps BST/AVL':>14s} {'time BST/AVL (ms)':>18s} {'BST/AVL':>8s}")

        for name, order in make_orders(edges).items():
            s = sortedness(order)
            b = measure(order, BST, edges, friends, correct)
            a = measure(order, AVL, edges, friends, correct)
            ratio = b["total ms"] / a["total ms"]
            print(f"{name:20s} {s:6.2f} {b['max height']:7d} / {a['max height']:<5d} "
                  f"{b['steps per question']:6.1f} / {a['steps per question']:<5.1f} "
                  f"{b['total ms']:8.0f} / {a['total ms']:<7.0f} {ratio:8.2f}")
            for tree_name, r in [("BST", b), ("AVL", a)]:
                out.write(f"{len(edges)},{name},{s:.3f},{tree_name},{r['max height']},"
                          f"{r['steps per question']:.2f},{r['rotations']},{r['build ms']:.1f},"
                          f"{r['query ms']:.1f},{r['total ms']:.1f}\n")
    out.close()
    print("\nSaved: results.csv   (BST/AVL above 1 = AVL is faster)")


# --------------------------------------------------------------
# STEP 8: sorted keys into ONE tree (the worst case)
# --------------------------------------------------------------
def sorted_keys_test():
    print("\n=== sorted keys 0, 1, 2, ... into one tree ===")
    last_time = 0
    for n in [1000, 2000, 4000, 8000, 16000, 100000]:
        if n == 100000:
            guess = last_time * (n / 16000) ** 2     # BST time grows like n * n
            print(f"BST n={n:6d}: not run, would take about {guess:.0f} s (over our 60 s limit = TIMEOUT)")
        else:
            tree = BST()
            start = time.perf_counter()
            for key in range(n):
                tree.insert(key)
            last_time = time.perf_counter() - start
            print(f"BST n={n:6d}: {last_time:7.3f} s, height {tree.tree_height()}")
        tree = AVL()
        start = time.perf_counter()
        for key in range(n):
            tree.insert(key)
        print(f"AVL n={n:6d}: {time.perf_counter() - start:7.3f} s, height {tree.tree_height()}")


main()
sorted_keys_test()
