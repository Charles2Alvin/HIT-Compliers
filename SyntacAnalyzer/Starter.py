from Parser import *
from Grammar import *

if __name__ == "__main__":
    lexer = Lexer()
    lexer.configure('LL1Code.txt')

    g = Grammar()
    g.configure('LL1.txt')

    print("\nBuilding automata...")
    t1 = time.time()
    p = Parser()
    p.configure(g)
    print("Analysis table completed in", '{:.4f}s'.format(time.time() - t1))

    print("\nParsing...")
    t2 = time.time()
    p.updateParse(lexer.output)
    print("Syntactic analysis completed in", '{:.4f}s'.format(time.time() - t2))

    print("\nAnalyzing...")
    t3 = time.time()
    analyzer = Analyzer(p.root, p.Dlist, p.Slist)
    analyzer.configure()