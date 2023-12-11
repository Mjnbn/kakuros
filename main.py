import threading
import time
from collections import defaultdict
import copy
import graphic
import csp
import test
import kakuros


def main():
    for name, board in test.boards:
        # if name != "medium1":
        #     continue
        k = kakuros.Kakuros(board)
        start = time.time()
        c = csp.CSP(k, variable_ordering=csp.MCV, value_ordering=csp.LCV)
        c.solve()
        # thread = threading.Thread(target=c.solve)
        # thread.start()
        end = time.time()
        print("Time on test %s: %.6f" % (name, end - start))
        print("Number of assignments: %d" % k.number_of_assignments)
        # graphic.graphic(k)


if __name__ == "__main__":
    main()