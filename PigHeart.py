import os, sys
from random import shuffle, choice

TURN = 1

class StrVal(object):

	def __init__(self, symbol):

		self.symbol = symbol
		self.value = self.value( symbol )


	def __eq__(self, other):

		return self.symbol == other.symbol

	def value(self, symbol):

		if symbol.isdigit():
			return int(symbol)

		return { '♣': 0, '♦': 1, '♥': 2, '♠': 3, 'J':11, 'Q':12, 'K':13, 'A':14 }[ symbol ] 


class Card(object):

	def __init__(self, number, suit):

		self.number = StrVal( number ) 
		self.suit   = StrVal( suit )
		self.owner = None
		self.score = self.calculate_score()

	def calculate_score(self):

		if self.suit.symbol == '♥':
			return -self.number.value
		elif self.number.symbol == 'Q' and self.suit.symbol == '♠':
			return -50
		elif self.number.symbol == 'J' and self.suit.symbol == '♦':
			return 50
		else:
			return 0


	def __eq__(self, card):

		if type(card) != Card:
			return False

		return self.number.symbol == card.number.symbol and self.suit.symbol == card.suit.symbol

	def __lt__(self, card):

		if type(card) != Card:
			return False
			
		if self.number.value == card.number.value: # same number -> compare suit
			return self.suit.value < card.suit.value
		else:
			return self.number.value < card.number.value

	def __gt__(self, card):

		if type(card) != Card:
			return False
			
		if self.number.value == card.number.value: # same number -> compare suit
			return self.suit.value > card.suit.value
		else:
			return self.number.value > card.number.value

	def __repr__(self):

		return self.suit.symbol + self.number.symbol



class Player(object):

	def __init__(self, name, hand_cards):
		self.name = name
		self.hand_cards = hand_cards
		self.scores = 0
		self.first_move = False
		self.initialize_owner()

	def initialize_owner(self):
		
		for card in self.hand_cards:
			card.owner = self

	def re_get_hand_cards(self, hand_cards):

		self.hand_cards = hand_cards
		self.initialize_owner()

	def move_algorithm(self, moved_cards, possible_moves):

		return choice(possible_moves)

	def legal_move(self, moved_cards):

		possible_moves, follow_suit_cards = [], []

		if len(moved_cards) == 0:
			if Card('2', '♣') in self.hand_cards:
				possible_moves = [ Card('2', '♣') ]
			else:
				possible_moves = self.hand_cards
		else:
			first_suit = moved_cards[0].suit
			follow_suit_cards = [ card for card in self.hand_cards if card.suit == first_suit ]
			possible_moves = follow_suit_cards if len(follow_suit_cards)>0 else self.hand_cards

		next_card = self.move_algorithm( moved_cards, possible_moves )

		try:
			self.hand_cards.remove( next_card )
		except Exception:
			print( 'bug:', next_card )

		return next_card


class SmartPlayer(Player):

	def __init__(self, name, hand_cards):

		super().__init__(name, hand_cards)
				

	def lowest_score(self, possible_moves):

		lowest_card, lowest = None, 0
		for card in possible_moves:
			if card.score < lowest:
				lowest = card.score
				lowest_card = card
		return lowest_card if lowest_card is not None else max(possible_moves)

	def total_scores(self, moved_cards):

		return sum([card.score for card in moved_cards])

	def max_but_smaller_than_other(self, moved_cards, possible_moves):

		current_max_card = max( moved_cards )
		smaller_cards = [card for card in possible_moves if card < current_max_card] 
		return max(smaller_cards) if len(smaller_cards) > 0 else min(possible_moves)

	def move_algorithm(self, moved_cards, possible_moves):

		if len(moved_cards) == 0:
			if TURN < 4:
				no_score_bigger_cards = [ card for card in possible_moves if card.score == 0 ]
				return max( no_score_bigger_cards )
			else:
				return min( possible_moves )
		else:
			should_follow = (possible_moves[0].suit == moved_cards[0].suit)
			if not should_follow:
				return self.lowest_score( possible_moves )
			else:
				current_total_scores = self.total_scores( moved_cards )
				if current_total_scores > 0:
					return max( possible_moves )
				elif current_total_scores == 0:
					if TURN < 4:
						return max( possible_moves )
					elif len(moved_cards) == 3:
						return max( possible_moves )
					else:
						return self.max_but_smaller_than_other( moved_cards, possible_moves )
				else:
					return self.max_but_smaller_than_other( moved_cards, possible_moves )




class RealPlayer(Player):

	def __init__(self, name, hand_cards):

		super().__init__(name, self.rank_by_suit(hand_cards))

	def rank_by_suit(self, cards):

		Suits = { '♣': [], '♦': [], '♥': [], '♠': [] }
		for card in cards:
			Suits[ card.suit.symbol ].append( card )
		return sorted(Suits['♣']) + sorted(Suits['♦']) + sorted(Suits['♥']) + sorted(Suits['♠'])


	def show_hands_card(self):

		print( 'Current cards in hands:' )
		for option, card in enumerate(self.hand_cards):
			print( "({}).{}, ".format(option, card), end='' )
		#print( 'Options:', list(range(len(self.hand_cards))) )
		#print( 'Cards:  ', self.hand_cards )

	def check_input_option(self, possible_moves):

		option = input()

		if not option.isdigit():
			print("Input is not a digit!")
			return None

		option = int(option)

		if option >= len(self.hand_cards) or option < 0:
			print("Input option is out of range!")
			return None

		if self.hand_cards[ option ] not in possible_moves:
			print("Input option is not an valid move!")
			return None

		return self.hand_cards[ option ]


	def move_algorithm(self, moved_cards, possible_moves):

		self.show_hands_card()
		selected_card = None
		while not selected_card:
			selected_card = self.check_input_option( possible_moves )

		return selected_card









class PokerGame:

	def __init__(self, p1_name, p2_name, p3_name, p4_name):

		self.players = self.initialize_players( p1_name, p2_name, p3_name, p4_name )
		self.current_moved_cards = [] 		
		
	def initialize_players(self, p1_name, p2_name, p3_name, p4_name):

		pokers = self.create_poker()
		p1 = SmartPlayer( p1_name, pokers[:13] )
		p2 = SmartPlayer( p2_name, pokers[13:26] )
		p3 = SmartPlayer( p3_name, pokers[26:39] )
		p4 = RealPlayer( p4_name, pokers[39:] )

		return [p1, p2, p3, p4]

	def create_poker(self):

		pokers = []
		for num in range(2, 15):
			if num > 10:
				number = {11:'J', 12:'Q', 13:'K', 14:'A'}[num]
			else:
				number = str(num)
			pokers.append( Card(number, '♣') )
			pokers.append( Card(number, '♦') )
			pokers.append( Card(number, '♠') )
			pokers.append( Card(number, '♥') )

		shuffle( pokers )

		return pokers


	def find_first_move_player(self):

		for player in self.players:
			if Card('2', '♣') in player.hand_cards:
				player.first_move = True
				break


	def game_end(self):

		for player in self.players:
			if len(player.hand_cards) > 0:
				return False
		return True

	def get_next_first_move_player(self):

		for player_index, player in enumerate(self.players):
			if player.first_move:
				player.first_move = False
				return player_index
		assert(False)

	def update_current_moved_cards(self, current_player):

		card = current_player.legal_move( self.current_moved_cards )
		self.current_moved_cards.append( card )
		print( current_player.name, 'hands in', card )


	def total_scores(self):

		return sum([card.score for card in self.current_moved_cards])


	def calculate_scores(self):

		first_suit = self.current_moved_cards[0].suit
		follow_cards, unfollow_cards = [], []
		for card in self.current_moved_cards:
			if card.suit == first_suit:
				follow_cards.append( card )
			else:
				unfollow_cards.append( card )

		max_card = max( follow_cards )
		
		try:
			max_card.owner.first_move = True
		except Exception:
			print( 'Error:', max_card )
			import sys
			sys.exit(0)

		max_card.owner.scores += self.total_scores()
		print('Cards on board:', self.current_moved_cards)
		print( max_card.owner.name, 'gets this turn.(Get score %d)' % self.total_scores() )

		self.current_moved_cards = []


	def show_scores(self):

		print('--------------------Final players score:--------------------')
		for player in self.players:
			print( player.name, ':', player.scores )


	def start(self):

		global TURN

		TURN = 1
		
		self.find_first_move_player()

		while not self.game_end():

			print('********************** Turn %d **********************' % TURN)

			first_player_index = self.get_next_first_move_player() 
			
			for i in range(4):
				current_player_index = (first_player_index + i) % 4
				current_player = self.players[ current_player_index ]
				self.update_current_moved_cards( current_player )
			
			self.calculate_scores()

			TURN += 1

		self.show_scores()


	def play_more(self):

		#import sys
		#sys.stdout.close()
		for _ in range(1000):
			pokers = self.create_poker()
			for index, player in enumerate(self.players):
				player.re_get_hand_cards( pokers[index*13:index*13+13] )
				player.first_move = False
			self.start()

		print('---------------Average scores:----------------')
		for player in self.players:
			print( player.name, ':', player.scores/1000 )




if __name__ == '__main__':

	game = PokerGame('Ivor', 'Xaiver', 'GARO', 'Max')
	game.start()
	