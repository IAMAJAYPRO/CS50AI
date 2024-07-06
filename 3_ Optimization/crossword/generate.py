import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword: Crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment: dict[Variable, str]) -> list[list[None | str]]:
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var in self.domains:
            length = var.length
            self.domains[var] = set(
                word for word in self.domains[var] if len(word) == length)

    def revise(self, x: Variable, y: Variable):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        for word in self.domains[x].copy():
            overlap = self.crossword.overlaps[x, y]
            constraint_overlap = not any(
                word[overlap[0]] == w[overlap[1]] for w in self.domains[y]) if overlap else True
            constraint = not (self.domains[y]-{word}) or constraint_overlap
            if constraint:  # y is empty
                self.domains[x].remove(word)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        from collections import deque
        queue = deque(arcs if arcs is not None else (
            x for x in self.crossword.overlaps if self.crossword.overlaps[x]))
        while queue:
            v1, v2 = queue.popleft()
            if self.revise(v1, v2):
                if not self.domains[v1]:
                    return False
                for var in self.crossword.neighbors(v1):
                    if var != v2:
                        queue.append((var, v1))
        return True

    def assignment_complete(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return all(var in assignment for var in self.crossword.variables)

    def consistent(self, assignment: dict[Variable, str]):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for v0 in assignment:
            if v0 in assignment:
                if len(assignment[v0]) != v0.length:
                    return False
                for v1 in self.crossword.neighbors(v0):
                    if v1 in assignment:
                        if len(assignment[v1]) != v1.length:
                            return False
                        overlap = self.crossword.overlaps[v0, v1]
                        if assignment[v0][overlap[0]] != assignment[v1][overlap[1]]:
                            return False
        return True

    def order_domain_values(self, var, assignment: dict[Variable, str]):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)

        def sort_fun(word):
            ct = 0
            for v2 in neighbors:
                if v2 in assignment:
                    continue
                (i, j) = self.crossword.overlaps[var, v2]
                # for every word in neighbors domain check if its compitable word
                ct += sum(1 for dm_wd in self.domains[v2]
                          if word[i] != dm_wd[j])
            return ct

        li = sorted(self.domains[var], key=sort_fun)
        return li

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [
            var for var in self.crossword.variables if var not in assignment]
        min_vals = min(len(self.domains[var]) for var in unassigned)
        mins = [var for var in unassigned if len(
            self.domains[var]) == min_vals]
        return min(mins, key=lambda var: len(self.crossword.neighbors(var)))

    def backtrack(self, assignment: dict[Variable, str]):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for word in self.order_domain_values(var, assignment):
            assign_copy = assignment.copy()
            assign_copy[var] = word
            if self.consistent(assign_copy):
                result = self.backtrack(assign_copy)
                if result:  # success
                    return result
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="CS50 crossword project.",
        epilog="Project completed by @IAMAJAYPRO",
        usage="Usage: python generate.py structure words [output]\nExample:\n  python generate.py data/structure1.txt data/words1.txt output.png")
    parser.add_argument('structure', type=str,
                        help='The structure to use :file')
    parser.add_argument('words', type=str, help='The words to use :file')
    parser.add_argument('output', nargs='?', default=None,
                        help='The output file (optional)')
    args = parser.parse_args()
    # Check usage
    """if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")"""

    # Parse command-line arguments
    structure = args.structure
    words = args.words
    output = args.output

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
