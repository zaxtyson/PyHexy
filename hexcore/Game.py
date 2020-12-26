from gameui.Config import Config
from hexcore.Board import Board, Team
from hexcore.Judge import Judge
from hexcore.Player import Player


class Game:
    def __init__(self, board_size: int):
        self.player1: Player = None
        self.player2: Player = None
        self.board = Board(board_size)
        self.judge = Judge()
        self.judge.set_board(self.board)
        self.current_turn = Team.RED if Config.first_player == 0 else Team.BLUE  # 先手队伍

    def set_player_one(self, player: Player):
        """设置1号玩家"""
        self.player1 = player
        self.player1.set_board(self.board)

    def set_player_two(self, player: Player):
        """设置2号玩家"""
        self.player2 = player
        self.player2.set_board(self.board)

    def get_current_player(self) -> Player:
        """获取当前下棋的玩家"""
        if self.player1.team == self.current_turn:
            return self.player1
        if self.player2.team == self.current_turn:
            return self.player2

    def start(self):
        """游戏开始"""
        # 每次游戏开始, 清空棋盘, 重置裁判状态
        self.board.reset()
        self.judge.reset()

        while not self.judge.has_winner():
            if self.current_turn == self.player1.team:
                self.player1.let_me_play()
                # self.board.show_state()
                self.current_turn = self.player2.team
            elif self.current_turn == self.player2.team:
                self.player2.let_me_play()
                # self.board.show_state()
                self.current_turn = self.player1.team
            self.judge.check_winner()  # 检查棋盘状态

        # 游戏结束
        winner = self.judge.get_winner_team()
        print("获胜者:", winner)
