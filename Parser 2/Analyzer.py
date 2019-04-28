from Helper import *


class Line:
    def __init__(self, op, operand1, operand2, assign):
        self.op = op
        self.operand1 = operand1
        self.operand2 = operand2
        self.assign = assign

    def __str__(self):
        return '(' + self.op + ', ' + self.operand1 + ', ' + self.operand2 + ', ' + self.assign + ')'


class Symbol:
    def __init__(self, name, type, addr):
        self.name = name
        self.type = type
        self.addr = addr
        self.val = 0

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.type == other.type
        else:
            return False

    def __str__(self):
        return self.name + ' ' + self.type + ' ' + str(self.val) + ' ' + str(self.addr)


class TreeNode:
    def __init__(self, name=None, production=Production(None, None)):
        self.parent = None
        self.children = []
        self.name = name
        self.production = production
        self.left = production.left
        self.right = production.right
        self.tuple = []

    @staticmethod
    def search(root):
        queue = [root]
        while len(queue) != 0:
            head = queue[0]
            print(head.name, head.tuple, head.left, head.right)
            queue.pop(0)
            if head.children is not None:
                for child in head.children:
                    queue.append(child)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.tuple == other.tuple and self.name == other.name
        else:
            return False


class Analyzer:
    def __init__(self, root, Dlist, Slist):
        self.root = root
        self.stack = []
        self.code = []
        self.Dlist = Dlist
        self.Slist = Slist
        self.count = 0      # 行号
        self.record = []
        self.table = []

    def configure(self):
        # 把包含在其他语句块的语句块挑出来
        indices = []
        for i in range(len(self.Slist)):
            for j in range(i, len(self.Slist)):
                if self.isSubTreeOf(self.Slist[i], self.Slist[j]):
                    if i not in indices:
                        indices.append(i)

        # 只保留不包含在其他语句块的语句块
        Slist = []
        for i in range(len(self.Slist)):
            if i not in indices:
                Slist.append(self.Slist[i])
        self.Slist = Slist
        # 为每个独立语句块生成中间代码
        for node in self.Slist:
            if node.name not in self.record:
                self.generate(node)
        # 设置行号
        # self.setLine()
        # 设置变量名
        self.setVar()
        # 显示中间代码
        self.showCode()
        # 检查变量是否已声明
        self.isDeclared()
        # 显示符号表
        self.showSymbols()
        # 输出符号表到文件
        self.outputSymbol()
        # 输出中间代码到文件
        self.outCode()

    def generate(self, root):
        flag1 = True        # 表明该节点的孩纸不包含$，没有依赖关系
        for i in range(len(root.tuple) - 1, -1, -1):
            if root.tuple[i][0] == '$':
                flag1 = False
                break

        flag2 = True        # 表明该节点全为$，完全依赖关系
        for item in root.tuple:
            if item[0] != '$':
                flag2 = False
                break

        if flag1 is True:       # 可以直接生成代码，没有依赖关系
            op = root.tuple[1]
            if op == '=':
                operand1, operand2, assign = root.tuple[2], '-', root.tuple[0]
            else:
                operand1, operand2, assign = root.tuple[0], root.tuple[2], root.name
            line = Line(op, operand1, operand2, assign)
            self.count += 1
            self.code.append(line)
        elif flag2 is False:    # 孩子既有终结符也有$
            if 'if' in root.tuple:
                # 三个j语句的位置
                j1, j2, j3 = 0, 0, 0
                # 生成第一个跳转语句
                op, operand1, operand2, assign = 'j'+str(root.children[2].tuple[1]), \
                                                 root.children[2].tuple[0], \
                                                 root.children[2].tuple[2], '-'
                line = Line(op, operand1, operand2, assign)
                self.count += 1

                self.code.append(line)
                # 设置第一个跳转语句的位置，以及跳转的目的地
                j1 = self.count
                j2 = j1 + 1

                # 生成第二个跳转语句
                op, operand1, operand2, assign = 'j', '-', '-', '-'
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                self.code.append(line)

                # 生成条件成立对应的语句块
                self.generate(root.children[4])

                # 记录第三个跳转语句的位置（离开语句）
                j3 = self.count

                # 生成第三个跳转语句
                op, operand1, operand2, assign = 'j', '-', '-', '-'
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                self.code.append(line)

                # 设置第二个跳转语句的目的地
                self.code[j2 - 1].assign = str(self.count)

                # if -> 生成条件不成立对应的语句块
                self.generate(root.children[6])
                self.code[j1 - 1].assign = str(j2 + 1)
                self.code[j3].assign = str(self.count + 1)
            elif 'while' in root.tuple:
                # 记录三个跳转语句的位置
                j1, j2, j3 = 0, 0, 0
                # 生成第一个跳转语句
                op, operand1, operand2, assign = 'j' + str(root.children[2].tuple[1]), \
                                                 root.children[2].tuple[0], \
                                                 root.children[2].tuple[2], '-'
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                j1 = self.count
                j2 = j1 + 1
                self.code.append(line)

                # 生成第二个跳转语句
                op, operand1, operand2, assign = 'j', '-', '-', '-'
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                self.code.append(line)

                # 生成条件成立对应的语句块
                self.generate(root.children[4])

                # 生成第三个跳转语句
                op, operand1, operand2, assign = 'j', '-', '-', str(j1)
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                self.code.append(line)
                self.code[j1 - 1].assign = str(j1 + 2)
                self.code[j2 - 1].assign = str(self.count + 1)

            else:
                if root.name in self.record:
                    return
                self.generate(root.children[i])
                operand1, op, operand2, assign = root.children[2].name, root.tuple[1], \
                                                 '-', root.tuple[0]
                line = Line(op, operand1, operand2, assign)
                self.count += 1
                self.code.append(line)
                self.record.append(root.name)

        else:                   # 子节点全是依赖关系
            for i in range(len(root.children)):
                self.generate(root.children[i])

    def setLine(self):
        indices = []      # 记录if语句的开始处
        for i in range(len(self.code)):
            line = self.code[i]
            if line.op[0] == 'j' and len(line.op) == 2:
                # 进入if分支语句块
                indices.append(i)
        while len(indices) != 0:
            index = indices.pop()
            # 设置第一个跳转语句的跳转位置
            self.code[index].assign = str(index + 3)
            # 设置第二个跳转语句的跳转位置
            cur = index + 2
            while self.code[cur].op[0] != 'j':
                cur += 1
            self.code[index + 1].assign = str(cur + 2)
            # 设置第三个跳转语句的跳转位置
            cur = cur + 2
            # while self.code[cur].op[0]

    def setVar(self):
        vars = []
        for line in self.code:
            if line.operand1[0] == '$' and line.operand1 not in vars:
                vars.append(line.operand1)
            if line.operand2[0] == '$' and line.operand2 not in vars:
                vars.append(line.operand2)
            if line.assign[0] == '$' and line.assign not in vars:
                vars.append(line.assign)
        tCount = 1
        for var in vars:
            for line in self.code:
                if line.operand1 == var:
                    line.operand1 = 't'+str(tCount)
                if line.operand2 == var:
                    line.operand2 = 't'+str(tCount)
                if line.assign == var:
                    line.assign = 't'+str(tCount)
            tCount += 1

    def showCode(self):
        count = 1
        for line in self.code:
            string = str(count) + ':\t' + '(' + line.op + ', ' + line.operand1 + ', ' \
                     + line.operand2 + ', ' + line.assign + ')'
            print(string)
            count += 1

    def isSubTreeOf(self, root1, root2):
        # 判断root1是否为root2的子树
        if not root2.children:
            return False
        for item in root2.tuple:
            if item == root1.name:
                return True
        flag = False
        for child in root2.children:
            flag = flag or self.isSubTreeOf(root1, child)
        return flag

    def isDeclared(self):
        addr, vars, duplicates = 0, [], []
        for item in self.Dlist:
            name, type = item.tuple[1], item.tuple[0]
            symbol = Symbol(name, type, addr)
            if type == 'int':
                addr += 4
            else:
                addr += 8
            if name not in vars:
                self.table.append(symbol)
                vars.append(name)
            else:
                duplicates.append(name)
        # 检查未声明的变量
        unDeclared = []
        for line in self.code:
            items = [line.operand1, line.operand2, line.assign]
            for item in items:
                if item not in vars and item[0] != 't' and item != '-' \
                and item not in unDeclared and not item.isdigit():
                    unDeclared.append(item)
        print("\n*** Variable declaration error ***")
        for var in unDeclared:
            print("Undeclared variable: ", var)
        for var in duplicates:
            print("Repeated declaration: ", var)

    def showSymbols(self):
        print("\n*** Symbol table ***")
        for symbol in self.table:
            print(symbol)

    def outputSymbol(self):
        f = open('Symbols.txt', 'w')
        for symbol in self.table:
            f.write(str(symbol))
            f.write("\n")

    def outCode(self):
        f = open('IntermediateCode.txt', 'w')
        for line in self.code:
            f.write(str(line))
            f.write('\n')


