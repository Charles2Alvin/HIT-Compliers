#!/usr/bin/python
# -*- coding: UTF-8 -*-
from semantic_analyzer import *
import collections
import pickle


# noinspection PyUnresolvedReferences
class Parser(object):
    """ LR1 Parser """
    def __init__(self):
        self.start_symbol = ''
        self.productions = []
        self.first_set = {}
        self.followSet = {}
        self.terminals = []
        self.nonterminals = []
        self.automata = []
        self.action_dict = collections.defaultdict(dict)
        self.goto_dict = collections.defaultdict(dict)
        self.root = ''

    def build_automata(self):
        """
        Build the automata for recognizing the viable prefix.

        Parameters:
          self - a parser obejct

        """
        start_state = [Item(self.start_symbol + "'", ['.', self.start_symbol], '#')]
        automata = [self.closure(start_state)]
        flag = True
        while flag:
            flag = False
            for state in automata:
                for symbol in self.nonterminals + self.terminals:
                    new_state = self.goto(state, symbol)
                    if len(new_state) == 0:      # the state goes nowhere with the symbol
                        continue
                    if new_state not in automata:
                        automata.append(new_state)
                        flag = True
        self.automata = automata

    def closure(self, itemset):
        """
        Build the closure of the given state, or say item set.

        Args:
            itemset: a state of the automata, which holds some items

        Returns:
            itemset: an expanded item set, or say its closure
        """
        for item in itemset:
            right = item.right
            index = right.index('.')
            var = len(right) - index - 1    # number of symbols after dot
            if var == 0:
                continue
            symbol = right[index + 1]       # the first symbol after dot
            for p in self.productions:
                if p.left != symbol:
                    continue
                    # build a new item and calculate its lookahead symbol
                    # construct the right part by moving the dot one step backward
                    # two conditions for calculating the lookahead symbol
                    # if there is only one symbol after dot, the new lookahead inherits from
                    # the original item;
                    # otherwise, the new lookahead will be the first set of the right part of after dot
                    # e.g. for A -> B.CDEF, C -> GH
                    # new item: C -> .GH, lookahead(C) = first(DEF)
                if var == 1:            # only one symbol after dot
                    lookahead = item.lookahead
                    if type(lookahead) is not list:
                        lookahead = [lookahead]
                else:
                    lookahead = []
                    flag = True         # records whether all the symbols after dot are nullable
                    for v in range(index + 2, index + var + 1):
                        terminal = right[v]
                        first = self.first_set[terminal]
                        for each in first:
                            if each not in lookahead and each != '$':
                                lookahead.append(each)
                        if '$' not in first:
                            flag = False
                            break
                    if flag is True:    # then '#' could be met
                        lookahead.append('#')
                new_right = ['.'] + p.right
                for terminal in lookahead:
                    new_item = Item(p.left, new_right, terminal)
                    if new_item not in itemset:
                        itemset.append(new_item)
        return itemset

    def goto(self, itemset, symbol):
        """
        Construct the transition state.

        Args:
            itemset: a state of the automata, which holds some items
            symbol: the transfer symbol
        Returns:
            itemset: a transition state
        """
        new_state = []
        for item in itemset:
            right = item.right
            index = right.index('.')
            if index == len(right) - 1 or right[1] == '$':     # no symbol follows the dot or epsilon transition
                continue
            if right[index + 1] == symbol:
                new_right = right.copy()
                new_right[index], new_right[index + 1] = new_right[index + 1], new_right[index]
                item = Item(item.left, new_right, item.lookahead)
                new_state.append(item)
        new_state = self.closure(new_state)
        return new_state

    def fill_table(self):
        """
        Construct the action table and goto table.

        Args:
            self: a parser object
        """
        action_dict, goto_dict = collections.defaultdict(dict), collections.defaultdict(dict)
        terms = self.terminals + ['#']
        for i in range(len(self.automata)):
            for symbol in terms:                    # fill the action table
                shiftable = []                      # collect the lookahead symbols of reducible items
                for item in self.automata[i]:
                    right = item.right
                    index = right.index('.')

                    if index == len(right) - 1:     # a reducible item, fill with reduce action
                        if symbol == item.lookahead and item.left != self.start_symbol + "'":          # 纵坐标终结符恰好为展望符，归约
                            right = item.right.copy()
                            right.pop(right.index('.'))
                            action_dict[i][symbol] = DictEntry(action='r', left=item.left, right=right)

                        if item.left == self.start_symbol + "'":    # initial state, accept it
                            action_dict[i]['#'] = DictEntry(action='acc')
                        continue

                    if right[index + 1] == '$' and symbol == item.lookahead:    # epsilon transition also reducible
                        right = item.right.copy()
                        right.pop(right.index('.'))
                        action_dict[i][symbol] = DictEntry(action='r', left=item.left, right=right)
                        continue

                    if right[index + 1] == symbol and right[index + 1] != '$':   # add shiftable terms
                        shiftable.append(right[index + 1])

                if len(shiftable) != 0:         # fill with shift action
                    goto_state = self.goto(self.automata[i], symbol)
                    index = self.automata.index(goto_state)
                    action_dict[i][symbol] = DictEntry(action='s', shift_state=index)

            for symbol in self.nonterminals:    # fill the goto table
                goto_state = self.goto(self.automata[i], symbol)
                if goto_state in self.automata:
                    goto_index = self.automata.index(goto_state)
                    goto_dict[i][symbol] = DictEntry(goto_state=goto_index)
        self.action_dict = action_dict
        self.goto_dict = goto_dict

    def parse(self, w):
        """
        Parse the input tokens and judge whether it is grammatically correct.
        Write the record to files
        Args:
            w: a list of tokens
        """
        w.append(['#', '-', '-', 'end'])
        f = open('./output/Analysis_Result.txt', 'w')
        i, step, counter = 0, 0, 0
        state_stack, symbol_stack, forest, Slist, Dlist = [0], ['#'], [], [], []

        while True:
            # Preprocess:
            # replace the identifiers with IDN
            # replacet the numbers with digit
            symbol = w[i][0]
            dtype = w[i][1]
            if dtype == 'digit' or dtype == 'IDN':
                symbol = w[i][1]
            f.write("Read symbol\t" + str(symbol) + '\n')
            top = state_stack[-1]
            dict_entry = self.action_dict[top][symbol]
            action = dict_entry.action
            content = dict_entry.content

            if action is None:
                print("Error at line", w[i][3], "no action")
                f.write("Error at line\t" + str(w[0][3]) + "\tno action\n")
                break

            if action == 's':               # take shift action
                state_index = content['shift_state']
                state_stack.append(state_index)
                symbol_stack.append(symbol)

                t = TreeNode(name=w[i][0])  # add a leaf node to the forest
                forest.append(t)
                i += 1

                f.write("\t\tshift\t" + str(symbol) + "\tand push state\t" + str(state_index) + "\n")

            elif action == 'r':             # take reduce action
                left = content['left']
                right = content['right']

                if right[0] == '$':       # reduce by epsilon production
                    symbol_stack.append(left)
                    state = self.goto_dict[state_stack[-1]][left].content['goto_state']
                    state_stack.append(state)
                    t = TreeNode(name=left)     # add a leaf node to the forest
                    forest.append(t)

                    f.write("\t\treduce using the production\t" + str(left) + "->" + str(right) + "\n")
                    f.write("\t\tpush state\t" + str(state) + "\n")
                    f.write("\t\tState stack:\t" + str(state_stack) + "\n")
                    f.write("\t\tSymbol stack:\t" + str(symbol_stack) + "\n")
                    f.write("\t\tForest stack:\t" + str(forest) + "\n")

                    continue
                # reduce by normal production
                # pop |β| symbols from top of the state stack
                # replace the top of the symbol stack with the left part of the production
                # push the goto state into the state stack
                length = len(right)
                state_stack = state_stack[0:len(state_stack) - length]
                symbol_stack = symbol_stack[0:len(symbol_stack) - length]
                symbol_stack.append(left)

                state = self.goto_dict[state_stack[-1]][left].content['goto_state']
                state_stack.append(state)

                # take nodes from the stack top as children and link them to their parent
                # add D-type node and S-type node to lists
                children = forest[len(forest) - length:]
                for l in range(length):
                    forest.pop()
                if len(right) == 1:
                    parent = TreeNode(name=children[0].name)
                else:
                    parent = TreeNode(name='$'+str(counter), production=Production(left, right))
                    for child in children:
                        parent.tuple.append(child.name)
                    counter += 1
                parent.children = children
                forest.append(parent)
                if left == 'S':
                    Slist.append(parent)
                elif left == 'D' and right != ['D', 'D']:
                    Dlist.append(parent)

                f.write("\t\treduce using the production\t" + str(left) +"->"+ str(right) + "\n")
                f.write("\t\tpush state\t" + str(state) + "\n")

            elif action == 'acc':
                print("Accept! Congratulations!")
                f.write("Accept! Congratulations!\n")
                break

            f.write("\t\tState stack:\t" + str(state_stack) + "\n")
            f.write("\t\tSymbol stack:\t" + str(symbol_stack) + "\n")
            f.write("\t\tForest stack:\t" + str(forest) + "\n")
            step += 1

        print("Finished in", step, "steps")
        f.write("Finished in\t" + str(step) + "\tsteps\n")
        self.root, self.Slist, self.Dlist = forest[0], Slist, Dlist

    def export_tables(self):
        """
        Export the action table and goto table to files and perform serialization.

        Args:
            self: a parser object
        """
        f = open('./output/ActionTable.txt', 'w')
        for k, v in self.action_dict.items():
            for key, value in v.items():
                string = str(k) + "\t" + str(key) + "\t" + str(value.action) + "\t" + str(value.content) + "\n"
                f.write(string)

        f.close()

        f = open('./output/GotoTable.txt', 'w')
        for k, v in self.goto_dict.items():
            for key, value in v.items():
                string = str(k) + "\t" + str(key) + "\t" + str(value.content) + "\n"
                f.write(string)
        f.close()

        f = open('./output/action_dict', 'wb')
        pickle.dump(self.action_dict, f)
        f.close()

        f = open('./output/goto_dict', 'wb')
        pickle.dump(self.goto_dict, f)
        f.close()

    def load_tables(self):
        """
        Load the action table and goto table dictionaries to the object

        Args:
            self: a parser object
        """
        action_dict, goto_dict = collections.defaultdict(dict), collections.defaultdict(dict)

        f = open('./output/action_dict', 'rb')
        self.action_dict = pickle.load(f)
        f.close()

        f = open('./output/goto_dict', 'rb')
        self.goto_dict = pickle.load(f)
        f.close()

    def production_index(self, left, right):
        for p in self.productions:
            if p.left == left and p.right == right:
                return p.index

    def view_automata(self):       # 查看自动机的所有状态，显示其蕴含的项目
        i = 0
        for state in self.automata:
            print(i)
            for item in state:
                print(item)
            i += 1

    def configure(self, grammar):
        self.productions = grammar.productions
        self.start_symbol = grammar.start_symbol
        self.nonterminals = grammar.nonterminals
        self.terminals = grammar.terminals
        self.first_set = grammar.firstSet
        self.followSet = grammar.followSet
        self.load_tables()

    def update_parse(self, w):
        self.build_automata()
        self.fill_table()
        self.export_tables()
        self.parse(w)

