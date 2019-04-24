import time
import re
class Lexer:
    def __init__(self):
        self.code = ''
        self.OPERATOR = ['+', '-', '*', '/', '+=', '-=', '/=', '*=', '++', '--',\
                         '==', '>=', '<=', '=', 'and', 'or', \
                         '&&', '||', '~',\
                         '++', '--']
        self.KEY_WORD = ['if', 'else', 'then', 'for', 'do', 'while', \
                         'int', 'float', 'char', 'long', 'double', 'bool', 'typedef', 'struct','void',\
                         'true', 'false','return', '@', \
                         'include', 'using', 'namespace', 'std', 'new',\
                         'printf', 'scanf', 'System', 'public', 'private', 'protected', 'class']
        self.TYPE = ['int', 'float', 'char', 'long', 'bool']
        self.DELIMITER = ['(', ')', '{', '}','[',']', ';', '<', '>', ',']
        self.map = {'if': 'IF', 'else': 'ELSE', 'then': 'THEN', 'for': 'FOR', 'while': 'WHILE', \
                    'int': 'INT', 'float': 'FLOAT', 'char': 'CHAR', 'long': 'LONG', 'bool': 'BOOL', \
                    'true':'TRUE', 'false':'FALSE','double': 'DOUBLE', '@': 'my', \
                    'typedef': 'C', 'struct': 'C', 'void': 'C', 'printf': 'C', 'scanf': 'C', 'return': 'C', \
                    'System': 'JAVA','public': 'ACESS', 'private': 'ACESS', 'protected': 'ACESS', 'class': 'JAVA', \
                    'using': 'CPP', 'namespace': 'CPP', 'main': 'CPP', 'include': 'CPP', 'new':'CPP'}
        self.delimiter = {'(': 'LP', ')': 'RP', '{': 'CLP', '}': 'CRP', '[': 'LSB', ']': 'RSB', \
                          ';': 'SEMI'}

        self.output = []
        self.variables = {}
        self.varCount = 0
        self.charError = False

    def readFile(self, path):
        f = open(path, 'r')
        code = f.read()
        self.code = code.split('\n')
        f.close()

    def preprocess(self):
        lineIndex = 1
        tuples = []
        flag = False
        for line in self.code:
            # # 删除单行内的所有注释
            # while '/*' in line and '*/' in line:
            #     leftNote = line.index('/*')
            #     rightNote = line.index('*/')
            #     part1 = line[0:leftNote]
            #     part2 = line[rightNote + 2:]
            #     line = part1 + part2
            # # 删除跨行注释，出现左部时，保留左边内容
            # if '/*' in line:
            #     leftNote = line.index('/*')
            #     line = line[0:leftNote]
            #     li = line.split()
            #     for word in li:
            #         tuples.append([word, lineIndex])
            #     flag = True
            # if '*/' in line and flag is True:
            #     flag = False
            #     rightNote = line.index('*/')
            #     line = line[rightNote + 2:]
            # if flag is True:
            #     lineIndex += 1
            #     continue
            word = ''
            for i in range(len(line)):
                if line[i] != ' ':
                    word += line[i]
                elif line[i] == ' ':
                    if word != '' and word != '\t':
                        word = word.replace('\t', '')
                        tuples.append([word, lineIndex])
                        word = ''
                    else:
                        continue
            if word != '' and word != '\t':
                word = word.replace('\t', '')
                tuples.append([word, lineIndex])
            lineIndex += 1
        self.charset = set(self.code)
        self.tuples = tuples

    def recogNum(self, word):
        length = len(word)
        decimal, exponent, plus, minus = False, False, False, False
        for i in range(length):
            char = word[i]
            if char.isdigit():
                continue
            elif char == '.':
                if decimal is False and exponent is False:
                    decimal = True
                    continue
                else:
                    return i
            elif char == 'E':
                if (not exponent) and i in range(1, length - 1) and \
                        word[i - 1].isdigit() and (not plus) and (not minus) \
                        and (word[i + 1].isdigit() or word[i + 1] in ['+', '-']):
                    exponent = True
                    continue
                else:
                    return i
            elif char == '+' or char == '-':
                if (not plus) and (not minus) and i != 0 and word[i - 1] == 'E':
                    plus = True
                    continue
                else:
                    return i
            elif char == '-':
                if (not plus) and (not minus) and i != 0 and word[i - 1] == 'E':
                    minus = True
                    continue
                else:
                    return i
            else:
                return i
        return True

    def recogIdentifier(self, word):
        length = len(word)
        letter = False
        for i in range(length):
            char = word[i]
            if char.isdigit():
                if letter:
                    continue
                else:
                    return i
            elif char.isalpha():
                letter = True
                continue
            elif char == '_':
                continue
            else:
                return i
        return True

    def parseWord(self, tuple):
        word, line = tuple[0], tuple[1]
        if len(word) == 0:
            return
        if len(word) >= 2 and word[0:2] in self.OPERATOR:
            self.output.append([word[0:2], "OP", "-", line])
            self.parseWord([word[2:], line])
            return
        char = word[0]
        if word in self.KEY_WORD:
            self.output.append([word, self.map[word], "-", line])
        elif word in self.OPERATOR:
            self.output.append([word, 'OP', word, line])
        elif char in self.OPERATOR:
            self.output.append([char, 'OP', word, line])
            self.parseWord([word[1:], line])
        elif char.isdigit():
            result = self.recogNum(word)
            if result is True:
                self.output.append([word, "digit", word, line])
            else:
                if result != 0:
                    self.output.append([word[:result], "digit", word[:result], line])
                    self.parseWord([word[result:], line])
        elif char.isalpha():
            result = self.recogIdentifier(word)
            if result is True:
                self.output.append([word, "IDN", word, line])
                self.varCount += 1
            else:
                if result != 0:
                    self.output.append([word[:result], "IDN", word[:result], line])
                    word = word[result:]
                    self.parseWord([word, line])
        elif char in self.DELIMITER:
            self.output.append([char, "delimiter", char, line])
            if len(word) >= 2:
                word = word[1:]
                self.parseWord([word, line])

    def parse(self):
        for tuple in self.tuples:
            self.parseWord(tuple)

    def setTable(self):
        # 输出符号表到文件
        f = open('Tokens.txt', 'w')
        for term in self.output:
            f.write(str(term[0]) + "\t<" + str(term[1]) + "," + str(term[2]) + ">\t" + str(term[3]) + "\n")
        f.close()

    def configure(self, path):
        print("Conducting lexical analysis...")
        t = time.time()
        self.readFile(path)
        self.preprocess()
        self.parse()
        self.setTable()
        print("Lexical analysis completed in", '{:.4f}ms'.format(1000*(time.time() - t)))


if __name__ == "__main__":
    lexer = Lexer()
    # lexer.configure('source.txt')
    lexer.configure('LL1Code.txt')
