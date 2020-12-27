# Hex Game

## Introduce

海克斯棋, 这是大二上计算机求解课的作业

语言为 Python3, 机器下棋使用蒙特卡洛搜索树实现

## Install

先安装依赖
```
pip install pygame
```

然后
```
python3 PyHex.py
```

## Game UI

![](https://img2020.cnblogs.com/blog/1824307/202012/1824307-20201227134709669-1337814921.png)

![](https://img2020.cnblogs.com/blog/1824307/202012/1824307-20201227134757425-1489189459.png)

## Problems

尽管在蒙特卡洛模拟的时候, 使用加权带路径压缩的并查集来判断获胜方, 然而性能还是很捉急  

在我的笔记本上, 11 阶棋盘在 1s 内模拟次数和展开节点数如下

```
[AI] Team.BLUE set piece at (0, 6) | simulate_times=881, node_count=14401, run_time=1.0
[AI] Team.BLUE set piece at (9, 0) | simulate_times=872, node_count=13925, run_time=1.0
[AI] Team.BLUE set piece at (0, 0) | simulate_times=886, node_count=13457, run_time=1.0
[AI] Team.BLUE set piece at (1, 7) | simulate_times=901, node_count=12997, run_time=1.0
[AI] Team.BLUE set piece at (1, 2) | simulate_times=893, node_count=12545, run_time=1.0
[AI] Team.BLUE set piece at (7, 10) | simulate_times=921, node_count=12101, run_time=1.0
[AI] Team.BLUE set piece at (1, 4) | simulate_times=938, node_count=11665, run_time=1.0
[AI] Team.BLUE set piece at (9, 4) | simulate_times=965, node_count=11237, run_time=1.0
[AI] Team.BLUE set piece at (0, 10) | simulate_times=1079, node_count=10817, run_time=1.0
[AI] Team.BLUE set piece at (3, 3) | simulate_times=1208, node_count=10405, run_time=1.0
```

为了提高模拟次数和展开结点数量, 可以在 `gameui/Config.py` 中提高 AI 每次运行的时间上限, 或者降低棋盘大小

```
board_size = 8  # 棋盘大小 NxN
game_mode = 2  # 1 双人模式, 2 人机模式, 3 机器对抗
first_player = 0  # 先手, 0 红方, 1蓝方
ai_level = 1  # 蒙特卡洛搜索时间上限/秒
```

时间上限设为 1s 时在 8 阶棋盘中效果还不错, 阶数高了得增加算法运行时间, 否则机器就如同智障

## TODO

- [ ] 用 C++ 重写蒙特卡洛搜索树
- [ ] 尝试蒙特卡洛搜索树的并行计算
- [ ] 优化一下这丑陋的界面