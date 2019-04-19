class Entry():
    def __init__(self, state, symbol, content):
        self.state = state
        self.symbol = symbol
        self.content = content


class Production():
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.index = 0      # 产生式的编号


class Item():
    def __init__(self, left, right, lookahead):
        self.left = left
        self.right = right
        self.lookahead = lookahead


class ItemSet():
    def __init__(self):
        self.items = []