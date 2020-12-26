import math


class Config:
    """游戏配置"""

    fps = 30  # 帧率
    window_title = "Hex Game"
    font_family = "Times New Roman"
    font_size = 50
    board_size = 11  # 棋盘大小 NxN
    hexagon_length = 30  # 六边形边长
    hexagon_line_thickness = 2  # 六边形边框厚度

    # 游戏模式
    game_mode = 2  # 1 双人模式, 2 人机模式, 3 机器对抗
    first_player = 0  # 先手, 0 红方, 1蓝方
    ai_level = 2  # AI 的等级, 越大越强(蒙特卡洛搜索时间上限/秒)

    # 计算游戏框大小
    # width = (3n-1)*d*cos30
    # height = (n+1)*d+(n-1)*d*cos60
    width = int((3 * board_size - 1) * hexagon_length * math.cos(math.pi / 6))
    height = int((board_size + 1 + (board_size - 1) * math.cos(math.pi / 3)) * hexagon_length)
