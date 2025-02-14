class Piece:
    def __init__(self, name, movement_squares, owner, promoted=False):
        self.name = name
        self.movement_squares = movement_squares
        self.owner = owner
        self.promoted = promoted
