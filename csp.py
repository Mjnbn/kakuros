NORMAL = 0
MCV = 1
LCV = 2

class CSP:
    def __init__(self, kakuros, variable_ordering=None, value_ordering=None):
        """
            filtering: None, Arc_Consistency, or Forward_Checking
            variable_ordering: None, MCV
            value_ordering: None, LCV
        """
        self.kakuros = kakuros
        self.variable_ordering = variable_ordering
        self.value_ordering = value_ordering

    def solve(self):
        """
            Returns True if a solution is found, False otherwise
        """
        return self.backtrack()

    def get_next_variable(self):
        if self.variable_ordering == NORMAL:
            for v in self.kakuros.variables:
                if v not in self.kakuros.curr_assignments:
                    return v
            return None
        elif self.variable_ordering == MCV:
            mcv = None
            for v in self.kakuros.variables:
                if v not in self.kakuros.curr_assignments:
                    if mcv is None or len(self.kakuros.domains[v]) < len(self.kakuros.domains[mcv]):
                        mcv = v
            return mcv

    def backtrack(self):
        """
            Returns True if a solution is found, False otherwise
        """
        if self.get_next_variable() is None:
            return True

        variable = self.get_next_variable()

        var = self.get_next_variable()

        domain = self.kakuros.domains[var]
        if self.value_ordering == LCV:
            domain = sorted(domain, key=lambda val: self.kakuros.get_num_consistent_values(var, val))

        for val in domain:
            if self.kakuros.is_consistent(var, val):
                self.kakuros.set_value(var, val)
                if self.backtrack():
                    return True
                self.kakuros.remove_value(var, val)
        return False