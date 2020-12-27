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
    """广度优先搜索算法, 用于裁判判断棋子是否联通两个边界, 并获取联通的路径"""

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


class UnionFind:
    """带权路径压缩的并查集"""

    def __init__(self):
        self.parent = {}  # 存储结点之间的关系
        self.rank = {}  # 存储结点对应的树高

        # edge_one 和 edge_two 用做标记, 当棋子落在己方边界位置, 就与对应的 edge 连接
        # 最后判断 edge_one 和 edge_two 是否连接即可知道棋盘两个边界是否联通
        self.edge_one = (-1, -1)
        self.edge_two = (-2, -2)
        self.parent[self.edge_one] = self.edge_one
        self.parent[self.edge_two] = self.edge_two
        self.rank[self.edge_one] = 0
        self.rank[self.edge_two] = 0

    def find(self, x: Pos) -> Pos:
        """查找结点的根节点(代表元), 如果没找到就加入并查集, 查找过程中会进行路径压缩"""
        if x not in self.parent:  # 元素不存在
            self.parent[x] = x
            self.rank[x] = 0

        while x != self.parent[x]:  # 还没有达到根节点
            gx = self.parent[self.parent[x]]  # 祖父结点
            self.parent[x] = gx  # 隔代压缩, 减小树高
            x = gx
        return x

    def connected(self, x: Pos, y: Pos) -> bool:
        """判断两个结点是否联通"""
        return self.find(x) == self.find(y)  # 根节点则联通

    def union(self, x: Pos, y: Pos) -> bool:
        """连接两个元素"""
        rx = self.find(x)  # x 的根节点
        ry = self.find(y)

        if rx == ry:
            return False

        # 将对应树高小的结点挂到树高大的结点上, 降低合并后的树高
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:  # 一样高, 随便挂, 整体树高 +1
            self.parent[rx] = ry
            self.rank[ry] += 1
        return True

    def union_edge_one(self, p: Pos):
        """将结点 p 与标记位置 1 联通"""
        return self.union(self.edge_one, p)

    def union_edge_two(self, p: Pos):
        """将结点 p 与标记位置 2 联通"""
        return self.union(self.edge_two, p)

    def edge_connected(self) -> bool:
        """通过判断两个标记位置是否联通判断整个棋盘的两个边界是否联通"""
        return self.connected(self.edge_one, self.edge_two)


class Node:
    """
    蒙特卡洛搜索树的结点
    保存了一些必要信息, 为了减少不必要的拷贝, 结点内**没有**保存每一步的棋盘状态
    结点的更新操作交给 MCTS 类实现
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
        """根据 uct 算法得出该结点的 value"""
        if self.visits == 0:
            return float('inf')
        # exploitation + exploration
        return self.reward / self.visits + 0.5 * sqrt(2 * log(self.parent.visits) / self.visits)


class BoardState:
    """棋盘状态类
    保存了当前棋盘的状态, 下棋方, 棋盘状态对应的并查集(用于判断胜利者)
    提供了一些对棋盘状态修改的方法
    """

    def __init__(self, state: State, turn: int):
        self.state = deepcopy(state)  # 当前棋盘状态, 二维数组
        self.size = len(state)  # 棋盘大小
        self.turn = turn  # 当前下棋方
        self.red_uf = UnionFind()  # 红方的并查集
        self.blue_uf = UnionFind()  # 蓝方的并查集
        self.init_union_find()

    def init_union_find(self):
        """根据棋盘状态, 初始化对应的并查集"""
        for row in range(self.size):
            for col in range(self.size):
                turn = self.state[row][col]
                self.update_union_find((row, col), turn)

    def get_winner(self) -> int:
        """使用并查集判断获胜者"""
        if self.red_uf.edge_connected():
            return RedTeam
        elif self.blue_uf.edge_connected():
            return BlueTeam
        return NoneTeam

    def get_neighbors(self, pos: Pos, team: int) -> Iterator[Pos]:
        """
        获取棋子的邻居列表
        :param pos: 棋子坐标
        :param team: 棋子所属队伍
        :return: 邻居坐标列表
        """
        directions = [(1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0)]  # 棋子的六个移动方向
        for dx, dy in directions:
            row, col = pos[0] + dx, pos[1] + dy
            if not (0 <= row < self.size and 0 <= col < self.size):  # 如果坐标不在棋盘范围内, 无效
                continue
            if team == self.state[row][col]:  # 如果属于同一方, 是邻接棋子
                yield row, col

    def change_turn(self):
        """交换下棋方"""
        if self.turn == RedTeam:
            self.turn = BlueTeam
        elif self.turn == BlueTeam:
            self.turn = RedTeam

    def update_union_find(self, move: Pos, turn: int):
        """更新并查集状态, 尝试将给定坐标与并查集中的结点联通"""
        if turn == NoneTeam:
            return

        row, col = move
        if turn == RedTeam:
            if row == 0:  # 红队棋子下在第一行(红方上边界)
                self.red_uf.union_edge_one(move)
            if row == self.size - 1:  # 红队棋子下在最后一行(红方下边界)
                self.red_uf.union_edge_two(move)
            # 棋子下在非边界位置, 将它与邻居连接起来
            for nb in self.get_neighbors(move, turn):
                self.red_uf.union(move, nb)

        elif turn == BlueTeam:
            if col == 0:
                self.blue_uf.union_edge_one(move)
            if col == self.size - 1:
                self.blue_uf.union_edge_two(move)
            for nb in self.get_neighbors(move, turn):
                self.blue_uf.union(move, nb)

    def set_piece(self, move: Pos):
        """下一步棋, 修改棋盘的状态, 更新并查集"""
        row, col = move
        self.state[row][col] = self.turn
        self.update_union_find(move, self.turn)
        self.change_turn()

    def get_moves(self) -> List[Pos]:
        """获取可以下棋的位置"""
        moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.state[row][col] == NoneTeam:
                    moves.append((row, col))
        return moves

    def print(self):
        for row in range(self.size):
            for col in range(self.size):
                print(self.state[row][col], end='\t')
            print()


class MCTS:
    """
    蒙特卡洛搜索树
    """

    def __init__(self, init_state, turn: int):
        self.root_state = BoardState(init_state, turn)
        self.root = Node((-1, -1), turn, None)

        # 一些统计信息
        self.run_time = 0
        self.simulate_times = 0

    def search(self, time_limit: int = 1) -> None:
        """在限定的时间内对树进行展开和模拟"""
        start_time = process_time()
        simulate_times = 0

        while process_time() - start_time < time_limit:
            node, state = self.select()
            winner = self.simulate(state)
            self.back_propagate(node, winner)
            simulate_times += 1

        # 记录统计信息
        self.run_time = process_time() - start_time
        self.simulate_times = simulate_times

    def select(self) -> Tuple[Node, BoardState]:
        """选择一个结点, 用于下一步模拟操作"""
        node = self.root
        # 每次选择只复制一次棋盘状态, 每经过一个子节点, 修改一次棋盘状态副本
        state_copy = BoardState(self.root_state.state, self.root_state.turn)

        while node.children:  # 如果没达到叶子节点, 一直深入下去
            max_value = max(node.children, key=lambda ch: ch.value).value  # 子节点中 value 最大值
            max_nodes = [n for n in node.children if n.value == max_value]  # value 最大的子节点
            node = choice(max_nodes)  # 随便选一个
            state_copy.set_piece(node.move)

            # 如果子节点还没有被探索, 直接选择它
            if node.visits == 0:
                return node, state_copy

        # 如果达到叶子结点, 就进行扩展, 随机返回一个子节点
        if self.expand(node, state_copy):
            node = choice(node.children)
            state_copy.set_piece(node.move)

        return node, state_copy

    def expand(self, parent: Node, state: BoardState):
        # 如果游戏在该节点处已经结束, 无需扩展
        if state.get_winner() != NoneTeam:
            return False

        for move in state.get_moves():  # 棋盘中空白位置都可以是子节点
            parent.children.append(Node(move, state.turn, parent))

        return True

    def simulate(self, state: BoardState) -> int:
        """在给定的状态下, 模拟一局对战, 返回胜利者"""
        moves = state.get_moves()
        while True:
            winner = state.get_winner()
            if winner != NoneTeam:
                return winner
            try:
                move = choice(moves)
                state.set_piece(move)
                moves.remove(move)
            except Exception as e:
                print(e)
                state.print()
                print(state.get_moves())
                input("!" * 100)

    def back_propagate(self, node: Node, winner: int):
        """从给定结点反向传播, 更新其父节点信息"""
        while node is not None:
            reward = 1 if winner == node.team else 0
            node.visits += 1
            node.reward += reward
            node = node.parent

    def best_move(self) -> Pos:
        """获取最佳下棋位置"""
        max_value = 0
        best_choice = None
        for ch in self.root.children:
            if ch.reward > max_value:
                max_value = ch.reward
                best_choice = ch
        return best_choice.move

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
        return self.simulate_times, self.tree_node_num, self.run_time
