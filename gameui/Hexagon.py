import math
import pygame
from pygame import Color
from pygame.rect import Rect
from gameui.Assets import Colors
from gameui.Config import Config


class Hexagon:
    """六边形对象"""

    def __init__(self, screen: pygame.display, row: int, col: int):
        """初始化六边形, 第几行第"""
        self.screen = screen
        self.row = row
        self.col = col
        self.points = []  # 六个顶点坐标
        self.line_thickness = Config.hexagon_line_thickness  # 六边形边框厚度
        self.rect: Rect = None  # 用于碰撞检测的矩形区域

        # 通过数组下标计算六边形中心坐标 (i, j) -> (cx, cy)
        # 算出来的公式是:
        # X(i,j) = (i+2*j+1)*d*cos30
        # Y(i,j) = (i+1)*d + i*d*sin30
        d = Config.hexagon_length  # 边长
        cx = (row + 2 * col + 1) * d * math.cos(math.pi / 6)
        cy = (row + 1) * d + row * d * math.sin(math.pi / 6)

        # 通过六边形中心坐标计算六个顶点的坐标
        cos30 = math.cos(math.pi / 6)
        sin30 = math.sin(math.pi / 6)
        sin60 = math.sin(math.pi / 3)

        self.points = [
            (cx, cy - d),  # P0, 中心点上方的顶点, 按顺时针编号
            (cx + d * cos30, cy - d * sin30),  # P1, 右上角顶点
            (cx + d * cos30, cy + d * sin30),
            (cx, cy + d),
            (cx - d * cos30, cy + d * sin30),
            (cx - d * cos30, cy - d * sin30),  # P5, 左上角顶点
        ]
        # 创建用于碰撞检测的矩形区域, 包括两个矩形
        # 第一个矩形覆盖 P5 到 P2 区域, 第二个矩形用于弥补上下三角形空白区域
        # 从左上角边的中点位置到右下角边的中点位置
        rect_x, rect_y = self.points[5]  # 六边形左上角的顶点作为矩形的起点
        rect_width, rect_height = 2 * d * sin60, d  # 矩形的宽和高
        rect_h = Rect(rect_x, rect_y, rect_width, rect_height)
        rect_x, rect_y = rect_x + d / 2 * cos30, rect_y - d / 2 * sin30  # 竖直矩形的起点, 六边形左上角边的中点
        rect_width, rect_height = d * cos30, d + d * sin30  # 竖直矩形的宽和高
        rect_v = Rect(rect_x, rect_y, rect_width, rect_height)
        self.rect = rect_h.union(rect_v)  # 合并区域

    def get_row_col(self):
        """获取行列坐标"""
        return self.row, self.col

    def draw(self, fill_color: Color, board_color: Color = Colors.BLACK):
        """绘制六边形"""
        pygame.draw.polygon(self.screen, fill_color, self.points)  # 填充六边形内部颜色
        pygame.draw.polygon(self.screen, board_color, self.points, self.line_thickness)  # 重绘边框

    def collidepoint(self, x: float, y: float) -> int:
        """检测坐标是否在六边形内部"""
        # 懒得计算点到六条边的距离了, 这里直接用矩形区域模拟
        return self.rect.collidepoint(x, y)
