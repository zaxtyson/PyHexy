from enum import Enum
from typing import List, Iterable


class Team(Enum):
    NONE = 0
    RED = -1
    BLUE = 1


class Piece:
    """棋子"""

    def __init__(self, row: int, col: int, team: Team = Team.NONE):
        self.row = row
        self.col = col
        self.team = team  # 棋子所属队伍, 默认无

    def set_team(self, team: Team):
        """设置棋子所属队伍"""
        self.team = team

    def __repr__(self):
        return f"{self.row, self.col, self.team}"


class Board:
    """棋盘"""

    def __init__(self, board_size: int):
        # 初始化空棋盘 board_size x board_size
        self.size = board_size
        self.board = None
        self.reset()

    def reset(self):
        """清空棋盘"""
        self.board = [[Piece(row, col) for col in range(self.size)] for row in range(self.size)]

    def __iter__(self):
        """支持迭代棋盘对象"""
        return iter(self.board)

    def __getitem__(self, item) -> List[Piece]:
        """支持 operator[]"""
        return self.board[item]

    def items(self) -> Iterable[Piece]:
        """获取全部棋子数组, 一次性遍历整个二维数组, 返回一个生成器"""
        for row in self.board:
            for piece in row:
                yield piece

    def state(self):
        """获取棋盘状态, 返回二维数组"""
        return [[p.team.value for p in row] for row in self]

    def set_piece(self, piece: Piece) -> bool:
        """落子, 成功返回 True, 失败返回 False"""
        row, col = piece.row, piece.col
        if row >= self.size or row < 0:  # 边界检查
            return False
        if col >= self.size or col < 0:
            return False
        if self[row][col].team != Team.NONE:
            return False  # 这个位置有棋子了
        self[row][col] = piece
        return True
