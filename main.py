import threading
import time
from collections import defaultdict
import copy
import graphic
import csp
import test


class Kakuros:
    def __init__(self, board):
        self.number_of_assignments = 0
        self.board = board
        self.variables = []
        self.raw_domains = defaultdict(list)
        self.neighbors = defaultdict(set)
        self.vertical_neighbors = defaultdict(set)
        self.horizontal_neighbors = defaultdict(set)
        self.vertical_sum = {}
        self.horizontal_sum = {}
        self.vertical_sum_so_far = {}
        self.horizontal_sum_so_far = {}
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
                if cell != "X" and "\\" not in cell:
                    if cell != "":
                        self.curr_assignments[(i, j)] = int(cell)
                    else:
                        variables.append((i, j))
                if "\\" in cell:
                    index = cell.find("\\")  # Find the index of '\\'

                    if index > 0:  # n\
                        number_before = int(cell[:index])
                        relevant_vars = []
                        k = i + 1
                        while (
                            k < len(self.board)
                            and self.board[k][j] != "X"
                            and "\\" not in self.board[k][j]
                        ):
                            relevant_vars.append((k, j))
                            k += 1
                        self.get_info_helper(
                            number_before, relevant_vars, is_vertical=False
                        )

                    if index < len(cell) - 1:  # \n
                        number_after = int(cell[index + 1 :])
                        relevant_vars = []
                        k = j + 1
                        while (
                            k < len(self.board[i])
                            and self.board[i][k] != "X"
                            and "\\" not in self.board[i][k]
                        ):
                            relevant_vars.append((i, k))
                            k += 1
                        self.get_info_helper(
                            number_after, relevant_vars, is_vertical=True
                        )

        for c, v in self.curr_assignments.items():
            self.set_value(c, v)

        for v in variables:
            if v not in self.curr_assignments:
                max_number = min(
                    9,
                    self.vertical_sum[v] if v in self.vertical_sum else 9,
                    self.horizontal_sum[v] if v in self.horizontal_sum else 9,
                )
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
            if (
                cnt == len(self.vertical_neighbors[var])
                and sum_so_far < self.vertical_sum[var]
            ):
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
            if (
                cnt == len(self.horizontal_neighbors[var])
                and sum_so_far < self.horizontal_sum[var]
            ):
                return False

        return True

    def get_domain(self, var):
        return [
            x
            for x in self.domains[var]
            if x
            <= min(
                self.vertical_sum[var] - self.vertical_sum_so_far.get(var, 0)
                if var in self.vertical_sum
                else 9,
                self.horizontal_sum[var] - self.horizontal_sum_so_far.get(var, 0)
                if var in self.horizontal_sum
                else 9,
            )
        ]

    def get_min_sum(self, var):
        return min(
            [
                self.vertical_sum[var] - self.vertical_sum_so_far.get(var, 0)
                if var in self.vertical_sum
                else 1000
            ],
            [
                self.horizontal_sum[var] - self.horizontal_sum_so_far.get(var, 0)
                if var in self.horizontal_sum
                else 1000
            ],
        )

    def get_num_consistent_values(self, var, value):
        cnt = 0
        for neighbor in self.neighbors[var]:
            if neighbor in self.curr_assignments:
                continue
            if value in self.domains[neighbor]:
                cnt += 1
        return cnt

    def set_value(self, var, val):
        self.number_of_assignments += 1
        self.curr_assignments[var] = val
        self.board[var[0]][var[1]] = chr(val + ord("0"))
        for v in self.neighbors[var]:
            if val in self.domains[v]:
                self.domains[v].remove(val)
                self.domain_history.append((var, v, val))
        if var in self.vertical_sum:
            self.vertical_sum_so_far[var] = self.vertical_sum_so_far.get(var, 0) + val
        if var in self.horizontal_sum:
            self.horizontal_sum_so_far[var] = (
                self.horizontal_sum_so_far.get(var, 0) + val
            )

    def remove_value(self, var, val):
        self.board[var[0]][var[1]] = ""
        self.curr_assignments.pop(var)
        while len(self.domain_history) > 0 and self.domain_history[-1][0] == var:
            (v1, v2, val) = self.domain_history.pop()
            self.domains[v2].add(val)
        if var in self.vertical_sum:
            self.vertical_sum_so_far[var] -= val
        if var in self.horizontal_sum:
            self.horizontal_sum_so_far[var] -= val


def main():
    for name, board in test.boards:
        # if name != "hard2":
        #     continue
        k = Kakuros(board)
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
