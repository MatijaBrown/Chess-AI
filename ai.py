import random

from common import *
import chess


def quiescence_search(alpha: int, beta: int, position: chess.ChessPosition) -> int:
    side = position.side_to_move
    legal_moves = position.legal_moves.copy()

    value = position.evaluate()

    if value >= beta:
        return beta
    if alpha < value:
        alpha = value

    for location in legal_moves.keys():
        piece = position.piece_at(location)
        targets = legal_moves[location]
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                loc = offset_of(x, y)
                flg = flag(loc)

                if targets & flg:
                    taking = position.piece_at(loc)

                    if abs(taking) == KING:
                        return position.side_to_move * float('inf')

                    en_passent = (flag(loc) & position.en_passent_targets) != 0
                    if en_passent:
                        taking = position.piece_at(loc - side * BOARD_SIZE)

                    if taking != NULL_PIECE:
                        position.move(chess.Move(location, loc, piece, taking, en_passent), True)
                        score = -quiescence_search(-beta, -alpha, position)
                        position.undo_last_move()

                        if score >= beta:
                            return beta
                        if score > alpha:
                            alpha = score

    return alpha


def nega_max(alpha: int, beta: int, depth: int, position: chess.ChessPosition) -> int:
    if position.draw:
        return 0
    elif position.checkmate:
        return position.side_to_move * float('inf')        

    if depth == 0:
        return quiescence_search(alpha, beta, position)

    side = position.side_to_move
    legal_moves = position.legal_moves.copy()

    for location in legal_moves.keys():
        piece = position.piece_at(location)
        targets = legal_moves[location]
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                loc = offset_of(x, y)
                flg = flag(loc)

                if targets & flg:
                    taking = position.piece_at(loc)

                    if abs(taking) == KING:
                        return position.side_to_move * float('inf')

                    en_passent = (flag(loc) & position.en_passent_targets) != 0
                    if en_passent:
                        taking = position.piece_at(loc - side * BOARD_SIZE)

                    position.move(chess.Move(location, loc, piece, taking, en_passent), True)
                    score = -nega_max(-beta, -alpha, depth - 1, position)
                    position.undo_last_move()

                    if score >= beta:
                        return beta
                    if score > alpha:
                        alpha = score
    
    return alpha


def calculate_best_move(position: chess.ChessPosition):
    side = position.side_to_move

    best_value = float("-inf")
    best_moves = []

    legal_moves = position.legal_moves.copy()

    for location in legal_moves.keys():
        piece = abs(position.piece_at(location))
        targets = legal_moves[location]
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                loc = offset_of(x, y)
                flg = flag(loc)

                if targets & flg:
                    taking = position.piece_at(loc)
                    en_passent = (flag(loc) & position.en_passent_targets) != 0
                    move = chess.Move(location, loc, side * piece, taking, en_passent)

                    position.move(move, True)
                    if side == BLACK:
                        score = -nega_max(float('-inf'), float('inf'), 2, position)
                    elif side == WHITE:
                        score = nega_max(float('-inf'), float('inf'), 2, position)
                    position.undo_last_move()

                    if score > best_value:
                        best_moves.clear()
                        best_value = score
                        best_moves.append(move)
                    elif score == best_value:
                        best_moves.append(move)
    
    picked_move = best_moves[random.randint(0, len(best_moves) - 1)]
    return picked_move