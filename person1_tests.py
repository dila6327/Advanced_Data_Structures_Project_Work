# ==============================================================
#  PERSON 1: Kanan Gasimzada
#  Tests. Run them FIRST:   python3 person1_tests.py
# ==============================================================
import random
from person1_trees import BST, AVL, check_avl


print("Test 1: keys 1..7 in sorted order")
bst = BST()
avl = AVL()
for key in [1, 2, 3, 4, 5, 6, 7]:
    bst.insert(key)
    avl.insert(key)
assert bst.tree_height() == 7          # BST becomes a chain
assert avl.tree_height() == 3          # AVL stays short
assert avl.root.key == 4               # 4 is in the middle
assert avl.rotations == 4              # we counted this on paper
print("  ok: BST height 7, AVL height 3, root 4, 4 rotations")


print("Test 2: the two double-rotation cases")
avl = AVL()
for key in [3, 1, 2]:                  # Left-Right case
    avl.insert(key)
assert avl.root.key == 2 and avl.rotations == 2
avl = AVL()
for key in [1, 3, 2]:                  # Right-Left case
    avl.insert(key)
assert avl.root.key == 2 and avl.rotations == 2
print("  ok: both give root 2 after 2 rotations")


print("Test 3: random numbers, compared with Python's set")
random.seed(13)
bst = BST()
avl = AVL()
correct = set()
for i in range(500):
    key = random.randint(0, 999)
    bst.insert(key)
    avl.insert(key)
    correct.add(key)
for key in range(1000):
    assert bst.search(key) == (key in correct)
    assert avl.search(key) == (key in correct)
assert check_avl(avl.root)
print("  ok: same answers as Python set, AVL is valid")


print("Test 4: many sorted keys")
bst = BST()
for key in range(2000):
    bst.insert(key)
assert bst.tree_height() == 2000       # deeper than Python's recursion limit (1000)
avl = AVL()
for key in range(100000):
    avl.insert(key)
assert avl.tree_height() == 17
assert check_avl(avl.root)
print("  ok: BST height 2000 with no crash, AVL with 100000 keys has height 17")

print("\nALL TESTS PASSED")
