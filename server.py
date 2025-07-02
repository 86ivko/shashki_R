from flask import Flask, request, jsonify
from flask_cors import CORS
import copy

app = Flask(__name__)
CORS(app)

# 0 - пусто, 1 - белая, 2 - черная, 3 - белая дамка, 4 - черная дамка
BOARD_SIZE = 8

def initial_board():
    b = []
    for y in range(BOARD_SIZE):
        b.append([])
        for x in range(BOARD_SIZE):
            if y < 3 and (x + y) % 2 == 1:
                b[y].append(2)
            elif y > 4 and (x + y) % 2 == 1:
                b[y].append(1)
            else:
                b[y].append(0)
    return b

# Для MVP: одна партия на сервере
GAME = {
    'board': initial_board(),
    'turn': 'white',
    'winner': None
}

def is_valid_move(board, from_, to, color):
    # Проверка: ход на одну клетку по диагонали вперёд, только на пустое поле
    if board[to['y']][to['x']] != 0:
        return False
    dx = to['x'] - from_['x']
    dy = to['y'] - from_['y']
    if abs(dx) == 1 and ((color == 'white' and dy == -1) or (color == 'black' and dy == 1)):
        return True
    # Битьё
    if abs(dx) == 2 and ((color == 'white' and dy == -2) or (color == 'black' and dy == 2)):
        mid_x = (from_['x'] + to['x']) // 2
        mid_y = (from_['y'] + to['y']) // 2
        mid_piece = board[mid_y][mid_x]
        if color == 'white' and mid_piece in [2, 4]:
            return True
        if color == 'black' and mid_piece in [1, 3]:
            return True
    return False

def make_move(board, from_, to):
    piece = board[from_['y']][from_['x']]
    board[to['y']][to['x']] = piece
    board[from_['y']][from_['x']] = 0
    # Битьё
    if abs(to['x'] - from_['x']) == 2:
        mid_x = (from_['x'] + to['x']) // 2
        mid_y = (from_['y'] + to['y']) // 2
        board[mid_y][mid_x] = 0
    # Дамка
    if piece == 1 and to['y'] == 0:
        board[to['y']][to['x']] = 3
    if piece == 2 and to['y'] == 7:
        board[to['y']][to['x']] = 4

def check_winner(board):
    white, black = 0, 0
    for row in board:
        for p in row:
            if p in [1, 3]:
                white += 1
            if p in [2, 4]:
                black += 1
    if white == 0:
        return 'black'
    if black == 0:
        return 'white'
    return None

@app.route('/state', methods=['GET'])
def get_state():
    return jsonify(GAME)

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    from_ = data['from']
    to = data['to']
    color = GAME['turn']
    board = GAME['board']
    if GAME['winner']:
        return jsonify({'error': 'Game over', 'winner': GAME['winner']}), 400
    if not is_valid_move(board, from_, to, color):
        return jsonify({'error': 'Invalid move'}), 400
    make_move(board, from_, to)
    GAME['turn'] = 'black' if GAME['turn'] == 'white' else 'white'
    GAME['winner'] = check_winner(board)
    return jsonify(GAME)

@app.route('/reset', methods=['POST'])
def reset():
    GAME['board'] = initial_board()
    GAME['turn'] = 'white'
    GAME['winner'] = None
    return jsonify(GAME)

if __name__ == '__main__':
    app.run(debug=True) 