# game.py
# 五子棋游戏核心规则模块 - 管理棋盘状态与胜负判定

class Board:
    """棋盘类：管理游戏状态，包括棋盘布局、当前玩家、胜负判定等"""
    
    def __init__(self, size=15):
        """初始化15x15标准棋盘"""
        self.size = 15
        self.board = [[0] * size for _ in range(size)]  # 0=空, 1=黑棋, 2=白棋
        self.current_player = 1  # 黑棋先手
        self.game_over = False
        self.winner = None
        self.move_history = []  # 用于悔棋功能

    def init_board(self):
        """重置棋盘到初始状态"""
        self.board = [[0] * self.size for _ in range(self.size)]
        self.current_player = 1
        self.player_color = 1  # 玩家执黑
        self.ai_color = 2      # AI执白
        self.game_over = False
        self.winner = None
        self.move_history = []

    def place_piece(self, row, col, player):
        """
        执行落子操作
        
        Args:
            row: 行号(0-14)
            col: 列号(0-14)
            player: 玩家编号(1或2)
            
        Returns:
            bool: 落子是否成功
        """
        # 边界检查
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.board[row][col] != 0:
            return False
        if player != self.current_player:
            return False
        if self.game_over:
            return False

        # 执行落子
        self.board[row][col] = player
        self.move_history.append((row, col, player))
        
        # 检查胜负
        if self._check_winner(row, col, player):
            self.game_over = True
            self.winner = player
        else:
            # 切换玩家: 3-1=2, 3-2=1
            self.current_player = 3 - player
            
        return True

    def _check_winner(self, row, col, player):
        """
        检查指定位置是否形成五子连珠
        
        检查四个方向：横向、纵向、左斜、右斜
        任一连线达到5子即获胜
        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            count = 1
            
            # 正向搜索
            r, c = row + dx, col + dy
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r += dx
                c += dy
                
            # 反向搜索
            r, c = row - dx, col - dy
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                count += 1
                r -= dx
                c -= dy
                
            if count >= 5:
                return True
                
        return False

    def is_full(self):
        """检查棋盘是否已满（平局判定）"""
        return not any(0 in row for row in self.board)

    def get_empty_positions(self):
        """获取所有空位坐标，供AI决策使用"""
        return [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]