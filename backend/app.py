# app.py
# Flask 后端服务 - 处理游戏逻辑与 AI 对战请求

from flask import Flask, request, jsonify, send_from_directory, abort #1
from flask_cors import CORS
import sys  #1
import os  #1
import pygame


# ===================== 适配打包的路径函数=====================
def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容打包后和开发模式）"""
    if hasattr(sys, '_MEIPASS'):
        # 打包后运行：_MEIPASS是PyInstaller创建的临时目录
        base_path = sys._MEIPASS
    else:
        # 开发模式：用项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ============================================================================

# 添加项目根目录到Python路径（原有代码，已适配新路径函数）
sys.path.insert(0, get_resource_path(''))

# 导入模块（路径已适配）
from backend.game import Board
from backend.ai_1 import AI as AI_simple_normal
from backend.ai_2 import AI as AI_hard

# ===================== 项目根目录改为动态路径 =====================
# 原有：PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = get_resource_path('')
# =====================================================================

# ===================== Flask初始化路径 =====================
# 原有：app = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'))
app = Flask(__name__,
            static_folder=get_resource_path('static'),
            template_folder=get_resource_path('frontend'))  # 模板目录适配
# =====================================================================

CORS(app, resources={r"/api/*": {"origins": "*"}})  # 允许跨域请求

# 全局游戏状态
board = Board()
ai = None  # AI 实例动态创建

# 初始化 pygame 混音器
pygame.mixer.init()

# ===================== 音效路径适配 =====================
# 原有：SOUND_PATH = os.path.join(PROJECT_ROOT, 'static', 'sounds', 'luozi.mp3')
SOUND_PATH = get_resource_path(os.path.join('static', 'sounds', 'luozi.mp3'))
# =====================================================================

# 加载音效
try:
    fall_sound = pygame.mixer.Sound(SOUND_PATH)
except Exception as e:
    print(f"加载音效失败：{e}")
    fall_sound = None


@app.route('/api/restart', methods=['POST'])
def restart():
    """
    重新开始游戏

    Args (JSON):
        first_hand: 1=玩家先手, 2=AI先手

    Returns:
        游戏状态（棋盘、当前玩家、颜色分配等）
    """
    data = request.get_json(silent=True) or {}
    first_hand = data.get('first_hand', 1)

    board.init_board()

    # 设置颜色分配
    if first_hand == 1:
        board.player_color = 1  # 玩家执黑
        board.ai_color = 2  # AI执白
        board.current_player = board.player_color
    else:
        board.player_color = 2  # 玩家执白
        board.ai_color = 1  # AI执黑
        board.current_player = board.ai_color

    return jsonify({
        'board': board.board,
        'current_player': board.current_player,
        'player_color': board.player_color,
        'ai_color': board.ai_color,
        'game_over': board.game_over,
        'winner': board.winner
    })


@app.route('/api/move', methods=['POST'])
def move():
    """
    处理落子请求

    Args (JSON):
        row: 落子行号（AI先手时可不传）
        col: 落子列号（AI先手时可不传）
        difficulty: 难度 ('easy'/'normal'/'hard')

    Returns:
        最新游戏状态
    """
    global ai
    data = request.get_json(silent=True) or {}
    row = data.get('row')
    col = data.get('col')
    difficulty = data.get('difficulty', 'normal')

    # 根据难度创建AI实例
    if difficulty == 'hard':
        if not isinstance(ai, AI_hard):
            ai = AI_hard(board)
    else:
        if not isinstance(ai, AI_simple_normal):
            ai = AI_simple_normal(board)

    ai.set_difficulty(difficulty)

    # AI 回合
    if board.current_player == board.ai_color:
        try:
            ai_move = ai.get_move()
            if ai_move:
                board.place_piece(ai_move[0], ai_move[1], board.ai_color)
        except Exception as e:
            print(f"AI决策错误: {e}")
            # 如果AI决策失败，随机选择一个空位
            empty_positions = board.get_empty_positions()
            if empty_positions:
                import random
                ai_move = random.choice(empty_positions)
                board.place_piece(ai_move[0], ai_move[1], board.ai_color)
    else:
        # 玩家回合
        if not board.place_piece(row, col, board.player_color):
            return jsonify({'error': '无效落子'}), 400

        # 检查玩家获胜
        if board.game_over:
            return jsonify({
                'board': board.board,
                'current_player': board.current_player,
                'player_color': board.player_color,
                'ai_color': board.ai_color,
                'game_over': board.game_over,
                'winner': board.winner
            })

        # AI 回合
        if board.current_player == board.ai_color and not board.game_over:
            try:
                ai_move = ai.get_move()
                if ai_move:
                    board.place_piece(ai_move[0], ai_move[1], board.ai_color)
            except Exception as e:
                print(f"AI决策错误: {e}")
                # 如果AI决策失败，随机选择一个空位
                empty_positions = board.get_empty_positions()
                if empty_positions:
                    import random
                    ai_move = random.choice(empty_positions)
                    board.place_piece(ai_move[0], ai_move[1], board.ai_color)

    return jsonify({
        'board': board.board,
        'current_player': board.current_player,
        'player_color': board.player_color,
        'ai_color': board.ai_color,
        'game_over': board.game_over,
        'winner': board.winner
    })


@app.route('/api/undo', methods=['POST'])
def undo():
    """
    悔棋操作（撤销玩家和AI各一步）

    Returns:
        悔棋后的游戏状态
    """
    if board.game_over:
        return jsonify({'error': '游戏已结束，不能悔棋'}), 400

    if len(board.move_history) < 2:
        return jsonify({'error': '没有足够的步数可以悔棋'}), 400

    # 撤销两步
    for _ in range(2):
        r, c, _ = board.move_history.pop()
        board.board[r][c] = 0

    board.current_player = board.player_color
    board.game_over = False
    board.winner = None

    return jsonify({
        'board': board.board,
        'current_player': board.current_player,
        'player_color': board.player_color,
        'ai_color': board.ai_color,
        'game_over': board.game_over,
        'winner': board.winner
    })


@app.route('/api/resign', methods=['POST'])
def resign():
    """
    玩家认输

    Returns:
        游戏结束状态（AI 获胜）
    """
    board.game_over = True
    board.winner = board.ai_color
    return jsonify({
        'board': board.board,
        'current_player': board.current_player,
        'game_over': board.game_over,
        'winner': board.winner
    })


# 前端页面路由
@app.route('/')
def index():
    """提供主页面"""
    # ===================== 前端路径适配 =====================
    # 原有：frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    frontend_dir = get_resource_path('frontend')
    # ==============================================================
    return send_from_directory(frontend_dir, 'index.html')


@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """提供前端静态文件"""
    # ===================== 前端路径适配 =====================
    # 原有：frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
    frontend_dir = get_resource_path('frontend')
    # ==============================================================
    return send_from_directory(frontend_dir, filename)


@app.route('/quweiAuthor/<path:filename>')
def serve_quwei_author(filename):
    """提供曲威作者页面文件"""
    # ===================== 前端路径适配 =====================
    # 原有：quwei_dir = os.path.join(PROJECT_ROOT, 'frontend', 'quweiAuthor')
    quwei_dir = get_resource_path(os.path.join('frontend', 'quweiAuthor'))
    # ==============================================================
    return send_from_directory(quwei_dir, filename)


@app.route('/quweiAuthor/author/<path:filename>')
def serve_quwei_author_html(filename):
    """提供曲威作者的 HTML 文件"""
    # ===================== 前端路径适配 =====================
    # 原有：author_dir = os.path.join(PROJECT_ROOT, 'frontend', 'quweiAuthor', 'author')
    author_dir = get_resource_path(os.path.join('frontend', 'quweiAuthor', 'author'))
    # ==============================================================
    return send_from_directory(author_dir, filename)


@app.route('/downloads/<path:filename>')
def serve_downloads(filename):
    """提供下载文件"""
    downloads_dir = get_resource_path('downloads')
    return send_from_directory(downloads_dir, filename, as_attachment=True)


# 通用前端 HTML 文件路由（支持直接在根路径访问）- 必须放在最后
@app.route('/<path:filename>')
def serve_html_files(filename):
    """提供前端 HTML 文件（如 aiBattle.html、FriendBattle.html 等）"""
    # 只允许访问 html 文件
    if filename.endswith('.html'):
        # ===================== 前端路径适配 =====================
        # 原有：frontend_dir = os.path.join(PROJECT_ROOT, 'frontend')
        frontend_dir = get_resource_path('frontend')
        # ==============================================================
        return send_from_directory(frontend_dir, filename)
    # 如果不是 html 文件，返回 404
    abort(404)

