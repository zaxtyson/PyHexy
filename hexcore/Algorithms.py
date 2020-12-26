from copy import deepcopy
from math import log, sqrt
from queue import Queue
from random import choice
from time import process_time
from typing import List, Iterator, Callable, Tuple

Pos = Tuple[int, int]
State = List[List[int]]
RedTeam, BlueTeam, NoneTeam = -1, 1, 0


class BFS:
    """广度优先搜索算法, 用于裁判判断棋子是否联通两个边界"""

    def __init__(self, state: State):
        self.state = state
        self.size = len(state)

    def get_neighbors(self, pos: Pos, team: int) -> Iterator[Pos]:
        """
        获取某个棋子的邻接棋子, 邻接棋子指: 当前位置周围 6 个方向中, 与当前棋子同属一方的棋子
        :param pos: 棋子位置
        :param team: 棋子所属的队伍
        :return: 该棋子邻接棋子的迭代器
        """
        directions = [(1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]  # 棋子的六个移动方向
        for dx, dy in directions:
            row, col = pos[0] + dx, pos[1] + dy
            if not (0 <= row < self.size and 0 <= col < self.size):  # 如果坐标不在棋盘范围内, 无效
                continue
            if team == self.state[row][col]:  # 如果属于同一方, 是邻接棋子
                yield row, col

    def find_path(self, start: Pos, team: int, stop_condition: Callable[[Pos], bool]) -> List[Pos]:
        """
        寻找指定起点到 "满足条件的点" 的路径, 如果没有, 返回 []
        :param team: 获取红队还是蓝队的路径
        :param start: 给定的起点位置
        :param stop_condition: 搜索结束条件, 用于指定终点位置
        :return: 起点到终点的路径
        """
        queue = Queue()
        visited = {}  # 记录已访问的结点, key 为结点坐标x,y, value 为其上一级结点坐标x,y
        queue.put(start)  # 起点位置入队 x,y
        visited[start] = (-1, -1)  # 起点已经访问, 无上级结点
        while not queue.empty():  # 如果队列未空
            node = queue.get()  # 队头结点出队
            if stop_condition(node):  # 如果 node 已经是终点
                path = []  # 记录起点到终点的路径
                pre = node  # 从终点反推回起点
                while pre != (-1, -1):
                    path.append(pre)
                    pre = visited[pre]  # pre 回到上一级
                path.reverse()  # 反转一次, 前面得到的是终点逆推到起点的路径
                return path
            # 把 node 相邻的, 且没有访问过的结点入队
            for nb in self.get_neighbors(node, team):
                if nb not in visited:
                    queue.put(nb)
                    visited[nb] = node  # 记录相邻结点的上一级结点
        return []

    def find_red_path(self) -> List[Pos]:
        """检查红方是否已经联通上下两边, 如果是, 返回路径, 如果没有, 返回 []"""

        # 遍历棋盘第一行(红方上界), 去找是否存在连接了最后一行(红方下界)的路径
        for col in range(self.size):
            if self.state[0][col] != RedTeam:
                continue  # 该位置没有红方棋子
            start_pos = 0, col
            last_row = self.size - 1  # 下界的行号
            path = self.find_path(start_pos, RedTeam, lambda pos: pos[0] == last_row)
            if path:
                return path
        return []

    def find_blue_path(self) -> List[Pos]:
        """检查蓝方是否已经联通左右两边, 如果是, 返回路径, 如果没有, 返回 []"""
        # 遍历棋盘第一列(蓝方左边界), 去找是否存在连接了最后一列(蓝方右边界)的路径
        for row in range(self.size):
            if self.state[row][0] != BlueTeam:
                continue  # 该位置没有蓝方棋子
            start_pos = row, 0
            last_col = self.size - 1  # 右边界的列号
            path = self.find_path(start_pos, BlueTeam, lambda pos: pos[1] == last_col)
            if path:
                return path
        return []

    def get_winner(self):
        """获取已经联通自己边界的的队伍"""
        if self.find_red_path():
            return RedTeam
        elif self.find_blue_path():
            return BlueTeam
        else:
            return NoneTeam


class Node:
    """
    蒙特卡洛搜索树的结点
    保存了一些必要信息, 为了减少不必要的拷贝, 结点内没有保存每一步的棋盘状态
    """

    def __init__(self, move: Pos = None, team: int = NoneTeam, parent=None):
        self.move = move  # 落子位置
        self.team = team  # 棋子所属队伍
        self.parent = parent  # 父节点
        self.visits = 0  # 该结点被访问的次数
        self.reward = 0  # 该结点处的获胜次数
        self.children = []  # 子节点

    @property
    def value(self):
        if self.visits == 0:
            return float('inf')
        return self.reward / self.visits + 0.5 * sqrt(
            2 * log(self.parent.visits) / self.visits)  # exploitation + exploration


class MCTS:
    """
    蒙特卡洛搜索树
    """

    def __init__(self, init_state, team: int):
        self.root_state = deepcopy(init_state)
        self.root = Node((-1, -1), team, None)
        self.turn = team  # 本轮下棋方

        # 一些统计信息
        self.run_time = 0
        self.simulate_count = 0

    @staticmethod
    def get_winner(state: State) -> int:
        """根据棋盘状态判断获胜者"""
        return BFS(state).get_winner()

    def search(self, time_limit: int = 1) -> None:
        """在限定的时间内找到下一步位置"""
        start_time = process_time()
        simulate_count = 0

        while process_time() - start_time < time_limit:
            node, state = self.select()
            winner = self.simulate(state)
            self.back_propagate(node, winner)
            simulate_count += 1

        # 记录统计信息
        self.run_time = process_time() - start_time
        self.simulate_count = simulate_count

    @staticmethod
    def modify_state(state: State, move: Pos, team: int):
        """用于修改棋盘的状态"""
        row, col = move
        state[row][col] = team

    @staticmethod
    def get_moves(state: State) -> List[Pos]:
        """获取可以下棋的位置"""
        size = len(state)
        moves = []
        for row in range(size):
            for col in range(size):
                moves.append((row, col))
        return moves

    def change_turn(self):
        """交换下棋方"""
        if self.turn == RedTeam:
            self.turn = BlueTeam
        elif self.turn == BlueTeam:
            self.turn = RedTeam

    def select(self) -> Tuple[Node, State]:
        """选择一个结点, 用于下一步模拟操作"""
        node = self.root
        # 每次选择只复制一次棋盘状态, 每经过一个子节点, 修改一次棋盘状态副本
        state_copy = deepcopy(self.root_state)

        while node.children:  # 如果没达到叶子节点, 一直深入下去
            max_value = max(node.children, key=lambda ch: ch.value).value   # 子节点中 value 最大值
            max_nodes = [n for n in node.children if n.value == max_value]  # value 最大的子节点
            node = choice(max_nodes)  # 随便选一个
            MCTS.modify_state(state_copy, node.move, node.team)  # 修改棋盘状态

            # 如果子节点还没有被探索, 直接选择它
            if node.visits == 0:
                return node, state_copy

        # 如果达到叶子结点, 就进行扩展, 随机返回一个子节点
        if self.expand(node, state_copy):
            node = choice(node.children)
            MCTS.modify_state(state_copy, node.move, node.team)  # 修改棋盘状态

        return node, state_copy

    def expand(self, parent: Node, state: State):
        # 如果游戏在该节点处已经结束, 无需扩展
        if self.get_winner(state) != NoneTeam:
            return False

        for move in self.get_moves(state):
            parent.children.append(Node(move, self.turn, parent))
        self.change_turn()
        return True

    def simulate(self, state: State) -> int:
        """模拟一局对战"""
        start = process_time()
        moves = self.get_moves(state)

        while self.get_winner(state) == NoneTeam:  # 无人获胜
            move = choice(moves)
            self.modify_state(state, move, self.turn)
            self.change_turn()
            moves.remove(move)
        # print(f"This simulation use: {process_time() - start:.8f}")
        return self.get_winner(state)

    def back_propagate(self, node: Node, winner: int):
        """反向传播, 更新父节点状态"""
        while node is not None:
            reward = 0 if winner == node.team else 1  # 获胜方产生的结点 +1 分
            node.visits += 1
            node.reward += reward
            node = node.parent

    def best_move(self) -> Pos:
        """获取最佳下棋位置"""
        max_value = max(self.root.children, key=lambda n: n.visits).visits
        max_nodes = [n for n in self.root.children if n.visits == max_value]
        return choice(max_nodes).move

    @property
    def tree_node_num(self) -> int:
        """统计树的结点数量"""
        queue = Queue()
        count = 0
        queue.put(self.root)
        while not queue.empty():
            node = queue.get()
            count += 1
            for child in node.children:
                queue.put(child)
        return count

    @property
    def statistics(self) -> tuple:
        """本次搜索的开销信息"""
        return self.simulate_count, self.tree_node_num, self.run_time
