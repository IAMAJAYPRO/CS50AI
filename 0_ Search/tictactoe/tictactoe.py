"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    ct = 0
    for row in board:
        for item in row:
            if not item is EMPTY:
                ct += 1
    return X if ct % 2 == 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    li = set()
    size = len(board)
    for row in range(size):
        for col in range(size):
            if board[row][col] is EMPTY:
                li.add((row, col))
    return li


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    size = len(board)
    new_board = [[item for item in row] for row in board]
    if new_board[action[0]][action[1]] is not EMPTY:
        raise ValueError("Already filled action error")
    if not all((0 <= x < size for x in action)):
        raise IndexError("Out of bounds actions")
    new_board[action[0]][action[1]] = player(new_board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    size = len(board)
    for row in board:
        # horizontal checks
        if all((item == row[0]) for item in row) and row[0] != EMPTY:
            return row[0]
    for i in range(size):
        # vertical checks
        if all((board[j][i] == board[0][i] for j in range(size))) and board[0][i] != EMPTY:
            return board[0][i]
    # diagonals
    if (all([board[i][i] == board[0][0] for i in range(size)]) or
            all([board[i][2-i] == board[0][2] for i in range(size)])) and board[1][1] != EMPTY:
        return board[1][1]

    # no winner auto return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return True if winner(board) or all((EMPTY not in row) for row in board) else False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    won = winner(board)
    if won == X:
        return 1
    elif won == O:
        return -1
    else:
        return 0


def min_(iterable, key=NotImplementedError):
    m_nu = 2
    for num in iterable:
        if num == -1:
            return -1
        m_nu = min(m_nu, num)
    return m_nu


def max_(iterable, key=NotImplementedError):
    m_nu = -2
    for num in iterable:
        if num == 1:
            return 1
        m_nu = max(m_nu, num)
    return m_nu


def best_val(board, cur_player=None):
    if terminal(board):
        return utility(board)
    if not cur_player:
        cur_player = player(board)
    if cur_player is X:
        return max_((best_val(result(board, action), X if cur_player == O else O) for action in actions(board)))
    else:
        return min_((best_val(result(board, action), X if cur_player == O else O) for action in actions(board)))


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    acts = list(actions(board))
    values = []
    cur_player = player(board)
    for action in acts:
        val = best_val(result(board, action))
        if cur_player == X:
            if val == 1:
                return action
            values.append(val)

        else:
            if val == -1:
                return action
            values.append(val)
    if cur_player == X:
        return acts[values.index(max(values))]
    else:
        return acts[values.index(min(values))]
