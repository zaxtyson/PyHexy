from typing import List, Tuple

from hexcore.Algorithms import BFS
from hexcore.Board import Board, Team


class Judge:
    """裁判"""

    def __init__(self):
        self.board: Board = None
        self.winner_path: List = []  # 获胜者的其中路径
        self.winner_team: Team = Team.NONE  # 获胜的队伍

    def reset(self):
        """清空裁判状态"""
        self.winner_team = Team.NONE
        self.winner_path = []

    def set_board(self, board):
        self.board = board

    def has_winner(self):
        """是否有人获胜"""
        return self.winner_team != Team.NONE

    def check_winner(self):
        """检查棋盘状态, 是否出现获胜者"""
        bfs = BFS(self.board.state())

        red_path = bfs.find_red_path()
        blue_path = bfs.find_blue_path()

        if red_path:
            self.winner_path = red_path  # 记录胜者棋子路径
            self.winner_team = Team.RED  # 红方胜利
            return

        if blue_path:
            self.winner_path = blue_path
            self.winner_team = Team.BLUE  # 蓝方胜
            return

    def get_winner_team(self) -> Team:
        """获取获胜的一方队伍"""
        return self.winner_team

    def get_winner_path(self) -> List[tuple]:
        """获取获胜方的路径列表"""
        return self.winner_path
