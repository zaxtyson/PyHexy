class Config:
    """游戏配置"""

    fps = 30  # 帧率
    window_title = "Hex Game"
    font_family = "Times New Roman"
    font_size = 50
    hexagon_length = 30  # 六边形边长
    hexagon_line_thickness = 2  # 六边形边框厚度

    # 游戏模式
    board_size = 11  # 棋盘大小 NxN
    game_mode = 3  # 1 双人模式, 2 人机模式, 3 机器对抗
    first_player = 0  # 先手, 0 红方, 1蓝方
    ai_level = 1  # 蒙特卡洛搜索时间上限/秒
