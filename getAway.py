from random import shuffle
from random import randint
import math
from copy import copy, deepcopy

from cards import Hand, Deck
from players import LowCardPolicy, MidCardPolicy, HighCardPolicy, HumanPlayer, RandomAgent, Rollout


class GetAwayGame:
    ACE_OF_SPADES = ('Spades', 'A', 12)
    MAX_GAMES = 100000

    def __init__(self, all_players, loser_count):
        ''' players: list of players
            loser_count: empty dictionary which keeps score '''
        self.all_players = all_players
        self.loser_count = loser_count

    def run_game(self, show_every_round, show_cpu_cards):
        self.deal_cards()
        players = copy(self.all_players)

        # shuffling list of players so that their order
        # in the game rotation is randomized
        shuffle(players)

        # game info variables:
        garbage = Hand([])
        table_cards = Hand([])
        starter = -1
        num_live_players = len(players)
        num_of_cards = {}
        cards_picked_up_from_table = {}
        for player in players:
            num_of_cards[player.name] = 12
            cards_picked_up_from_table[player.name] = Hand([])

        winners = []
        # Initializing game: first round decides who starts
        i=0
        while i<num_live_players:

            # First move of game - player plays ace of spades
            if i<1:
                for player in players:
                    if player.hand.has_specific_card(self.ACE_OF_SPADES):
                        starter = players.index( player )
                        table_cards.pick_up_card(
                            player.hand.pop_card(self.ACE_OF_SPADES)
                        )
                        i+=1
            # remaining players play their ace after first player
            else:
                # next player in rotation plays

                table_cards.pick_up_card(
                    players[(starter + i) % num_live_players].getAway_move(
                        table_cards, garbage, players, i, starter, True, winners, num_of_cards, cards_picked_up_from_table, num_live_players
                    )
                )
                i+=1

        # dump all cards after first round
        garbage.pick_up_cards( table_cards.pop_all_cards() )

        # central loop for game
        j=1
        while num_live_players>1:
            # begin a single round
            round_end_early = False
            i=0
            next_starting_player = players[starter]
            while i<num_live_players and (not round_end_early):

                # player takes turn
                current = players[(starter + i) % num_live_players]
                if show_cpu_cards:
                    if not isinstance(current, HumanPlayer):
                        current.show_cards()

                table_cards.pick_up_card( current.getAway_move(table_cards, garbage, players, i, starter, False, winners, num_of_cards, cards_picked_up_from_table, num_live_players) )

                num_of_cards[current.name] = current.hand.get_card_count()
                if cards_picked_up_from_table[current.name].has_specific_card(table_cards.get_top_card()):
                    cards_picked_up_from_table[current.name].pop_card(table_cards.get_top_card())

                # checking game status
                if not (i==0):
                    if table_cards.top_card_is_diffsuit():
                        round_end_early = True
                    elif table_cards.top_card_is_highest():
                        # checking if player who just played threw the highest card
                        next_starting_player = current

                if show_every_round:
                    self.print_status(current, table_cards)

                i+=1
            # loop breaks once everyone played, or round ended early (pick up)

            if round_end_early:
                if show_every_round:
                    print(f"{next_starting_player.name} picks up the table cards!")
                current_table_cards = table_cards.pop_all_cards()
                next_starting_player.pick_up_cards(
                    current_table_cards
                )
                cards_picked_up_from_table[next_starting_player.name].pick_up_cards(current_table_cards)
                num_of_cards[next_starting_player.name] = next_starting_player.hand.get_card_count()

            else:
                garbage.pick_up_cards( table_cards.pop_all_cards() )

            # case where next_starting_player must pick from garbage since
            # they start the next round
            if next_starting_player.hand.get_card_count() < 1:
                if show_every_round:
                    print(str(next_starting_player.name)+" picks a card from"
                          +" the garbage since they threw highest but are out!")

                garbage.shuffle_cards()
                num_of_cards[next_starting_player.name] = 1
                next_starting_player.pick_up_card( garbage.pop_card(1) )

            # removing winners:
            next_round_players = []
            for player in players:
                if player.hand.get_card_count() >= 1:
                    next_round_players.append(player)
                else:
                    winners.append(player)

            if show_every_round:
                print("End of Round status: ")
                for player in players:
                    print( f"{player.name} - {player.hand.get_card_count()}"
                           + " cards" )

            players.clear()
            players = next_round_players
            num_live_players = len(players)

            # setting up starting player for next round
            starter = players.index( next_starting_player )
            j+=1

        # at end of game, update loser count
        LOSER = players[0].name
        if LOSER in self.loser_count:
            self.loser_count[LOSER] += 1
        else:
            self.loser_count[LOSER] = 1

    def print_status(self, just_played, table_cards):
        ''' print status of game
            takes player who most recently played, garbage, and table cards
            to display status
        '''
        print(f"Most recent turn: {just_played.name}")
        print(f"table: ")
        table_cards.show_cards()
        print("----------------------------------------")

    def run_multiple_games(self, show_every_round, show_cpu_cards, count):
        if (count <= self.MAX_GAMES):
            for i in range(count):
                self.run_game(show_every_round, show_cpu_cards)
        else:
            print("Mumber of games must be less than " + str(self.MAX_GAMES))



    def deal_cards(self):
        split_decks = Deck().deal(len(self.all_players))
        i=0
        for player in self.all_players:
            player.set_hand( split_decks[i] )
            i+=1


# ---------------------------------------------------------------------------

def get_players():
    players = [None for x in range(4)]
    names = ["Agent1", "Agent2", "Agent3", "Agent4"]
    for i in range(4):
        selection = -1
        while selection not in [1,2,3,4,5,6]:
            print("Select the type for player "+str(i+1))
            print(" 1 - RandomAgent\n 2 - Heuristic1\n 3 - Heuristic2\n"
                  " 4 - Heuristic3\n 5 - Rollout\n 6 - Human")
            selection = int(input())

        name = ""
        while len(name) not in list(range(2,30)):
            print("Type the players name or leave blank (Agent"+str(i+1)+" default)")
            name = str(input())
            if len(name)==0:
                name = names[i]

        names[i] = name

        if selection==1:
            players[i] = RandomAgent(name=names[i])
        elif selection==2:
            players[i] = LowCardPolicy(name=names[i])
        elif selection==3:
            players[i] = MidCardPolicy(name=names[i])
        elif selection==4:
            players[i] = HighCardPolicy(name=names[i])
        elif selection==5:
            players[i] = Rollout(name=names[i])
        else:
            players[i] = HumanPlayer(name=names[i])
    return players

if __name__ == '__main__':
    # train_ai()
    all_players = get_players()
    loser_count = {}
    game = GetAwayGame( all_players, loser_count )

    interactive = False
    for player in all_players:
        if isinstance(player, HumanPlayer):
            interactive = True

    if interactive:
        game.run_game(True, False)

    else:
        rounds = int(input("How many games would you like to run (up to 100000): "))
        game.run_multiple_games(False, False, rounds)

    for name in loser_count:
        print(name + " couldn't get away " + str(loser_count[name]) + " time(s)!")
