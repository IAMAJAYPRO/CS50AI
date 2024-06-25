import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = [[False]*self.width for _ in range(self.height)]
        """for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)"""

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell: tuple[int, int]):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell: tuple[int, int]):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __sub__(self, other):
        if not other.issubset(self):
            raise LookupError("Set is not subset of other")
        new_cells = self.cells-other.cells
        new_ct = self.count-other.count
        return Sentence(new_cells, new_ct)

    def issubset(self, other):
        return self.cells.issubset(other.cells)

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell not in self.cells:
            return
        assert self.count >= 1
        self.cells.remove(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge: list[Sentence] = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        neighbours = set()
        for i in range(-1, 2):
            for j in range(-1, 2):
                h, k = cell[0]+i, cell[1]+j
                if not (0 <= h < self.height and 0 <= k < self.width):
                    continue

                if (h, k) in self.mines:
                    count -= 1
                    continue
                elif (h, k) in self.safes:
                    continue
                elif (h, k) != cell:
                    neighbours.add((h, k))
        self.moves_made.add(cell)
        self.mark_safe(cell)
        if not neighbours:
            return
        else:
            self.knowledge.append(Sentence(neighbours, count))
        # step 4 and 5 remin
        loop = True
        while loop:
            new_safes = set()
            new_mines = set()
            for sent in self.knowledge:

                new_safes.update(
                    safe for safe in sent.known_safes() if safe not in self.safes)
                new_mines.update(
                    mine for mine in sent.known_mines() if mine not in self.mines)
            loop: bool = new_safes or new_mines
            """
            print(new_mines,len(new_mines))
            print(new_safes,len(new_safes))
            """
            for cell in new_safes:
                self.mark_safe(cell)
            for cell in new_mines:
                self.mark_mine(cell)

            new_safes = set()
            new_mines = set()
            for sent1 in self.knowledge:
                for sent2 in self.knowledge:
                    if sent1 == sent2:
                        continue
                    if sent1.issubset(sent2):
                        new_sent = sent2-sent1
                        new_safes.update(
                            safe for safe in new_sent.known_safes() if safe not in self.safes)
                        new_mines.update(
                            mine for mine in new_sent.known_mines() if mine not in self.safes)
            loop: bool = new_safes or new_mines
            for cell in new_safes:
                self.mark_safe(cell)
            for cell in new_mines:
                self.mark_mine(cell)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                cell = i, j
                if cell not in self.mines and cell not in self.moves_made:
                    return cell
