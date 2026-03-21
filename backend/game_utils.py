# game_utils.py
# 游戏公用工具函数和常量

# 棋子类型
EMPTY = 0   # 空位
PLAYER = 1  # 玩家（黑棋）
AI = 2      # AI（白棋）

# 四个检查方向：竖直、水平、右下、右上
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

# 连子评分权重
SCORE_WEIGHTS = {
    1: 1,       # 单棋
    2: 100,     # 二连
    3: 1000,    # 三连
    4: 10000,   # 四连
    5: 100000   # 五连（获胜）
}


def count_consecutive(board, row, col, player, dx, dy):
    """
    统计指定方向连续同色棋子数
    
    Args:
        board: 棋盘状态
        row, col: 起始位置
        player: 棋子颜色
        dx, dy: 方向向量
        
    Returns:
        int: 连续棋子数量
    """
    count = 0
    r, c = row, col
    size = len(board)
    
    while 0 <= r < size and 0 <= c < size and board[r][c] == player:
        count += 1
        r += dx
        c += dy
    
    return count


def evaluate_position(board, row, col, player):
    """
    评估指定位置的落子价值
    
    基于四个方向连续同色棋子的长度计算得分
    
    Args:
        board: 棋盘状态
        row, col: 评估位置
        player: 假设落子的玩家
        
    Returns:
        int: 该位置评估得分
    """
    score = 0
    
    # 试探落子
    board[row][col] = player
    
    for dx, dy in DIRECTIONS:
        # 统计正反两个方向的连续棋子
        forward = count_consecutive(board, row + dx, col + dy, player, dx, dy)
        backward = count_consecutive(board, row - dx, col - dy, player, -dx, -dy)
        total = 1 + forward + backward
        
        # 根据连子长度计分
        score += SCORE_WEIGHTS.get(min(total, 5), 0)
    
    # 恢复棋盘
    board[row][col] = EMPTY
    
    return score


def get_empty_positions(board):
    """获取所有空位坐标"""
    size = len(board)
    return [(i, j) for i in range(size) for j in range(size) if board[i][j] == EMPTY]