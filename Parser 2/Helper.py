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


class ItemSet:
    def __init__(self):
        self.items = []


class TreeBuilder:
    def __init__(self):
        self.root = ''


class TreeNode:
    def __init__(self, name):
        self.token = None
        self.type = ''
        self.val = ''
        self.name = name
        self.symbol = None
        self.parent = None
        self.children = None

    @staticmethod
    def search(root):
        queue = [root]
        while len(queue) != 0:
            head = queue[0]
            print(head.name)
            queue.pop(0)
            if head.children is not None:
                for child in head.children:
                    queue.append(child)

class Analyzer:
    pass


# 为每个非终结符编写动作函数，在归约时调用
class SemanticActions:
    def handle(self, stack):
        pass


class Act1(SemanticActions):

    def handle(self, stack):
        print("val is", stack[-1])


class Act2(SemanticActions):

    def handle(self, stack):
        val = int(stack[-1]) + int(stack[-2])
        stack.pop(-1)
        stack.pop(-1)
        stack.append(val)


class Act3(SemanticActions):

    def handle(self, stack):
        pass


class Act4(SemanticActions):

    def handle(self, stack):
        val = int(stack[-1]) * int(stack[-2])
        stack.pop(-1)
        stack.pop(-1)
        stack.append(val)


class Act5(SemanticActions):

    def handle(self, stack):
        pass

class SemanticHandler():
    def __init__(self):
        self.actionMapper = {1: Act1(), 2: Act2(), 3: Act3(), 4: Act4()}
    """ 根据传入的符号，调用对应的action """
    def handle(self, index, stack):
        if index not in self.actionMapper.keys():
            return
        action = self.actionMapper[index]
        action.handle(stack)


class Symbol:
    def __init__(self):
        self.attr = {}