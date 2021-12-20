class Game:
    hand_list = ['piedra', 'papel', 'tijera']
    players = []
    players_hand = []

    def __init__(self):
        self.players = []
        self.hand_option = []
        for i in Game.hand_list:
            self.hand_option.append(i)
            self.answers = []
            self.turn = 0

