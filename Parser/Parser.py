from Grammar import *
from Lexer import *
import time

class Parser():
    """ SLR语法分析器 """
    def __init__(self):
        self.startSym = ''
        self.productions = []
        self.firstSet = {}
        self.followSet = {}
        self.terminals = []
        self.nonterminals = []
        self.states = []        # 自动机的所有状态，每个状态都是一个项目集
        self.table = []
        self.actionTable = []
        self.gotoTable = []

    def buildStates(self):
        startState = ItemSet()
        startState.items.append(Item(self.startSym + "'", ['.', self.startSym], '$'))
        startState = self.closure(startState)
        states = [startState]
        flag = True
        while flag:
            flag = False
            for state in states:
                for symbol in self.nonterminals + self.terminals:
                    newSet = self.goto(state, symbol)
                    if len(newSet.items) == 0:      # 当前状态对该符号没有转移路线
                        continue
                    exist = False                   # 以下检测新状态是否已存在
                    for each in states:
                        if self.equalState(each, newSet):
                            exist = True
                            break
                    if not exist:
                        states.append(newSet)       # 不存在则加入集合中
                        flag = True
        self.states = states

    def equalState(self, s1, s2):           # 判断两个状态（项目集）是否完全相同（包含完全相同的项目）
        length1, length2 = len(s1.items), len(s2.items)
        if length1 != length2:
            return False
        for i in range(length1):
            if s1.items[i].left == s2.items[i].left \
                    and s1.items[i].right == s2.items[i].right \
                    and s1.items[i].lookahead == s2.items[i].lookahead:
                continue
            else:
                return False
        return True

    def closure(self, itemset):             # 求出给定项目集（状态）的闭包
        for item in itemset.items:          # 遍历该状态下的每个item
            right = item.right
            index = right.index('.')
            if index == len(right) - 1:
                continue
            symbol = right[index + 1]       # 点号后的首字符
            for p in self.productions:
                if p.left == symbol:
                    newRight = ['.'] + p.right          # 构造新的item
                    if index == len(right) - 2:         # 计算新item的lookahead
                        lookahead = item.lookahead      # 即点号后面只有一个符号
                        if type(lookahead) is not list:
                            lookahead = [lookahead]
                    else:                               # 点号后第二个字符的first集
                        lookahead = self.firstSet[right[index + 2]]
                        # print("lookahead", lookahead)
                    for sym in lookahead:
                        newItem = Item(p.left, newRight, sym)
                        # print("sym", sym, lookahead)
                        flag = False  # 检测新item是否已经在set中
                        for each in itemset.items:
                            if each.left == newItem.left and each.right == newItem.right and each.lookahead == newItem.lookahead:
                                flag = True
                        if not flag:
                            itemset.items.append(newItem)

        return itemset

    def goto(self, itemSet, symbol):        # 求出给定项目集对于符号X的转移状态
        newSet = ItemSet()
        for item in itemSet.items:
            right = item.right
            index = right.index('.')
            if index == len(right) - 1:     # 点号在末尾
                continue
            if right[index + 1] == symbol:
                newRight = right.copy()
                newRight[index], newRight[index + 1] = newRight[index + 1], newRight[index]
                newItem = Item(item.left, newRight, item.lookahead)
                newSet.items.append(newItem)
        newSet = self.closure(newSet)
        return newSet

    def buildTable(self):
        actionTable, gotoTable = [], []
        terms = self.terminals + ['$']
        for i in range(len(self.states)):
            # 填action表
            for symbol in terms:
                shiftable = []                                 # 收集当前状态可归约的item的lookahead
                for item in self.states[i].items:               # 遍历每一个item
                    right = item.right
                    index = right.index('.')

                    if index == len(right) - 1:                 # 点在最后一位，填归约动作
                        if symbol == item.lookahead and item.left != self.startSym + "'":          # 纵坐标终结符恰好为展望符，归约
                            right = item.right.copy()
                            right.pop(right.index('.'))         # 找到这是当前item的产生式的编号
                            pindex = self.proIndex(item.left, right)
                            entry = Entry(i, symbol, 'r' + str(int(pindex) + 1))
                            if not self.contains(actionTable, entry):
                                actionTable.append(entry)

                        if item.left == self.startSym + "'":    # 初始状态，接受！
                            entry = Entry(i, '$', 'acc')
                            if not self.contains(actionTable, entry):
                                actionTable.append(entry)
                        continue
                    if right[index + 1] == symbol:   # 如果点后紧跟着纵坐标对应的终结符
                        shiftable.append(right[index + 1])

                if len(shiftable) != 0:
                    gotoState = self.goto(self.states[i], symbol)
                    gotoIndex = self.stateIndex(gotoState)      # shift后应进入的状态
                    entry = Entry(i, symbol, 's' + str(gotoIndex))
                    if not self.contains(actionTable, entry):
                        actionTable.append(entry)

            # 填goto表
            for symbol in self.nonterminals:
                gotoState = self.goto(self.states[i], symbol)
                gotoIndex = self.stateIndex(gotoState)
                if gotoIndex != None:
                    entry = Entry(i, symbol, gotoIndex)
                    gotoTable.append(entry)
        self.actionTable = actionTable
        self.gotoTable = gotoTable

    def outputTable(self):
        f = open('ActionTable.txt', 'w')
        for entry in self.actionTable:
            string = str(entry.state) + "\t" + str(entry.symbol) +\
                     "\t" + str(entry.content) + "\n"
            f.write(string)
        f.close()
        f = open('GotoTable.txt', 'w')
        for entry in self.gotoTable:
            string = str(entry.state) + "\t" + str(entry.symbol) +\
                     "\t" + str(entry.content) + "\n"
            f.write(string)
        f.close()

    def readTable(self):
        actionTable, gotoTable = [], []
        for line in open('ActionTable.txt', 'r'):
            l = line.split()
            state, symbol, content = l[0], l[1], l[2]
            entry = Entry(state, symbol, content)
            actionTable.append(entry)
        for line in open('GotoTable.txt', 'r'):
            l = line.split()
            state, symbol, content = l[0], l[1], l[2]
            entry = Entry(state, symbol, content)
            gotoTable.append(entry)
        self.actionTable = actionTable
        self.gotoTable = gotoTable

    def findAction(self, state, symbol):
        for entry in self.actionTable:
            if int(entry.state) == state and entry.symbol == symbol:
                return entry.content

    def findGoto(self, state, symbol):
        for entry in self.gotoTable:
            if int(entry.state) == state and entry.symbol == symbol:
                return int(entry.content)

    def parse(self, w):
        f = open('Analysis_Result.txt','w')
        stateStack, symbolStack = [0], ['$']
        w.append(['$', '-', '-'])
        i = 0
        step = 0
        while True:
            symbol = w[i][0]
            type = w[i][1]
            if type == 'digit' or type == 'IDN':
                symbol = w[i][1]
            elif type == 'delimiter' or type == 'OP':
                symbol = w[i][0]
            f.write("Read symbol\t" + str(symbol) + '\n')
            top = stateStack[-1]
            content = self.findAction(top, symbol)
            if content == None:
                print("Error at line", w[i][3], "no action")
                f.write("Error at line\t" + str(w[0][3]) + "\tno action\n")
                break
            if content[0] == 's':
                stateIndex = int(content[1:])
                stateStack.append(stateIndex)
                symbolStack.append(symbol)
                f.write("\t\tshift\t" + str(symbol) + "\tand push state\t" + str(stateIndex) + "\n")
                i += 1
                if i == len(w):
                    # 保持输入字符串的最右端是$，如果不够就给它补！
                    w.append(['$', '-', '-'])
            elif content[0] == 'r':
                # 从状态栈中弹出|β|个符号
                pindex = int(content[1:])
                p = self.productions[pindex - 1]
                length = len(p.right)
                stateStack = stateStack[0:len(stateStack) - length]

                # 归约式左部替换符号栈的栈顶
                symbolStack = symbolStack[0:len(symbolStack) - length]
                symbolStack.append(p.left)

                f.write("\t\treduce using the production\t" + str(p.left) +"\t"+ str(p.right) + "\n")
                # 将goto的状态压入状态栈
                state = self.findGoto(stateStack[-1], p.left)
                f.write("\t\tpush state\t" + str(state) + "\n")
                stateStack.append(state)

            elif content == 'acc':
                print("Accept! Congratulations!")
                f.write("Accept! Congratulations!\n")
                break
            else:
                print("error: no choice")
                f.write("error: no choice\n")

            f.write("\t\tState stack:\t" + str(stateStack) + "\n")
            f.write("\t\tSymbol stack:\t" + str(symbolStack) + "\n")
            # self.restInput(w, i + 1)
            step += 1
        print("Finished in", step, "steps")
        f.write("Finished in\t" + str(step) + "\tsteps\n")

    def restInput(self, w, index):
        print("\t\tThe rest of input string:\t", end="")
        for i in range(index, len(w)):
            print(w[i][0]+"\t", end="")
        print()

    def contains(self, tab, entry):
        for each in tab:
            if each.state == entry.state and each.symbol == entry.symbol \
                    and each.content == entry.content:
                return True
        return False

    def proIndex(self, left, right):
        for p in self.productions:
            if p.left == left and p.right == right:
                return p.index

    def stateIndex(self, state):
        for i in range(len(self.states)):
            cur = self.states[i]                    # 类中存放的第i个状态
            if len(cur.items) != len(state.items):  # 给定状态
                continue
            flag = True
            for j in range(len(cur.items)):         # 每个item必须相同
                if cur.items[j].left == state.items[j].left \
                        and cur.items[j].right == state.items[j].right \
                        and cur.items[j].lookahead == state.items[j].lookahead:
                    continue
                else:
                    flag = False
                    break
            if flag:
                return i

    def viewSet(self, itemset):         # 查看一个项目集下的所有项目
        for item in itemset.items:
            print(item.left, item.right, item.lookahead)

    def viewItem(self, item):
        print(item.left, item.right, item.lookahead)

    def viewStates(self, states):       # 查看自动机的所有状态，显示其蕴含的项目
        i = 0
        for state in states:
            print(i)
            self.viewSet(state)
            i += 1

    def viewTable(self):
        print("Action table:")
        for entry in self.actionTable:
            print(entry.state, entry.symbol, entry.content)
        print("Goto table:")
        for entry in self.gotoTable:
            print(entry.state, entry.symbol, entry.content)

    def configure(self, grammar):
        self.productions = grammar.productions
        self.startSym = grammar.startSym
        self.nonterminals = grammar.nonterminals
        self.terminals = grammar.terminals
        self.firstSet = grammar.firstSet
        self.followSet = grammar.followSet
        self.readTable()

    def updateParse(self, w):
        self.buildStates()
        self.buildTable()
        self.outputTable()
        self.parse(w)

if __name__ == "__main__":
    lexer = Lexer()
    lexer.configure('source.txt')

    g = Grammar()
    g.configure('MyGrammar.txt')

    print("Building automata...")
    t1 = time.time()
    p = Parser()
    p.configure(g)
    print("Analysis table completed in", '{:.4f}s'.format(time.time() - t1))

    print("Parsing...")
    t2 = time.time()
    # p.parse(lexer.output)
    p.updateParse(lexer.output)
    print("Syntactic analysis completed in", '{:.4f}s'.format(time.time() - t2))


