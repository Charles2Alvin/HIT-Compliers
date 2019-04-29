from helper import *


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
        self.temp_var = []

    def configure(self):
        # 把包含在其他语句块的语句块挑出来
        indices = []
        for i in range(len(self.Slist)):
            for j in range(i, len(self.Slist)):
                if self.is_sub_tree_of(self.Slist[i], self.Slist[j]):
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
        # 设置变量名
        self.set_var()
        # 显示中间代码
        self.show_code()
        # 检查变量是否已声明
        self.check_declaration()
        # 检查类型转换错误
        self.check_convert()
        # 显示符号表
        self.show_symbols()
        # 输出符号表到文件
        self.output_symbol()
        # 输出中间代码到文件
        self.output_code()

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

    def set_var(self):  # 把$符号改成t符号
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

    def show_code(self):
        count = 1
        for line in self.code:
            string = str(count) + ':\t' + '(' + line.op + ', ' + line.operand1 + ', ' \
                     + line.operand2 + ', ' + line.assign + ')'
            print(string)
            count += 1

    def is_sub_tree_of(self, root1, root2):
        # 判断root1是否为root2的子树
        if not root2.children:
            return False
        for item in root2.tuple:
            if item == root1.name:
                return True
        flag = False
        for child in root2.children:
            flag = flag or self.is_sub_tree_of(root1, child)
        return flag

    def check_declaration(self):      # 检查变量声明错误
        addr, vars, duplicates = 0, [], []
        for item in self.Dlist:       # 遍历Dlist来填符号表
            name, type = item.tuple[1], item.tuple[0]
            symbol = Symbol(name, type, hex(addr))
            if type == 'int':
                addr += 4
            else:
                addr += 8
            if name not in vars:
                self.table.append(symbol)
                vars.append(name)
            else:
                duplicates.append(name)
        # 检查变量未声明错误、类型转换错误（double -> int）
        unDeclared = []
        for line in self.code:
            items = [line.operand1, line.operand2, line.assign]
            for item in items:
                if item not in vars and item[0] != 't' and item != '-' \
                and item not in unDeclared and not item.isdigit():
                    unDeclared.append(item)
            var1, var2 = line.operand1, line.operand2
            type1, type2 = self.find_type(var1), self.find_type(var2)
            if type1 is None or type2 is None:
                continue
            if line.assign[0] == 't':
                types = [type1, type2]
                if 'double' in types:
                    new_type = 'double'
                    incr = 8
                else:
                    new_type = 'int'
                    incr = 4
                self.temp_var.append(Symbol(line.assign, new_type, hex(addr)))
                addr += incr

        print("\n*** Variable declaration error ***")
        for var in unDeclared:
            print("Undeclared variable: ", var)
        for var in duplicates:
            print("Repeated declaration: ", var)

    def find_type(self, var):
        for symbol in self.table:
            if symbol.name == var:
                return symbol.type
        for symbol in self.temp_var:
            if symbol.name == var:
                return symbol.type

    def show_symbols(self):
        print("\n*** Symbol table ***")
        for symbol in self.table:
            print(symbol)
        print("\n*** Temp vars table ***")
        for symbol in self.temp_var:
            print(symbol)

    def output_symbol(self):
        f = open('./output/Symbols.txt', 'w')
        for symbol in self.table:
            f.write(str(symbol))
            f.write("\n")

    def output_code(self):
        f = open('./output/IntermediateCode.txt', 'w')
        for line in self.code:
            f.write(str(line))
            f.write('\n')

    def check_convert(self):
        vars, count = [], 0
        for line in self.code:
            op, var1, var2 = line.op, line.operand1, line.assign
            count += 1
            if op != '=':
                continue
            type1, type2 = self.find_type(var1), self.find_type(var2)
            if type1 == 'double' and type2 == 'int':
                vars.append(count)
        print("\n*** Type convert error ***")
        for var in vars:
            print("Convert from double to int, at line", var)


