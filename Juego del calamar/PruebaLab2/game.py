class Game():
    NUM_MARBLES = 5
    NUM_PLAYERS = 2
    def __init__(self):
        self.sockets = []
        self.marbles = []
        for i in range(0, Game.NUM_PLAYERS):
            self.marbles.append(Game.NUM_MARBLES)
            self.answers = []
            self.turn = 0