class Game:
    NUM_MARBLES = 5
    NUM_PLAYERS = 2

    def __init__(self):
        self.sockets = []
        self.answers = []
        self.turn = 0
        self.action = []
        self.num_ronda = 0
        self.wins = [0,0]
