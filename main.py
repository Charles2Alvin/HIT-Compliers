from parser import *
from grammar import *
from lexer import *
if __name__ == "__main__":
    lexer = Lexer()
    lexer.configure('./grammar&code/SimpleCode.txt')

    g = Grammar()
    g.configure('./grammar&code/SimpleGrammar.txt')

    print("\nBuilding automata...")
    t1 = time.time()
    p = Parser()
    p.configure(g)
    print("Analysis table completed in", '{:.4f}s'.format(time.time() - t1))

    print("\nParsing...")
    t2 = time.time()
    # p.parse(lexer.output)
    p.update_parse(lexer.output)
    print("Syntactic analysis completed in", '{:.4f}s'.format(time.time() - t2))

    print("\nAnalyzing...")
    t3 = time.time()
    analyzer = Analyzer(p.root, p.Dlist, p.Slist)
    analyzer.configure()