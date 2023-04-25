# -*- coding: utf-8 -*-

from rummy.deck.card import Card

class Rank:
    suits = ['♠', '♣', '♥', '♦']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    @property
    def ranked_cards(self):
        return [Card(rank, suit) for rank in self.ranks for suit in self.suits]

    def __repr__(self):
        return str([(i, str(card)) for i, card in enumerate(self.ranked_cards)])

    @staticmethod
    def get_suit_and_rank_key(card):
        return Rank.suits.index(card.suit), Rank.ranks.index(card.rank)

    @staticmethod
    def get_rank_key(card):
        return Rank.ranks.index(card.rank)

if __name__ == '__main__':
    print(Rank().ranked_cards)