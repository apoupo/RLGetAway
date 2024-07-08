from abc import ABC, abstractmethod
from cards import Hand, Deck
from random import randint, shuffle
from copy import copy, deepcopy


class Player(ABC):

    def __init__(self, name, hand=[]):
        ''' Given name, and hand (list of card tuples), initializes player '''
        self.hand = Hand(hand)
        self.name = name
        self.rounds_played = 0

    def set_hand(self, hand):
        self.hand = Hand(hand)

    def show_cards(self):
        print(str(self.name))
        self.hand.show_cards()

    def pick_up_cards(self, c):
        self.hand.pick_up_cards(c)

    def pick_up_card(self, c):
        self.hand.pick_up_card(c)

    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        ''' abstract method. table_cards is a Hand
            containing cards on the table,

            * function should return the card played by the player
            * it should be a valid move depending on the table cards.
        '''
        pass

class HumanPlayer(Player):
    ''' human player which interacts with game through command line '''
    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        selection = 0
        self.hand.cards = sorted(self.hand.cards, key=lambda element: (element[0], element[2]))
        print("Would you like to see your cards? (y/n)")
        show_player_cards = input()
        if ( show_player_cards.lower() == 'y' ):
            self.hand.show_cards()

        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()
            if self.hand.has_suit( table_suit ):
                # Case 1 - player has the live suit
                valid_move = False
                while not valid_move:
                    print("(Suited) Enter the index of the"
                    + " card you would like to play: ")
                    selection = int(input())
                    valid_move = self.hand.get_card_suit(selection)==table_suit
            else:
                # Case 2 - player does not have live suit
                valid_moves = list(range(1, (self.hand.get_card_count()+1)))
                while not (selection in valid_moves):
                    print("(Any) Enter the index of the"
                    + " card you would like to play: ")
                    selection = int(input())
        else:
            # Case 3 - player is starting round
            valid_moves = list(range(1, (self.hand.get_card_count()+1)))
            while not (selection in valid_moves):
                print("(Start of Round) Enter the index of the"
                + " card you would like to play: ")
                selection = int(input())

        return self.hand.pop_card(selection)
    
class LowCardPolicy(Player):
    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        selection = 0
        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()
            if self.hand.has_suit( table_suit ):
                # Case 1 - player has the live suit
                card_values = [ card[2] if card[0]==table_suit else -1
                                for card in self.hand.cards ]
                selection = card_values.index(min(card_values))+1
            else:
                # Case 2 - player does not have live suit
                card_values = [ card[2] for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1
        else:
            # Case 3 - player is starting a round
            card_values = [ card[2] for card in self.hand.cards ]
            selection = card_values.index(min(card_values))+1

        return self.hand.pop_card( selection )


class MidCardPolicy(Player):
    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        selection = 0
        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()
            if self.hand.has_suit( table_suit ):
                selection = 0
                card_values = [ card[2] if card[0]==table_suit else -1
                                for card in self.hand.cards ]
                table_cards_val = [ card[2] if card[0]==table_suit else -1
                                for card in table_cards.cards ]
                maxCard = max(table_cards_val)
                while card_values[selection] == -1:
                    selection += 1
                for i in range(len(card_values)):
                    if card_values[i] > card_values[selection] and card_values[i] < maxCard:
                        selection = i
                selection += 1
            else:
                # Case 2 - player does not have live suit
                card_values = [ card[2] for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1
        else:
            # Case 3 - player is starting a round
            card_values = [ card[2] for card in self.hand.cards ]
            selection = card_values.index(min(card_values))+1

        return self.hand.pop_card( selection )

class HighCardPolicy(Player):
    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        selection = 0
        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()
            if self.hand.has_suit( table_suit ):
                card_values = [ card[2] if card[0]==table_suit else -1
                                for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1

            else:
                # Case 2 - player does not have live suit
                card_values = [ card[2] for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1
        else:
            # Case 3 - player is starting a round
            card_values = [ card[2] for card in self.hand.cards ]
            selection = card_values.index(max(card_values))+1

        return self.hand.pop_card( selection )
class RandomAgent(Player):
    ''' CPU player which selects cards at random to play '''
    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        if self.hand.get_card_count() == 1:
            return self.hand.pop_card(1)
        selection = 0
        # note: randint includes end points, range() does not
        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()

            if self.hand.has_suit( table_suit ):
                # Case 1 - player has the live suit
                self.hand.shuffle_cards()
                end = self.hand.get_card_count()+1
                for i in range(1,  end):
                    if self.hand.get_card_suit(i) == table_suit:
                        selection = i
                        i = end
            else:
                # Case 2 - player does not have live suit
                selection = randint(1, self.hand.get_card_count())
        else:
            # Case 3 - player is starting round (any)
            selection = randint(1, self.hand.get_card_count())

        return self.hand.pop_card( selection )
    

class HumanLikeCPU(Player):
    ''' human-like CPU - Always selects highest possible card
    Removed this entirely'''
    def getAway_move(self, table_cards, num_live_players = 0):
        selection = 0
        if table_cards.get_card_count() > 0:
            table_suit = table_cards.get_bottom_suit()
            if self.hand.has_suit( table_suit ):
                # Case 1 - player has the live suit
                card_values = [ card[2] if card[0]==table_suit else -1
                                for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1
            else:
                # Case 2 - player does not have live suit
                card_values = [ card[2] for card in self.hand.cards ]
                selection = card_values.index(max(card_values))+1
        else:
            # Case 3 - player is starting a round
            card_values = [ card[2] for card in self.hand.cards ]
            selection = card_values.index(max(card_values))+1

        return self.hand.pop_card( selection )

class Rollout(Player):

    def getAway_move(self, table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players = 0):
        lcAverageScore = 0
        mcAverageScore = 0
        hcAverageScore = 0
        remainingCards = Deck()
        for card in table_cards.cards:
            remainingCards.full_deck.remove(card)

        for card in garbage.cards :
            remainingCards.full_deck.remove(card)

        for card in self.hand.cards:
            remainingCards.full_deck.remove(card)

        for player in players:
            if player.name == self.name:
                continue
            for card in cards_picked_up_from_table[player.name].cards:
                remainingCards.full_deck.remove(card)


        lcPolicy = LowCardPolicy(self.name, deepcopy(self.hand.cards))
        mcPolicy = MidCardPolicy(self.name, deepcopy(self.hand.cards))
        hcPolicy = HighCardPolicy(self.name, deepcopy(self.hand.cards))
        for j in range(10):
            shuffle(remainingCards.full_deck)
            itr = 0
            playersCopy = deepcopy(players)
            for k in range(len(playersCopy)):
                if playersCopy[k].name == self.name:
                    continue
                playersCopy[k].hand = deepcopy(cards_picked_up_from_table[playersCopy[k].name])
                for m in range(num_of_cards[playersCopy[k].name]-cards_picked_up_from_table[playersCopy[k].name].get_card_count()):
                    playersCopy[k].hand.pick_up_card(remainingCards.full_deck[itr])
                    itr += 1


            table_cards_copy = deepcopy(table_cards)
            garbage_copy = deepcopy(garbage)
            winners_copy = deepcopy(winners)
            players_copy = deepcopy(playersCopy)
            players_copy[(starter+i)%num_live_players] = deepcopy(lcPolicy)
            lcAverageScore += runRoundsAndCalculatePoints(table_cards_copy, garbage_copy, players_copy, i, starter, isFirstRound, winners_copy, num_live_players, 1, num_of_cards, cards_picked_up_from_table)



            table_cards_copy = deepcopy(table_cards)
            garbage_copy = deepcopy(garbage)
            winners_copy = deepcopy(winners)
            players_copy = deepcopy(playersCopy)
            players_copy[(starter+i)%num_live_players] = deepcopy(mcPolicy)
            mcAverageScore += runRoundsAndCalculatePoints(table_cards_copy, garbage_copy, players_copy, i, starter, isFirstRound, winners_copy, num_live_players, 1, num_of_cards, cards_picked_up_from_table)


            table_cards_copy = deepcopy(table_cards)
            garbage_copy = deepcopy(garbage)
            winners_copy = deepcopy(winners)
            players_copy = deepcopy(playersCopy)
            players_copy[(starter+i)%num_live_players] = deepcopy(hcPolicy)
            hcAverageScore += runRoundsAndCalculatePoints(table_cards_copy, garbage_copy, players_copy, i, starter, isFirstRound, winners_copy, num_live_players, 1, num_of_cards, cards_picked_up_from_table)


        if lcAverageScore < mcAverageScore and lcAverageScore < hcAverageScore:
            card = lcPolicy.getAway_move(table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players)
            return self.hand.pop_card(card)
        elif mcAverageScore < lcAverageScore and mcAverageScore < hcAverageScore:
            card = mcPolicy.getAway_move(table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players)
            return self.hand.pop_card(card)
        else:
            card = hcPolicy.getAway_move(table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players)
            return self.hand.pop_card(card)



def runRoundsAndCalculatePoints(table_cards, garbage, players, i, starter, isFirstRound, winners, num_live_players, changeToWhat, num_of_cards, cards_picked_up_from_table):
    playerName = players[(starter + i) % num_live_players].name
    if isFirstRound:
        while i<num_live_players:
            # next player in rotation plays
            table_cards.pick_up_card(
                players[(starter + i) % num_live_players].getAway_move(
                    table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players
                )
            )
            i+=1
        
        round = 2
        # dump all cards after first round
        garbage.pick_up_cards( table_cards.pop_all_cards() )

        # central loop for game
        j=1
        while num_live_players>1 and round < 5:
            if round == 2:
                if changeToWhat == 0:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = LowCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
                elif changeToWhat == 1:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = MidCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
                else:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = HighCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
            # begin a single round
            round_end_early = False
            i=0
            next_starting_player = players[starter]
            while i<num_live_players and (not round_end_early):

                # player takes turn
                current = players[(starter + i) % num_live_players]

                table_cards.pick_up_card( current.getAway_move(table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players) )

                # checking game status
                if not (i==0):
                    if table_cards.top_card_is_diffsuit():
                        round_end_early = True
                    elif table_cards.top_card_is_highest():
                        # checking if player who just played threw the highest card
                        next_starting_player = current

                
                i+=1
            # loop breaks once everyone played, or round ended early (pick up)

            if round_end_early:

                next_starting_player.pick_up_cards(
                    table_cards.pop_all_cards()
                )

            else:
                garbage.pick_up_cards( table_cards.pop_all_cards() )

            # case where next_starting_player must pick from garbage since
            # they start the next round
            if next_starting_player.hand.get_card_count() < 1:

                garbage.shuffle_cards()
                next_starting_player.pick_up_card( garbage.pop_card(1) )

            # removing winners:
            next_round_players = []
            for player in players:
                if player.hand.get_card_count() >= 1:
                    next_round_players.append(player)
                else:
                    winners.append(player)


            players.clear()
            players = next_round_players
            num_live_players = len(players)

            # setting up starting player for next round
            starter = players.index( next_starting_player )
            j+=1
            round += 1
        
        for player in players:
            if player.name == playerName:
                card_values = [ card[2]
                                for card in player.hand.cards]
                return sum(card_values)
        return 0
    else:
        round = 1

        # central loop for game
        j=1
        while num_live_players>1 and round < 5:
            if round == 2:
                if changeToWhat == 0:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = LowCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
                elif changeToWhat == 1:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = MidCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
                else:
                    for m in range(len(players)):
                        if players[m].name == playerName:
                            players[m] = HighCardPolicy(players[m].name, deepcopy(players[m].hand.cards))
            # begin a single round
            round_end_early = False
            next_starting_player = players[starter]
            while i<num_live_players and (not round_end_early):

                # player takes turn
                current = players[(starter + i) % num_live_players]

                table_cards.pick_up_card( current.getAway_move(table_cards, garbage, players, i, starter, isFirstRound, winners, num_of_cards, cards_picked_up_from_table, num_live_players) )

                # checking game status
                if not (i==0):
                    if table_cards.top_card_is_diffsuit():
                        round_end_early = True
                    elif table_cards.top_card_is_highest():
                        # checking if player who just played threw the highest card
                        next_starting_player = current

                
                i+=1
            # loop breaks once everyone played, or round ended early (pick up)

            if round_end_early:

                next_starting_player.pick_up_cards(
                    table_cards.pop_all_cards()
                )

            else:
                garbage.pick_up_cards( table_cards.pop_all_cards() )

            # case where next_starting_player must pick from garbage since
            # they start the next round
            if next_starting_player.hand.get_card_count() < 1:

                garbage.shuffle_cards()
                next_starting_player.pick_up_card( garbage.pop_card(1) )

            # removing winners:
            next_round_players = []
            for player in players:
                if player.hand.get_card_count() >= 1:
                    next_round_players.append(player)
                else:
                    winners.append(player)


            players.clear()
            players = next_round_players
            num_live_players = len(players)

            # setting up starting player for next round
            starter = players.index( next_starting_player )
            i = 0
            j+=1
            round += 1
        
        for player in players:
            if player.name == playerName:
                card_values = [ card[2]
                                for card in player.hand.cards]
                return sum(card_values)
        return 0


        

        
