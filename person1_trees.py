# ==============================================================
#  PERSON 1: Kanan Gasimzada
#  Two search trees: a plain BST and an AVL tree.
# ==============================================================


# --------------------------------------------------------------
# A NODE is one box of the tree.
# --------------------------------------------------------------
class Node:
    def __init__(self, key):
        self.key = key        # the number we store
        self.left = None      # child with a smaller key
        self.right = None     # child with a bigger key
        self.height = 1       # only the AVL tree uses this


# --------------------------------------------------------------
# PLAIN BST
# We walk down with a while loop (no recursion), because a BST
# can become a very long chain and recursion would crash.
# --------------------------------------------------------------
class BST:
    def __init__(self):
        self.root = None
        self.steps = 0        # how many nodes we looked at
        self.max_depth = 0    # the height of the tree

    def insert(self, key):
        new_node = Node(key)

        # empty tree: the new node is the root
        if self.root is None:
            self.root = new_node
            self.max_depth = 1
            return

        current = self.root
        depth = 1
        while True:
            self.steps += 1
            if key == current.key:          # already in the tree
                return
            if key < current.key:           # go left
                if current.left is None:
                    current.left = new_node
                    break
                current = current.left
            else:                           # go right
                if current.right is None:
                    current.right = new_node
                    break
                current = current.right
            depth += 1

        # the new node is one level below "current"
        if depth + 1 > self.max_depth:
            self.max_depth = depth + 1

    def search(self, key):
        current = self.root
        while current is not None:
            self.steps += 1
            if key == current.key:
                return True
            if key < current.key:
                current = current.left
            else:
                current = current.right
        return False

    def tree_height(self):
        return self.max_depth


# --------------------------------------------------------------
# AVL TREE helpers
# --------------------------------------------------------------
def get_height(node):
    if node is None:
        return 0
    return node.height


def update_height(node):
    node.height = 1 + max(get_height(node.left), get_height(node.right))


def get_balance(node):
    # left height minus right height; AVL allows only -1, 0 or 1
    return get_height(node.left) - get_height(node.right)


def rotate_right(y):
    x = y.left
    y.left = x.right
    x.right = y
    update_height(y)
    update_height(x)
    return x                  # x is the new top of this part


def rotate_left(x):
    y = x.right
    x.right = y.left
    y.left = x
    update_height(x)
    update_height(y)
    return y                  # y is the new top of this part


# --------------------------------------------------------------
# AVL TREE
# Insert like a BST, then fix the balance on the way back up.
# Recursion is fine here: an AVL tree is always short.
# --------------------------------------------------------------
class AVL:
    def __init__(self):
        self.root = None
        self.steps = 0
        self.rotations = 0

    def insert(self, key):
        self.root = self.insert_at(self.root, key)

    def insert_at(self, node, key):
        # 1) normal BST insert
        if node is None:
            return Node(key)
        self.steps += 1
        if key == node.key:
            return node
        if key < node.key:
            node.left = self.insert_at(node.left, key)
        else:
            node.right = self.insert_at(node.right, key)

        # 2) new height of this node
        update_height(node)

        # 3) fix the balance if needed (4 cases)
        balance = get_balance(node)

        if balance > 1 and key < node.left.key:       # Left-Left
            self.rotations += 1
            return rotate_right(node)

        if balance < -1 and key > node.right.key:     # Right-Right
            self.rotations += 1
            return rotate_left(node)

        if balance > 1 and key > node.left.key:       # Left-Right
            self.rotations += 2
            node.left = rotate_left(node.left)
            return rotate_right(node)

        if balance < -1 and key < node.right.key:     # Right-Left
            self.rotations += 2
            node.right = rotate_right(node.right)
            return rotate_left(node)

        return node

    def search(self, key):
        current = self.root
        while current is not None:
            self.steps += 1
            if key == current.key:
                return True
            if key < current.key:
                current = current.left
            else:
                current = current.right
        return False

    def tree_height(self):
        return get_height(self.root)


# --------------------------------------------------------------
# CHECK: is this a correct AVL tree?
#   - every key is in the right place (smaller left, bigger right)
#   - every stored height is correct
#   - every balance is -1, 0 or 1
# --------------------------------------------------------------
def check_avl(node, low=None, high=None):
    if node is None:
        return True
    if low is not None and node.key <= low:
        return False
    if high is not None and node.key >= high:
        return False
    if node.height != 1 + max(get_height(node.left), get_height(node.right)):
        return False
    if abs(get_balance(node)) > 1:
        return False
    return check_avl(node.left, low, node.key) and check_avl(node.right, node.key, high)
