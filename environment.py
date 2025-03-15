import numpy as np

class SimpleEnvironment:
    def __init__(self):
        self.state = 0  # Initial state

    def get_possible_actions(self):
        return ["move_left", "move_right", "stay"]

    def apply_action(self, action):
        if action == "move_left":
            self.state -= 1
        elif action == "move_right":
            self.state += 1
        return self.state

    def is_terminal(self):
        return self.state >= 10 or self.state <= -10

    def reset(self):
        self.state = 0
        return self.state

class BreakthroughEnvironment:
    def __init__(self):
        self.board = [[0] * 5 for _ in range(5)]  # 5x5 board
        self.current_player = 1  # 1 for White, -1 for Black
        self.state = (self.board, self.current_player)  # Represent state as a tuple

    def get_possible_actions(self):
        actions = []
        for x in range(5):
            for y in range(5):
                if self.board[x][y] == self.current_player:
                    actions.extend(self._get_moves(x, y))
        return actions

    def _get_moves(self, x, y):
        moves = []
        if self.current_player == 1:
            moves.append(("move_forward", x, y, x + 1, y))
        elif self.current_player == -1:
            moves.append(("move_forward", x, y, x - 1, y))
        return moves

    def apply_action(self, action):
        move_type, x1, y1, x2, y2 = action
        self.board[x2][y2] = self.board[x1][y1]
        self.board[x1][y1] = 0
        self.current_player *= -1  # Switch players
        self.state = (self.board, self.current_player)  # Update state
        return self.state

    def is_terminal(self):
        return any(row[0] == 1 for row in self.board) or any(row[-1] == -1 for row in self.board)

    def reset(self):
        self.board = [[0] * 5 for _ in range(5)]
        self.current_player = 1
        self.state = (self.board, self.current_player)
        return self.state

class ConnectFourEnvironment:
    def __init__(self):
        self.board = [[0] * 7 for _ in range(6)]  # 6x7 board
        self.current_player = 1  # 1 for Player 1, -1 for Player 2
        self.state = (self.board, self.current_player)

    def get_possible_actions(self):
        return [col for col in range(7) if self.board[0][col] == 0]

    def apply_action(self, action):
        for row in reversed(range(6)):
            if self.board[row][action] == 0:
                self.board[row][action] = self.current_player
                break
        self.current_player *= -1
        self.state = (self.board, self.current_player)
        return self.state

    def is_terminal(self):
        # Check for a win
        for row in range(6):
            for col in range(4):
                if self.board[row][col] != 0 and self.board[row][col] == self.board[row][col + 1] == self.board[row][col + 2] == self.board[row][col + 3]:
                    return True
        for col in range(7):
            for row in range(3):
                if self.board[row][col] != 0 and self.board[row][col] == self.board[row + 1][col] == self.board[row + 2][col] == self.board[row + 3][col]:
                    return True
        for row in range(3):
            for col in range(4):
                if self.board[row][col] != 0 and self.board[row][col] == self.board[row + 1][col + 1] == self.board[row + 2][col + 2] == self.board[row + 3][col + 3]:
                    return True
        for row in range(3):
            for col in range(3, 7):
                if self.board[row][col] != 0 and self.board[row][col] == self.board[row + 1][col - 1] == self.board[row + 2][col - 2] == self.board[row + 3][col - 3]:
                    return True
        # Check for a draw
        return all(self.board[0][col] != 0 for col in range(7))

    def reset(self):
        self.board = [[0] * 7 for _ in range(6)]
        self.current_player = 1
        self.state = (self.board, self.current_player)
        return self.state

class TicTacToeEnvironment:
    def __init__(self):
        self.board = [[0] * 3 for _ in range(3)]  # 3x3 board
        self.current_player = 1  # 1 for Player 1, -1 for Player 2
        self.state = (self.board, self.current_player)

    def get_possible_actions(self):
        return [(row, col) for row in range(3) for col in range(3) if self.board[row][col] == 0]

    def apply_action(self, action):
        row, col = action
        self.board[row][col] = self.current_player
        self.current_player *= -1
        self.state = (self.board, self.current_player)
        return self.state

    def is_terminal(self):
        # Check rows
        for row in range(3):
            if self.board[row][0] != 0 and self.board[row][0] == self.board[row][1] == self.board[row][2]:
                return True
        # Check columns
        for col in range(3):
            if self.board[0][col] != 0 and self.board[0][col] == self.board[1][col] == self.board[2][col]:
                return True
        # Check diagonals
        if self.board[0][0] != 0 and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return True
        if self.board[0][2] != 0 and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return True
        # Check for a draw
        return all(self.board[row][col] != 0 for row in range(3) for col in range(3))

    def reset(self):
        self.board = [[0] * 3 for _ in range(3)]
        self.current_player = 1
        self.state = (self.board, self.current_player)
        return self.state