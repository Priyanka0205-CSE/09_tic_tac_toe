"""
GameEngine: owns the board, turn state, scoreboard, and round-end logic.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py).

Controls:
    Click  - place your symbol
    R      - restart the current round (scoreboard is kept)
    M      - reset the whole match (scoreboard is cleared)
    F      - choose who goes first (X or O), applies from the next round
"""

import pygame

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.small_font = pygame.font.SysFont("consolas", 16)
        self.score = {'X': 0, 'O': 0, 'draw': 0}
        self.first_player = 'X'      # who starts the next round
        self.new_round()

    # ---------- round / match control ----------

    def new_round(self):
        """Clear the board but keep the scoreboard."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.first_player
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (draw, only valid when round_over)
        self._maybe_take_computer_turn()   # if O starts, the computer moves first

    def reset_match(self):
        """Clear the scoreboard and start a fresh round."""
        self.score = {'X': 0, 'O': 0, 'draw': 0}
        self.new_round()

    def toggle_first_player(self):
        """Takes effect on the next round."""
        self.first_player = 'O' if self.first_player == 'X' else 'X'

    # ---------- moves ----------

    def handle_click(self, pos):
        if self.round_over:
            return   # round has ended - ignore all clicks
        if self.current_player != HUMAN_SYMBOL:
            return   # not your turn
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return   # cell already taken - reject, nothing changes
        self.board[row][col] = self.current_player
        self.check_round_end()
        if not self.round_over:
            self.current_player = COMPUTER_SYMBOL
            self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        if not self.round_over:
            self.current_player = HUMAN_SYMBOL

    def handle_keydown(self, key):
        if key == pygame.K_r:
            self.new_round()
        elif key == pygame.K_m:
            self.reset_match()
        elif key == pygame.K_f:
            self.toggle_first_player()

    def check_round_end(self):
        # Check for a winner FIRST, so a winning move that fills the
        # board is still scored as a win and not a draw.
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.score[winner] += 1
        elif is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.score['draw'] += 1

    # ---------- drawing ----------

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)

        if self.round_over:
            turn_label = "Round over"
        elif self.current_player == HUMAN_SYMBOL:
            turn_label = "Your turn (X)"
        else:
            turn_label = "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 15))

        score_text = f"X: {self.score['X']}  O: {self.score['O']}  Draws: {self.score['draw']}"
        renderer.draw_text(surface, font, score_text, (10, 55))

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, text)

        renderer.draw_text(surface, self.small_font, "R: restart round   M: reset match", (10, 545))
        renderer.draw_text(surface, self.small_font, f"F: first player (next round): {self.first_player}", (10, 575))