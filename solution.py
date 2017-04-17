class Sudoku:

    rows = 'ABCDEFGHI'
    cols = '123456789'
    unitlist = None
    units = None
    peers = None
    assignments = []
    boxes = None

    def __init__(self):

        self.boxes = self.cross(self.rows, self.cols)
        row_units = [self.cross(r, self.cols) for r in self.rows]
        column_units = [self.cross(self.rows, c) for c in self.cols]
        square_units = [self.cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
        diag_units = [
            [r+c for r, c in zip(self.rows, self.cols)],
            [r+c for r, c in zip(self.rows, reversed(self.cols))],
        ]

        self.unitlist = row_units + column_units + square_units + diag_units
        self.units = dict((s, [u for u in self.unitlist if s in u]) for s in self.boxes)
        self.peers = dict((s, set(sum(self.units[s], [])) - set([s])) for s in self.boxes)

    def assign_value(self, values, box, value):
        """
        Please use this function to update your values dictionary!
        Assigns a value to a given box. If it updates the board record it.
        """

        # Don't waste memory appending actions that don't actually change any values
        if values[box] == value:
            return values

        values[box] = value
        if len(value) == 1:
            self.assignments.append(values.copy())
        return values

    def naked_twins(self, values):
        """Eliminate values using the naked twins strategy.
        Args:
            values(dict): a dictionary of the form {'box_name': '123456789', ...}
    
        Returns:
            the values dictionary with the naked twins eliminated from peers.
        """

        for box in values:
            # Find all instances of naked candidates
            for unit in self.units[box]:
                twins = {}
                for inner_box in unit:
                    inner_value = values[inner_box]
                    if inner_value in twins:
                        twins[inner_value].append(inner_box)
                    else:
                        twins[inner_value] = [inner_box]

                # Instead of twins, naked candidates method is used which also supports twins, triples and quads.
                naked_candidates = {k:v for k,v in twins.items() if len(v) > 1 and len(k) == len(v)}

                # Eliminate the naked candidates as possibilities for their peers
                for candidate_values, candidate_boxes in naked_candidates.items():
                    for value in candidate_values:
                        boxes_to_eliminate = [unit_box for unit_box in unit if unit_box not in candidate_boxes]
                        for box_to_eliminate in boxes_to_eliminate:
                            if value in values[box_to_eliminate]:
                                self.assign_value(values, box_to_eliminate, values[box_to_eliminate].replace(value, ''))

        return values

    def cross(self, A, B):
        "Cross product of elements in A and elements in B."
        return [a+b for a in A for b in B]

    def grid_values(self, grid):
        """
        Convert grid into a dict of {square: char} with '123456789' for empties.
        Args:
            grid(string) - A grid in string form.
        Returns:
            A grid in dictionary form
                Keys: The boxes, e.g., 'A1'
                Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
        """
        assert len(grid) == 81, "Input grid must be a string of length 81 (9x9)"
        grids = dict(zip(self.boxes, grid))
        for key, value in grids.items():
            if value == '.':
                grids[key] = self.cols
        return grids

    def display(self, values):
        """
        Display the values as a 2-D grid.
        Args:
            values(dict): The sudoku in dictionary form
        """
        digits = '123456789'

        width = 1 + max(len(values[s]) for s in self.boxes)

        line = '+'.join(['-' * (width * 3)] * 3)
        for r in self.rows:
            print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                          for c in digits))
            if r in 'CF': print(line)
        return

    def eliminate(self, values):
        """
            Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
            Input: A sudoku in dictionary form.
            Output: The resulting sudoku in dictionary form.
            """
        solved_values = [box for box in values.keys() if len(values[box]) == 1]
        for box in solved_values:
            digit = values[box]
            for peer in self.peers[box]:
                values = self.assign_value(values, peer, values[peer].replace(digit, ''))
        return values

    def only_choice(self, values):
        """
        Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
        Input: A sudoku in dictionary form.
        Output: The resulting sudoku in dictionary form.
        """
        for unit in self.unitlist:
            for digit in '123456789':
                dplaces = [box for box in unit if digit in values[box]]
                if len(dplaces) == 1:
                    values = self.assign_value(values, dplaces[0], digit)
        return values

    def reduce_puzzle(self, values):
        """
           Iterate eliminate() and naked_twins(), only_choice(). If at some point, there is a box with no available values, return False.
           If the sudoku is solved, return the sudoku.
           If after an iteration of both functions, the sudoku remains the same, return the sudoku.
           Input: A sudoku in dictionary form.
           Output: The resulting sudoku in dictionary form.
           """
        stalled = False
        while not stalled:
            solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
            values = self.eliminate(values)
            values = self.naked_twins(values)
            values = self.only_choice(values)
            solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
            stalled = solved_values_before == solved_values_after
            if len([box for box in values.keys() if len(values[box]) == 0]):
                return False
        return values

    def search(self, values):
        "Using depth-first search and propagation, create a search tree and solve the sudoku."
        values = self.reduce_puzzle(values)
        if values is False:
            return False ## Failed earlier
        if all(len(values[s]) == 1 for s in self.boxes):
            return values ## Solved!
        # Choose one of the unfilled squares with the fewest possibilities
        n,s = min((len(values[s]), s) for s in self.boxes if len(values[s]) > 1)
        # Now use recurrence to solve each one of the resulting sudokus, and
        for value in values[s]:
            new_sudoku = values.copy()
            new_sudoku[s] = value
            attempt = self.search(new_sudoku)
            if attempt:
                return attempt

    def solve(self, grid, display=False):
        """
        Find the solution to a Sudoku grid.
        Args:
            grid(string): a string representing a sudoku grid.
                Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        Returns:
            The dictionary representation of the final sudoku grid. False if no solution exists.
        """
        values = self.search(self.grid_values(grid))
        self.visualize()
        if display: self.display(values)
        return values

    def visualize(self):
        try:
            from visualize import visualize_assignments
            visualize_assignments(self.assignments)

        except SystemExit:
            pass
        except:
            print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')


if __name__ == '__main__':

    sudoku = Sudoku()
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    sudoku.solve(diag_sudoku_grid, display=True)