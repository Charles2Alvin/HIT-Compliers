class Entry:
    def __init__(self, state, symbol, action=None, **content):
        self.state = state
        self.symbol = symbol
        self.action = action
        self.content = content

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.state == other.state and self.symbol == other.symbol
        else:
            return False


class Production:
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.index = 0      # 产生式的编号

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.left == other.left and self.right == other.right
        else:
            return False


class Item:
    def __init__(self, left, right, lookahead):
        self.left = left
        self.right = right
        self.lookahead = lookahead

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.left == other.left and self.right == other.right and self.lookahead == other.lookahead
        else:
            return False

    def __str__(self):
        return self.left + " " + self.right + " " + self.lookahead


















