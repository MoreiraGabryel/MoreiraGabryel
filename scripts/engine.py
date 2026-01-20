import os
import re
import sys

def check_winner(b):
    win_states = [
        [b[0][0], b[0][1], b[0][2]], [b[1][0], b[1][1], b[1][2]], [b[2][0], b[2][1], b[2][2]],
        [b[0][0], b[1][0], b[2][0]], [b[0][1], b[1][1], b[2][1]], [b[0][2], b[1][2], b[2][2]],
        [b[0][0], b[1][1], b[2][2]], [b[0][2], b[1][1], b[2][0]]
    ]
    if ['O', 'O', 'O'] in win_states: return 1
    if ['X', 'X', 'X'] in win_states: return -1
    return 0

def minimax(board, depth, is_maximizing):
    score = check_winner(board)
    if score == 1: return score
    if score == -1: return score
    if not any(' ' in row for row in board): return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'O'
                    score = minimax(board, depth + 1, False)
                    board[i][j] = ' '
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i][j] == ' ':
                    board[i][j] = 'X'
                    score = minimax(board, depth + 1, True)
                    board[i][j] = ' '
                    best_score = min(score, best_score)
        return best_score

def best_move(board):
    best_score = -float('inf')
    move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                score = minimax(board, 0, False)
                board[i][j] = ' '
                if score > best_score:
                    best_score = score
                    move = (i, j)
    return move

def main():
    issue_title = os.getenv("ISSUE_TITLE", "")
    if not issue_title.startswith("tttp:"):
        return

    try:
        coords = issue_title.split(":")[1].split(",")
        u_row, u_col = int(coords[0]), int(coords[1])
    except: return

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    rows = re.findall(r"\| (.*?) \| (.*?) \| (.*?) \|", content)
    board_data = []
    for r in rows[1:]: 
        parsed_row = []
        for cell in r:
            if "❌" in cell or "X" in cell: parsed_row.append("X")
            elif "⭕" in cell or "O" in cell: parsed_row.append("O")
            else: parsed_row.append(" ")
        board_data.append(parsed_row)

    if board_data[u_row][u_col] == " ":
        board_data[u_row][u_col] = "X"
        
        if any(' ' in r for r in board_data) and check_winner(board_data) == 0:
            ai_r, ai_c = best_move(board_data)
            board_data[ai_r][ai_c] = "O"

    new_table = "| | | |\n| :---: | :---: | :---: |\n"
    for r in range(3):
        new_table += "|"
        for c in range(3):
            val = board_data[r][c]
            if val == "X": new_table += " ❌ |"
            elif val == "O": new_table += " ⭕ |"
            else:
                new_table += f" [ ](https://github.com/MoreiraGabryel/MoreiraGabryel/issues/new?title=tttp:{r},{c}) |"
        new_table += "\n"

    winner = check_winner(board_data)
    if winner == 1:
        status = "**Status:** Fim de jogo."
        msg = "**Mensagem do Sistema:** `eu sempre Venço"
    elif not any(' ' in r for r in board_data):
        status = "**Status:** Empate!"
        msg = "**Mensagem do Sistema:** *Você foi um bom oponente.*"
    else:
        status = "**Status:** Sua vez!"
        msg = "**Mensagem do Sistema:** *Aguardando sua derrota...*"

    content = re.sub(r"\| \| \| \|\n\| :---: \| :---: \| :---: \|\n(?:\|.*?\|\n){3}", new_table, content)
    content = re.sub(r"\*\*Status:\*\*.*", status, content)
    content = re.sub(r"\*\*Mensagem do Sistema:\*\*.*", msg, content)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
