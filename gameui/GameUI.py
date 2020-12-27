import math
from threading import Thread

import pygame
from pygame import sysfont, Color

from gameui.Assets import Assets, Colors
from gameui.Config import Config
from gameui.Hexagon import Hexagon
from hexcore.Board import Team, Piece
from hexcore.Game import Game
from hexcore.Player import Human, AI


class Utils:
    """工具类"""

    @staticmethod
    def get_team_color(team: Team):
        """获取队伍对应的颜色"""
        if team == Team.RED:
            return Colors.RED
        elif team == Team.BLUE:
            return Colors.BLUE
        else:
            return Colors.WHITE


class GameUI:
    """游戏的UI界面"""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(Config.window_title)
        pygame.display.set_icon(Assets.img_logo)
        pygame.sysfont.initsysfonts()
        pygame.font.init()
        pygame.fastevent.init()
        self.clock = pygame.time.Clock()
        self.game = None
        self.game_thread = None
        self.game_started = False  # 游戏开始了吗

        # 计算游戏框大小
        # width = (3n-1)*d*cos30, height = (n+1)*d+(n-1)*d*cos60
        n, d = Config.board_size, Config.hexagon_length
        self.width = int((3 * n - 1) * d * math.cos(math.pi / 6))
        self.height = int((n + 1) * d + (n - 1) * d * math.cos(math.pi / 3))
        self.screen = pygame.display.set_mode([self.width, self.height])
        self.font = pygame.font.SysFont(Config.font_family, Config.font_size)

    def render_text_center(self, text: str, y: int, color: Color) -> pygame.font:
        """渲染字体, 在屏幕中心显示"""
        x = (self.width - Config.font_size / 2 * len(text)) // 2
        text = self.font.render(text, True, color)
        self.screen.blit(text, (x, y))
        return text

    def event_handle(self):
        """事件消息处理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            # 消息转发给其它线程, 使用 fastevent 获取
            pygame.fastevent.post(event)
        # 界面变化部分重绘
        pygame.display.flip()

    def draw_welcome_ui(self):
        """游戏欢迎界面"""
        self.screen.fill(Colors.WHITE)  # 设置背景颜色
        self.render_text_center("[ Hex Game ]", self.height // 5, Colors.BLACK)
        surf_start_rect = Assets.surf_start.get_rect()  # 开始游戏图片对应的矩形
        surf_start_rect.move_ip((self.width - Assets.surf_start.get_width()) / 2, self.height - 200)  # 移动矩形到屏幕底下
        self.screen.blit(Assets.surf_start, surf_start_rect)

        # 点击开始进入游戏
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if surf_start_rect.collidepoint(x, y):
                    self.game_started = True
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    def draw_game_board(self):
        """游戏棋盘界面"""
        # 画出棋盘上下左右边界矩形
        n = Config.board_size  # 棋盘一行的六边形数量
        d = Config.hexagon_length  # 六边形边长
        rect_width = (2 * n - 1) * d * math.cos(math.pi / 6)  # 上下矩形的宽度
        rect_height = d * math.sin(math.pi / 6)  # 上下矩形的高度
        bt_rect_start_x = n * d * math.cos(math.pi / 6)  # 底部矩形的起点 x 坐标
        bt_rect_start_y = self.height - rect_height  # 底部矩形的起点 y 坐标
        # 左右先画, 防止覆盖上下矩形部分区域
        pygame.draw.rect(self.screen, Colors.BLUE, [0, rect_height, bt_rect_start_x, self.height])  # 左侧矩形
        pygame.draw.rect(self.screen, Colors.BLUE, [rect_width, 0, self.width, self.height])  # 右侧背景
        pygame.draw.rect(self.screen, Colors.RED, [0, 0, rect_width, rect_height])  # 上方矩形
        pygame.draw.rect(self.screen, Colors.RED,
                         [bt_rect_start_x, bt_rect_start_y, self.width, self.height])  # 下方矩形
        # 画出棋盘
        for row in range(Config.board_size):
            for col in range(Config.board_size):
                # 按棋盘矩阵的数据渲染棋盘颜色
                team = self.game.board[row][col].team
                hexagon = Hexagon(self.screen, row, col)
                hexagon.draw(Utils.get_team_color(team))
                # 动态绑定棋子与六边形对象
                self.game.board[row][col].hexagon = hexagon

    def draw_game_win_ui(self):
        """赢了"""
        win_team = self.game.judge.get_winner_team()
        self.screen.fill(Colors.WHITE)
        self.screen.blit(Assets.surf_game_win, [(self.width - Assets.surf_game_win.get_width()) / 2, self.height / 6])
        self.render_text_center(f"Winner: {win_team}", self.height - 100, Colors.BLACK)

    def draw_winner_path(self):
        """高亮胜利者路线"""
        path = self.game.judge.get_winner_path()
        for row, col in path:
            piece = self.game.board[row][col]
            if hasattr(piece, "hexagon"):
                piece.hexagon.draw(Colors.YELLOW)

    def game_loop(self):
        """游戏主体的事件循环"""
        # 鼠标悬浮事件检测, 如果这个位置没有棋子, 就设置其颜色为当前下棋方的颜色
        x, y = pygame.mouse.get_pos()
        cur_team = self.game.get_current_player().team
        for piece in self.game.board.items():
            if not hasattr(piece, "hexagon"):
                continue  # 暂未绑定六边形
            if piece.hexagon.collidepoint(x, y) and piece.team == Team.NONE:
                piece.hexagon.draw(Utils.get_team_color(cur_team))

    def when_human_operation(self):
        """人类玩家操作时的回调函数, 等待UI点击事件发生"""
        while True:
            # 改函数作为回调被后台线程的 game 对象调用, 为了监听主线程的事件循环, 需要使用 fastevent
            event = pygame.fastevent.wait()  # 阻塞, 等待鼠标点击事件发生
            if event.type != pygame.MOUSEBUTTONDOWN:
                continue
            x, y = pygame.mouse.get_pos()
            player = self.game.get_current_player()  # 当前准备下棋的玩家
            for piece in self.game.board.items():
                if piece.hexagon.collidepoint(x, y):  # 玩家选择了一个落子点
                    new_piece = Piece(*piece.hexagon.get_row_col())
                    if not player.set_piece(new_piece):  # 如果落子成功, 棋盘数据被修改, 后面会自动重绘
                        print(f"{player.team}: 落子失败 at {x, y} -> {piece.row, piece.col}")  # 落子失败
                    return None  # 落子成功, 退出循环

    def start_game_thread(self):
        """游戏线程"""
        if self.game_thread:
            return  # 已经启动

        p1, p2 = None, None
        if Config.game_mode == 1:
            p1 = Human(Team.RED)
            p2 = Human(Team.BLUE)
            p1.bind_play_operation(self.when_human_operation)
            p2.bind_play_operation(self.when_human_operation)
        elif Config.game_mode == 2:
            p1 = Human(Team.RED)
            p2 = AI(Team.BLUE)
            p1.bind_play_operation(self.when_human_operation)
        elif Config.game_mode == 3:
            p1 = AI(Team.BLUE)
            p2 = AI(Team.RED)

        self.game = Game(Config.board_size)
        self.game.set_player_one(p1)
        self.game.set_player_two(p2)
        self.game_thread = Thread(target=self.game.start)
        self.game_thread.start()

    def start(self):
        """开始游戏"""
        while True:
            self.clock.tick(Config.fps)
            # 游戏没有开始, 显示欢迎界面
            if not self.game_started:
                self.draw_welcome_ui()
            else:
                self.start_game_thread()
                self.draw_game_board()
                if not self.game.judge.has_winner():  # 目前无人获胜
                    self.game_loop()
                else:  # 有人赢了
                    self.draw_winner_path()
                    pygame.display.flip()  # 立刻重绘界面
                    pygame.time.wait(2000)
                    self.draw_game_win_ui()
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    self.game_started = False
                    self.game_thread = None
            # 事件处理, 界面重绘
            self.event_handle()
