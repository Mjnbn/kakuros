import threading
import time
from collections import defaultdict
import copy
import graphic
import csp

class Kakuros:
    def __init__(self, board):
        self.board = board
        self.variables = []
        self.raw_domains = defaultdict(list)
        self.neighbors = defaultdict(set)
        self.vertical_neighbors = defaultdict(set)
        self.horizontal_neighbors = defaultdict(set)
        self.vertical_sum = {}
        self.horizontal_sum = {}
        self.constraints = {}
        self.curr_assignments = {}
        self.domains = {}
        self.domain_history = []
        self.get_info()

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

        for v in variables:
            if v not in self.curr_assignments:
                max_number = min(9, self.vertical_sum[v] if v in self.vertical_sum else 9, self.horizontal_sum[v] if v in self.horizontal_sum else 9)
                self.domains[v] = set(range(1, max_number + 1))

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

    def get_num_consistent_values(self, var, value):
        cnt = 0
        for neighbor in self.neighbors[var]:
            if neighbor in self.curr_assignments:
                continue
            if value in self.domains[neighbor]:
                cnt += 1
        return cnt

    def set_value(self, var, val):
        self.curr_assignments[var] = val
        self.board[var[0]][var[1]] = chr(val + ord('0'))
        for v in self.neighbors[var]:
            if val in self.domains[v]:
                self.domains[v].remove(val)
                self.domain_history.append((var, v, val))

    def remove_value(self, var, val):
        self.board[var[0]][var[1]] = ''
        self.curr_assignments.pop(var)
        while len(self.domain_history) > 0 and self.domain_history[-1][0] == var:
            (v1, v2, val) = self.domain_history.pop()
            self.domains[v2].add(val)        


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
            kakuros.remove_value(v, d)

    return False


matrix = [
    ['X', 'X', 'X', '3\\', '23\\', '45\\', '6\\', 'X', 'X', 'X'],
    ['X', 'X', '\\12', '', '', '', '', '4\\', 'X', 'X'],
    ['X', '20\\', '32\\21', '', '', '', '', '', '15\\', 'X'],
    ['\\3', '', '', '17\\15', '', '', '5\\4', '', '', '16\\'],
    ['\\24', '', '', '', '16\\3', '', '', '4\\7', '', ''],
    ['\\45', '', '', '', '', '', '', '', '', ''],
    ['\\17', '', '', '13\\17', '', '', '24\\6', '', '', ''],
    ['X', '\\16', '', '', '17\\15', '', '', '13\\6', '', ''],
    ['X', 'X', '\\32', '', '', '', '', '', 'X', 'X'],
    ['X', 'X', 'X', '\\30', '', '', '', '', 'X', 'X']
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
    k = Kakuros(matrix)
    # thread = threading.Thread(target=solve_kakuros, args=[k])
    # thread.start()
    #time.sleep(0.5)
    # graphic.graphic(k)

    start = time.time()
    c = csp.CSP(k, variable_ordering=csp.MCV, value_ordering=csp.LCV)
    c.solve()
    # graphic.graphic(k)
    end = time.time()
    print("Time: %.6f" % (end - start))


if __name__== "__main__":
    main()