import threading
import time
from collections import defaultdict
import copy
import graphic

NORMAL = 0

class Kakuros:
    def __init__(self, board, filtering=None, variable_ordering=None, value_ordering=None):
        self.board = board
        self.variables = []
        self.raw_domains = defaultdict(list)
        self.neighbors = defaultdict(set)
        self.vertical_neighbors = defaultdict(set)
        self.horizontal_neighbors = defaultdict(set)
        self.vertical_sum = defaultdict(int)
        self.horizontal_sum = defaultdict(int)
        self.constraints = defaultdict(set)
        self.curr_assignments = {}
        self.domains = {}  # {var1: [val1, val2, ...], ...}
        #self.unassigned_variables = variables.copy()
        #self.state = state
        # for var in self.curr_assignments:
        #     self.state[var[0]][var[1]] = str(self.curr_assignments[var])
        #     self.unassigned_variables.remove(var)
        self.filtering = filtering
        self.variable_ordering = variable_ordering
        self.value_ordering = value_ordering
        #self.get_info(board)

    def get_info(self):
        variables = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                cell = self.board[i][j]
                if cell != 'X' and '\\' not in cell:
                    if cell != '':
                        self.curr_assignments[(i, j)] = int(cell)
                    else:
                        variables.append((i, j))
                        self.domains[(i,j)] = set([i for i in range(1, 10)])
                if '\\' in cell:
                    index = cell.find('\\')  # Find the index of '\\'

                    if index > 0:  # n\
                        number_before = int(cell[:index])
                        relevant_vars = []
                        k = i + 1
                        while k < len(self.board) and self.board[k][j] != 'X' and '\\' not in self.board[k][j]:
                            relevant_vars.append((k, j))
                            k += 1
                        self.get_info_helper(number_before, relevant_vars, is_vertical=False)

                    if index < len(cell) - 1:  # \n
                        number_after = int(cell[index + 1:])
                        relevant_vars = []
                        k = j + 1
                        while k < len(self.board[i]) and self.board[i][k] != 'X' and '\\' not in self.board[i][k]:
                            relevant_vars.append((i, k))
                            k += 1
                        self.get_info_helper(number_after, relevant_vars, is_vertical=True)

        for c,v in self.curr_assignments.items():
            self.set_value(c,v)

        self.variables = variables

    def get_info_helper(self, number, relevant_vars, is_vertical):
        if is_vertical:
            for var1 in relevant_vars:
                self.vertical_sum[var1] = number
        else:
            for var1 in relevant_vars:
                self.horizontal_sum[var1] = number

        if len(relevant_vars) == 1:
            self.raw_domains[relevant_vars[0]].append(number)

        for v1 in relevant_vars:
            for v2 in relevant_vars:
                if v1 != v2:
                    self.neighbors[v1].add(v2)
                    if is_vertical:
                        self.vertical_neighbors[v1].add(v2)
                    else:
                        self.horizontal_neighbors[v1].add(v2)

    def is_consistent(self, var, value):
        # Check if the assignment violates any constraints
        for neighbor in self.neighbors[var]:
            if neighbor in self.curr_assignments:
                neighbor_value = self.curr_assignments[neighbor]
                if neighbor_value == value:
                    return False

        # Check if the assignment violates the sum constraints
        if var in self.vertical_sum:
            cnt = 0
            sum_so_far = value
            if sum_so_far > self.vertical_sum[var]:
                return False
            for neighbor in self.vertical_neighbors[var]:
                if neighbor in self.curr_assignments:
                    cnt += 1
                    sum_so_far += self.curr_assignments[neighbor]
                    if sum_so_far > self.vertical_sum[var]:
                        return False
                elif sum_so_far == self.vertical_sum[var]:
                    return False
            if cnt == len(self.vertical_neighbors[var]) and sum_so_far < self.vertical_sum[var]:
                return False

        if var in self.horizontal_sum:
            sum_so_far = value
            cnt = 0
            if sum_so_far > self.horizontal_sum[var]:
                return False
            for neighbor in self.horizontal_neighbors[var]:
                if neighbor in self.curr_assignments:
                    cnt += 1
                    sum_so_far += self.curr_assignments[neighbor]
                    if sum_so_far > self.horizontal_sum[var]:
                        return False
                elif sum_so_far == self.horizontal_sum[var]:
                    return False
            if cnt == len(self.horizontal_neighbors[var]) and sum_so_far < self.horizontal_sum[var]:
                return False

        return True

    def get_next_variable(self):
        if self.variable_ordering == NORMAL:
            for v in self.variables:
                if v not in self.curr_assignments:
                    return v
            return None

    def set_value(self, var, val):
        self.curr_assignments[var] = val
        self.board[var[0]][var[1]] = chr(val + ord('0'))
        time.sleep(0.05)
        for v in self.neighbors[var]:
            if val in self.domains[v]:
                self.domains[v].remove(val)


def backtrack(kakuros):
    if kakuros.get_next_variable() is None:
        return True
    v = kakuros.get_next_variable()
    dom = kakuros.domains[v].copy()
    for d in dom:
        if kakuros.is_consistent(v, d):
            pre_k = copy.deepcopy(kakuros.domains)
            kakuros.set_value(v, d)
            result = backtrack(kakuros)
            if result is True:
                return result
            kakuros.curr_assignments.pop(v)
            kakuros.board[v[0]][v[1]] = ''
            kakuros.domains = pre_k

    return False


matrix = [
    ['X', 'X', '11\\', '5\\', 'X', '15\\', '15\\', 'X'],
    ['X', '3\\3', '', '', '4\\17', '', '', 'X'],
    ['\\22', '', '', '', '', '', '', 'X'],
    ['\\3', '', '', '11\\4', '', '', '10\\', 'X'],
    ['X', '\\8', '', '', '7\\3', '', '', '8\\'],
    ['X', 'X', '4\\4', '', '', '3\\4', '', ''],
    ['X', '\\21', '', '', '', '', '', ''],
    ['X', '\\3', '', '', '\\4', '', '', 'X']
]


def solve_kakuros(k):
    start = time.time()
    k.get_info()
    result = backtrack(k)
    end = time.time()
    if result is False:
        print("No solution")
    print("Time: %.2f" % (end - start))

def main():
    k = Kakuros(matrix, variable_ordering=NORMAL)
    thread = threading.Thread(target=solve_kakuros, args=[k])
    thread.start()
    #time.sleep(0.5)
    graphic.graphic(k)


if __name__== "__main__":
    main()