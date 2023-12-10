def check_winner(board: list):
    # remove dots
    test_board = [i if i != "." else None for i in board]

    # 0 1 2
    # 3 4 5
    # 6 7 8
    checks = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
    for x1, x2, x3 in checks:
        if test_board[x1] and test_board[x1] == test_board[x2] == test_board[x3]:
            return test_board[x1]

    return None
