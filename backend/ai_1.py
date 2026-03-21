# ai_1.py
# AI决策模块 - 简单/普通难度实现
# 简单模式：带围堵功能的随机策略
# 普通模式：基于贪心算法的综合评估策略

import random
import time
from backend.game import Board

class AI:
    """简单/普通难度AI：提供随机围堵和贪心算法两种策略"""
    
    def __init__(self, board):
        """初始化AI实例
        
        Args:
            board: 棋盘对象引用
        """
        self.board = board
        self.difficulty = "normal"

    def set_difficulty(self, diff):
        """设置AI难度级别
        
        Args:
            diff: 难度级别 ("easy"/"normal"/"hard")
                  hard难度会降级为normal处理
        """
        self.difficulty = diff

    def get_move(self):
        """根据当前难度获取AI落子决策
        
        Returns:
            tuple: (row, col)落子坐标，无有效位置返回None
        """
        if self.difficulty == "easy":
            return self._random_move()
        else:
            return self._greedy_move()

    def _random_move(self):
        """简单模式：带围堵功能的随机落子
        
        策略：优先检测并围堵玩家4连子和3连子威胁，否则随机选择空位
        """
        start_time = time.time()
        
        # 优先围堵玩家4连子和3连子威胁
        blocking_move = self._detect_and_block()
        if blocking_move:
            elapsed = (time.time() - start_time) * 1000
            if elapsed > 300:
                print(f"警告：AI围堵决策耗时 {elapsed:.2f}ms")
            return blocking_move
        
        # 无威胁时随机落子
        empty = self.board.get_empty_positions()
        return random.choice(empty) if empty else None
    
    def _detect_and_block(self):
        """检测玩家连子威胁并返回围堵位置
        
        检测规则：
        - 优先检测四连子威胁（两端至少一端为空）
        - 其次检测三连子威胁（两端都为空）
        
        Returns:
            tuple: 围堵位置(row, col)，无威胁返回None
        """
        player = 1
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for row in range(self.board.size):
            for col in range(self.board.size):
                if self.board.board[row][col] == player:
                    for dx, dy in directions:
                        # 优先检测四连子
                        pos = self._check_four_in_direction(row, col, dx, dy, player)
                        if pos:
                            return pos
                        # 其次检测三连子
                        pos = self._check_three_in_direction(row, col, dx, dy, player)
                        if pos:
                            return pos
        
        return None
    
    def _check_four_in_direction(self, row, col, dx, dy, player):
        """检查指定方向是否有4连子
        
        Args:
            row, col: 起始位置
            dx, dy: 方向向量
            player: 玩家编号
            
        Returns:
            tuple: 可围堵位置，无4连子返回None
        """
        count = 1
        positions = [(row, col)]
        
        # 统计连续棋子
        r, c = row + dx, col + dy
        while 0 <= r < self.board.size and 0 <= c < self.board.size and self.board.board[r][c] == player:
            count += 1
            positions.append((r, c))
            r += dx
            c += dy
        
        # 正好4连子时计算围堵位置
        if count == 4:
            start_r, start_c = row - dx, col - dy
            end_r, end_c = positions[-1][0] + dx, positions[-1][1] + dy
            
            # 检查两端是否可围堵
            if 0 <= start_r < self.board.size and 0 <= start_c < self.board.size:
                if self.board.board[start_r][start_c] == 0:
                    return (start_r, start_c)
            
            if 0 <= end_r < self.board.size and 0 <= end_c < self.board.size:
                if self.board.board[end_r][end_c] == 0:
                    return (end_r, end_c)
        
        return None
    
    def _check_three_in_direction(self, row, col, dx, dy, player):
        """检查指定方向是否有三连子且两端为空
        
        Args:
            row, col: 起始位置
            dx, dy: 方向向量
            player: 玩家编号
            
        Returns:
            tuple: 可围堵位置，无三连子返回None
        """
        count = 1
        positions = [(row, col)]
        
        # 统计连续棋子
        r, c = row + dx, col + dy
        while 0 <= r < self.board.size and 0 <= c < self.board.size and self.board.board[r][c] == player:
            count += 1
            positions.append((r, c))
            r += dx
            c += dy
        
        # 正好3连子时计算围堵位置
        if count == 3:
            start_r, start_c = row - dx, col - dy
            end_r, end_c = positions[-1][0] + dx, positions[-1][1] + dy
            
            # 检查两端是否都为空
            start_empty = (0 <= start_r < self.board.size and 0 <= start_c < self.board.size and 
                          self.board.board[start_r][start_c] == 0)
            end_empty = (0 <= end_r < self.board.size and 0 <= end_c < self.board.size and 
                        self.board.board[end_r][end_c] == 0)
            
            if start_empty and end_empty:
                # 随机选择一端进行阻拦
                return random.choice([(start_r, start_c), (end_r, end_c)])
        
        return None

    def _greedy_move(self):
        """普通模式：贪心算法选择最优落子
        
        策略：
        1. 优先检测必胜位置（AI能连五）
        2. 其次检测必败位置（玩家能连五，需要阻拦）
        3. 综合评估进攻和防守得分，选择最优位置
        """
        empty = self.board.get_empty_positions()
        if not empty:
            return None
        
        # 第一步：检测AI必胜位置
        for row, col in empty:
            if self._check_five(row, col, 2):
                return (row, col)
        
        # 第二步：检测玩家必胜位置（需要阻拦）
        for row, col in empty:
            if self._check_five(row, col, 1):
                return (row, col)
        
        # 第三步：贪心评估选择最优位置
        best_score = -float('inf')
        best_move = None
        
        for row, col in empty:
            attack_score = self._evaluate_position(row, col, 2)
            defense_score = self._evaluate_position(row, col, 1)
            total = attack_score + defense_score * 1.2
            
            if total > best_score:
                best_score = total
                best_move = (row, col)
        
        return best_move
    
    def _check_five(self, row, col, player):
        """检查在指定位置落子是否能形成五连
        
        Args:
            row, col: 落子位置
            player: 玩家编号
            
        Returns:
            bool: 是否能形成五连
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        self.board.board[row][col] = player
        
        for dx, dy in directions:
            count = 1
            # 正向统计
            r, c = row + dx, col + dy
            while 0 <= r < self.board.size and 0 <= c < self.board.size and self.board.board[r][c] == player:
                count += 1
                r += dx
                c += dy
            # 反向统计
            r, c = row - dx, col - dy
            while 0 <= r < self.board.size and 0 <= c < self.board.size and self.board.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy
            
            if count >= 5:
                self.board.board[row][col] = 0
                return True
        
        self.board.board[row][col] = 0
        return False

    def _evaluate_position(self, row, col, player):
        """评估指定位置的得分
        
        Args:
            row, col: 评估位置
            player: 假设落子的玩家编号
            
        Returns:
            int: 该位置评估得分
        """
        self.board.board[row][col] = player
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            # 分析该方向的棋型
            pattern_score = self._analyze_direction(row, col, dx, dy, player)
            score += pattern_score
        
        self.board.board[row][col] = 0
        return score
    
    def _analyze_direction(self, row, col, dx, dy, player):
        """分析指定方向的棋型并评分
        
        Args:
            row, col: 落子位置
            dx, dy: 方向向量
            player: 玩家编号
            
        Returns:
            int: 该方向得分
        """
        opponent = 3 - player
        
        # 正向统计连续棋子和空位
        count = 1
        block = 0
        empty_count = 0
        
        # 正向
        r, c = row + dx, col + dy
        while 0 <= r < self.board.size and 0 <= c < self.board.size:
            if self.board.board[r][c] == player:
                count += 1
                r += dx
                c += dy
            elif self.board.board[r][c] == 0:
                empty_count += 1
                break
            else:
                block += 1
                break
        
        if not (0 <= r < self.board.size and 0 <= c < self.board.size):
            block += 1
        
        # 反向
        r, c = row - dx, col - dy
        while 0 <= r < self.board.size and 0 <= c < self.board.size:
            if self.board.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy
            elif self.board.board[r][c] == 0:
                empty_count += 1
                break
            else:
                block += 1
                break
        
        if not (0 <= r < self.board.size and 0 <= c < self.board.size):
            block += 1
        
        # 根据棋型评分
        if count >= 5:
            return 100000  # 五连
        elif count == 4:
            if block == 0:
                return 50000   # 活四
            elif block == 1:
                return 10000   # 冲四
        elif count == 3:
            if block == 0:
                return 5000    # 活三
            elif block == 1:
                return 500     # 眠三
        elif count == 2:
            if block == 0:
                return 200     # 活二
            elif block == 1:
                return 50      # 眠二
        elif count == 1:
            return 10
        
        return 0