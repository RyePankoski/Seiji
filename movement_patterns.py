def get_valid_placement_squares(board, piece):
    valid_squares = set()  # Using a set to avoid duplicates

    if piece.name == "monarch":
        center = board.size // 2
        for y in range(board.size):
            for x in range(board.size):
                # Skip center square and occupied squares
                if not ((x == center and y == center) or board.get_piece((x, y))):
                    valid_squares.add((x, y))
        return list(valid_squares)

    if piece.name == "spy":
        center = board.size // 2
        for y in range(board.size):
            for x in range(board.size):
                # Skip center square and occupied squares
                if not board.get_piece((x, y)):
                    valid_squares.add((x, y))
        return list(valid_squares)

    # For other pieces, collect all squares that friendly pieces can move to
    for y in range(board.size):
        for x in range(board.size):
            board_piece = board.get_piece((x, y))
            if board_piece and board_piece.owner == piece.owner:
                if board_piece.name == "spy":
                    continue
                if board_piece.name == "palace":
                    # Add 5x5 area around palace
                    for dy in range(-2, 3):  # -2, -1, 0, 1, 2
                        for dx in range(-2, 3):  # -2, -1, 0, 1, 2
                            new_x, new_y = x + dx, y + dy
                            if (0 <= new_x < board.size and
                                    0 <= new_y < board.size and
                                    (board.get_piece((new_x, new_y)) is None or
                                     board.get_piece((new_x, new_y)).owner != piece.owner)):
                                valid_squares.add((new_x, new_y))
                else:
                    # Calculate actual squares by adding movement deltas to current position
                    moves = [(x + dx, y + dy) for dx, dy in board_piece.movement_squares]
                    # Filter moves based on board boundaries and piece ownership
                    valid_moves = [
                        (move_x, move_y) for move_x, move_y in moves
                        if 0 <= move_x < board.size and 0 <= move_y < board.size
                           and (board.get_piece((move_x, move_y)) is None
                                or board.get_piece((move_x, move_y)).owner != board_piece.owner)
                    ]
                    valid_squares.update(valid_moves)

    return list(valid_squares)


def get_valid_moves(piece, x, y, board):
    # Group movement squares by direction to check line of sight
    moves_by_direction = {}
    for dx, dy in piece.movement_squares:
        # Normalize the direction to handle multistep moves
        if dx != 0:
            dx_norm = dx // abs(dx)
        else:
            dx_norm = 0
        if dy != 0:
            dy_norm = dy // abs(dy)
        else:
            dy_norm = 0
        direction = (dx_norm, dy_norm)

        # Store the full move under its direction
        if direction not in moves_by_direction:
            moves_by_direction[direction] = []
        moves_by_direction[direction].append((dx, dy))

    valid_moves = []
    # Check each direction
    for direction, moves in moves_by_direction.items():
        # Sort moves by distance from current position
        moves.sort(key=lambda m: abs(m[0]) + abs(m[1]))

        # Check each move in this direction until we hit a piece
        for dx, dy in moves:
            move_x, move_y = x + dx, y + dy

            # Check board boundaries
            if not (0 <= move_x < board.size and 0 <= move_y < board.size):
                break

            target_piece = board.get_piece((move_x, move_y))
            if target_piece is None:
                # Empty square, add it and continue checking
                valid_moves.append((move_x, move_y))
            elif target_piece.owner != piece.owner:
                # Enemy piece - only add if not an unpromoted advisor
                if not (piece.name == "advisor" and not piece.promoted):
                    valid_moves.append((move_x, move_y))
                break
            else:
                # Friendly piece, stop checking this direction
                break

    return valid_moves
