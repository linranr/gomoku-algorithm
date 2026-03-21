# ai_2.py
# AI决策模块 - 困难难度实现
# 基于Minimax算法配合α-β剪枝优化，搜索深度6层

import random
import time
from backend.game import Board

BOARD_SIZE = 15
INF = 1000000000

# 方向向量：右、下、右下、左下
DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

# 棋型评分表
PATTERNS = {
    5: 100000,    # 五连
    4: 10000,     # 活四
    3: 1000,      # 活三
    2: 100,       # 活二
    1: 10         # 单棋
}

# Zobrist哈希表
zobrist_black = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
zobrist_white = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
zobrist_initialized = False

def init_zobrist():
    """初始化Zobrist哈希表"""
    global zobrist_initialized
    if not zobrist_initialized:
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                zobrist_black[i][j] = random.randint(0, 2**64 - 1)
                zobrist_white[i][j] = random.randint(0, 2**64 - 1)
        zobrist_initialized = True

def get_zobrist_key(board):
    """计算棋盘的Zobrist哈希值"""
    key = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 1:
                key ^= zobrist_black[i][j]
            elif board[i][j] == 2:
                key ^= zobrist_white[i][j]
    return key

def evaluate_position(board, row, col, player):
    """评估指定位置的得分
    
    Args:
        board: 棋盘状态
        row, col: 评估位置
        player: 玩家编号
        
    Returns:
        int: 该位置评估得分
    """
    # 检查位置是否为空
    if board[row][col] != 0:
        return 0
    
    board[row][col] = player
    score = 0
    
    for dx, dy in DIRECTIONS:
        count = 1
        # 正向统计
        r, c = row + dx, col + dy
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dx
            c += dy
        # 反向统计
        r, c = row - dx, col - dy
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r -= dx
            c -= dy
        
        # 根据连子数计分
        if count >= 5:
            score += PATTERNS[5]
        elif count == 4:
            score += PATTERNS[4]
        elif count == 3:
            score += PATTERNS[3]
        elif count == 2:
            score += PATTERNS[2]
        elif count == 1:
            score += PATTERNS[1]
    
    board[row][col] = 0
    return score

def evaluate_board(board, player):
    """评估整个棋盘对指定玩家的得分
    
    Args:
        board: 棋盘状态
        player: 玩家编号
        
    Returns:
        int: 棋盘评估得分
    """
    score = 0
    opponent = 3 - player
    
    # 评估己方棋子的贡献
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                score += evaluate_position(board, i, j, player)
    
    # 评估对方棋子的威胁（降低己方得分）
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == opponent:
                # 检查对方棋子周围是否有空位可以形成威胁
                threat_score = 0
                for dx, dy in DIRECTIONS:
                    count = 1
                    # 正向统计
                    r, c = i + dx, j + dy
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == opponent:
                        count += 1
                        r += dx
                        c += dy
                    # 反向统计
                    r, c = i - dx, j - dy
                    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == opponent:
                        count += 1
                        r -= dx
                        c -= dy
                    # 根据连子数计分
                    if count >= 5:
                        threat_score += PATTERNS[5]
                    elif count == 4:
                        threat_score += PATTERNS[4]
                    elif count == 3:
                        threat_score += PATTERNS[3]
                    elif count == 2:
                        threat_score += PATTERNS[2]
                    elif count == 1:
                        threat_score += PATTERNS[1]
                score -= threat_score * 1.2
    
    return score

def get_candidate_positions(board, max_candidates=20):
    """获取候选落子位置
    
    只考虑已有棋子周围的空位，减少搜索空间
    对候选位置进行评分，优先考虑有威胁的位置
    
    Args:
        board: 棋盘状态
        max_candidates: 最大候选位置数量
        
    Returns:
        list: 候选位置列表 [(row, col), ...]
    """
    candidates = []
    seen_positions = set()  # 避免重复添加同一位置
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] != 0:
                # 检查周围8个位置
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                            if board[ni][nj] == 0:
                                pos_key = (ni, nj)
                                if pos_key not in seen_positions:
                                    seen_positions.add(pos_key)
                                    # 评估该位置的得分
                                    score = evaluate_position(board, ni, nj, board[i][j])
                                    candidates.append((score, ni, nj))
    
    # 如果棋盘为空，返回中心点
    if not candidates:
        return [(BOARD_SIZE // 2, BOARD_SIZE // 2)]
    
    # 按得分降序排序
    candidates.sort(key=lambda x: -x[0])
    
    # 限制候选位置数量
    candidates = candidates[:max_candidates]
    
    # 返回位置列表
    return [(row, col) for _, row, col in candidates]

def minimax(board, depth, alpha, beta, maximizing_player, ai_player, human_player, transposition_table):
    """Minimax算法配合α-β剪枝
    
    Args:
        board: 棋盘状态
        depth: 当前搜索深度
        alpha: 当前最大下界
        beta: 当前最小上界
        maximizing_player: 是否为最大化层
        ai_player: AI执子颜色
        human_player: 玩家执子颜色
        transposition_table: 置换表（用于缓存）
        
    Returns:
        tuple: (score, row, col)
    """
    # 到达搜索深度或游戏结束
    if depth == 0:
        score = evaluate_board(board, ai_player)
        return (score, -1, -1)
    
    # 检查是否有人获胜
    if check_winner(board, ai_player):
        return (INF, -1, -1)
    if check_winner(board, human_player):
        return (-INF, -1, -1)
    
    # 获取候选位置
    candidates = get_candidate_positions(board)
    
    if not candidates:
        score = evaluate_board(board, ai_player)
        return (score, -1, -1)
    
    # 对候选位置进行排序优化
    if maximizing_player:
        current_player = ai_player
    else:
        current_player = human_player
    
    # 智能排序：优先考虑有威胁的位置
    center = BOARD_SIZE // 2
    def position_priority(pos):
        row, col = pos
        # 计算该位置对当前玩家的得分
        attack_score = evaluate_position(board, row, col, current_player)
        # 计算该位置对对手的威胁（阻拦得分）
        opponent = 3 - current_player
        defense_score = evaluate_position(board, row, col, opponent)
        # 综合得分：进攻得分 + 防守权重 * 阻拦得分
        total_score = attack_score + (defense_score * 1.5 if maximizing_player else defense_score * 2.0)
        # 距离中心的距离（越近越好）
        distance = abs(row - center) + abs(col - center)
        return (-total_score, distance)  # 降序排序
    
    candidates.sort(key=position_priority)
    
    if maximizing_player:
        max_eval = -INF
        best_row, best_col = -1, -1
        
        for row, col in candidates:
            board[row][col] = current_player
            
            # 计算Zobrist键
            key = get_zobrist_key(board)
            
            # 检查置换表
            if key in transposition_table and transposition_table[key][0] >= depth:
                eval_score = transposition_table[key][1]
            else:
                eval_score, _, _ = minimax(board, depth - 1, alpha, beta, False, 
                                          ai_player, human_player, transposition_table)
                transposition_table[key] = (depth, eval_score)
            
            board[row][col] = 0
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_row, best_col = row, col
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        return (max_eval, best_row, best_col)
    else:
        min_eval = INF
        best_row, best_col = -1, -1
        
        for row, col in candidates:
            board[row][col] = current_player
            
            # 计算Zobrist键
            key = get_zobrist_key(board)
            
            # 检查置换表
            if key in transposition_table and transposition_table[key][0] >= depth:
                eval_score = transposition_table[key][1]
            else:
                eval_score, _, _ = minimax(board, depth - 1, alpha, beta, True, 
                                          ai_player, human_player, transposition_table)
                transposition_table[key] = (depth, eval_score)
            
            board[row][col] = 0
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_row, best_col = row, col
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        
        return (min_eval, best_row, best_col)

def check_winner(board, player):
    """检查指定玩家是否获胜
    
    Args:
        board: 棋盘状态
        player: 玩家编号
        
    Returns:
        bool: 是否获胜
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                for dx, dy in DIRECTIONS:
                    count = 1
                    # 正向检查
                    ni, nj = i + dx, j + dy
                    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == player:
                        count += 1
                        ni += dx
                        nj += dy
                    # 反向检查
                    ni, nj = i - dx, j - dy
                    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == player:
                        count += 1
                        ni -= dx
                        nj -= dy
                    if count >= 5:
                        return True
    return False

def find_threat_positions(board, player):
    """查找玩家的威胁位置（需要阻拦的位置）
    
    Args:
        board: 棋盘状态
        player: 玩家编号
        
    Returns:
        list: 威胁位置列表 [(row, col, threat_level), ...]
    """
    threats = []
    visited = set()  # 避免重复添加同一位置
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                for dx, dy in DIRECTIONS:
                    # 检查该方向上的连子情况
                    count = 1
                    # 正向统计
                    ni, nj = i + dx, j + dy
                    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == player:
                        count += 1
                        ni += dx
                        nj += dy
                    # 记录正向端点（连子末端之后的第一个位置）
                    forward_end = (ni, nj)
                    
                    # 反向统计
                    ni, nj = i - dx, j - dy
                    while 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and board[ni][nj] == player:
                        count += 1
                        ni -= dx
                        nj -= dy
                    # 记录反向端点（连子起始端之前的第一个位置）
                    backward_end = (ni, nj)
                    
                    # 如果有威胁，检查两端空位
                    if count >= 3:
                        threat_level = 5 if count >= 4 else (3 if count == 3 else 1)
                        
                        # 检查正向端点
                        if (0 <= forward_end[0] < BOARD_SIZE and 
                            0 <= forward_end[1] < BOARD_SIZE and 
                            board[forward_end[0]][forward_end[1]] == 0):
                            key = (forward_end[0], forward_end[1], threat_level)
                            if key not in visited:
                                threats.append((forward_end[0], forward_end[1], threat_level))
                                visited.add(key)
                        
                        # 检查反向端点
                        if (0 <= backward_end[0] < BOARD_SIZE and 
                            0 <= backward_end[1] < BOARD_SIZE and 
                            board[backward_end[0]][backward_end[1]] == 0):
                            key = (backward_end[0], backward_end[1], threat_level)
                            if key not in visited:
                                threats.append((backward_end[0], backward_end[1], threat_level))
                                visited.add(key)
    
    # 按威胁等级降序排序
    threats.sort(key=lambda x: -x[2])
    return threats

class AI:
    """困难难度AI：基于Minimax+α-β剪枝，搜索深度4层"""
    
    def __init__(self, board):
        """初始化AI实例
        
        Args:
            board: 棋盘对象引用
        """
        self.board = board
        self.difficulty = "hard"
        self.max_depth = 4
        
        # 初始化Zobrist哈希
        init_zobrist()
    
    def set_difficulty(self, diff):
        """设置AI难度级别
        
        Args:
            diff: 难度级别 ("easy"/"normal"/"hard")
        """
        self.difficulty = diff
    
    def get_move(self):
        """获取AI落子决策
        
        Returns:
            tuple: (row, col)落子坐标，无有效位置返回None
        """
        if not hasattr(self.board, 'ai_color') or not hasattr(self.board, 'player_color'):
            return (BOARD_SIZE // 2, BOARD_SIZE // 2)
        
        # 复制棋盘状态
        board_copy = [row[:] for row in self.board.board]
        
        ai_player = self.board.ai_color
        human_player = self.board.player_color
        
        # 获取候选位置（只检查有意义的空位）
        candidates = get_candidate_positions(board_copy, max_candidates=30)
        
        # 第一步：检查AI是否有必胜位置
        for row, col in candidates:
            board_copy[row][col] = ai_player
            if check_winner(board_copy, ai_player):
                board_copy[row][col] = 0
                return (row, col)
            board_copy[row][col] = 0
        
        # 第二步：检查玩家是否有必胜位置（需要阻拦）
        player_threats = find_threat_positions(board_copy, human_player)
        if player_threats and player_threats[0][2] >= 5:
            # 玩家有致命威胁，必须阻拦
            return (player_threats[0][0], player_threats[0][1])
        
        # 第三步：检查玩家是否有四连子威胁
        for row, col, threat_level in player_threats:
            if threat_level >= 4:
                # 阻拦玩家的四连子
                return (row, col)
        
        # 置换表（用于缓存）
        transposition_table = {}
        
        # 执行Minimax搜索，深度4层
        start_time = time.time()
        score, row, col = minimax(board_copy, self.max_depth, -INF, INF, True, 
                                   ai_player, human_player, transposition_table)
        elapsed = (time.time() - start_time) * 1000
        
        if elapsed > 1000:
            print(f"警告：AI决策耗时 {elapsed:.2f}ms")
        
        # 如果没有找到最佳位置，返回中心点
        if row == -1 or col == -1:
            empty_positions = self.board.get_empty_positions()
            if empty_positions:
                return random.choice(empty_positions)
            return (BOARD_SIZE // 2, BOARD_SIZE // 2)
        
        return (row, col)
