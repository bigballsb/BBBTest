#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from time import sleep

import colorama

from rummy.controller.ai_controller import AiController
from rummy.controller.human_controller import HumanController
from rummy.game.players import Players
from rummy.game.round import Round
from rummy.game.score import Score
from rummy.player.human import Human
from rummy.ui.menu_action_dialog import MenuActionDialog
from rummy.ui.user_input import UserInput
from rummy.ui.view import View
from rummy.view.round_view import RoundView


class Play:
    def __init__(self):
        print('Welcome to Python Rummy')
        self.colorama()
        players = Players()
        players.choose_players()
        players.choose_opponents()
        self.players = players.get_players()
        self.ai_only = players.is_ai_only()
        self.score = Score(self.players)
        self.round = Round(self.players)
        self.round.deal_cards(self.players)
        self.play_game()
        self.rupee_value = 2
        self.check_game_objective = self.check_game_objective
        self.calculate_score = self.calculate_score
        self.update_scores = self.update_scores

    @staticmethod
    def colorama():
        if 'PYCHARM_HOSTED' in os.environ:
            convert = False  # in PyCharm, we should disable convert
            strip = False
        else:
            convert = None
            strip = None
        colorama.init(convert=convert, strip=strip)

    def play_game(self):
        while self.round.last_turn != len(self.players):
            action = controller.get_player_action(player)  # Assuming you have a method that gets the player's action
            if action in ['declare', 'first_drop', 'middle_drop', 'auto_drop', 'invalid_declare']:
                self.update_scores(self.players, action, player)
            self.round.prepare_turn()
            player = self.players[self.round.current_player]
            player.turn(self.round)
            # Todo: Views should be agnostic. Each template will have placeholders for data.
            # Todo: Player should return data to be displayed in views placeholders.
            controller = self._select_player_controller(player)
            controller.show_start_turn(player)
            controller.show_knocked(player)
            controller.draw_card(player)
            controller.show_end_turn(player)
            controller.discard_or_knock(player)
            controller.show_discard(player)
            self.round.end_turn()
        View.render(self.end_round())
        sleep(1.2)
        if self.score.is_end_of_game():
            View.render(self.score.show_winners())
        else:
            self.start_new_round()

    def update_scores(self, players, action, player):
        # Calculate the score for the given player based on the action
        # action can be 'declare', 'first_drop', 'middle_drop', 'auto_drop', or 'invalid_declare'

        if action == 'declare':
            # Check if the player meets the game objective
            if self.check_game_objective(player):
                player.score = 0
                # Calculate scores for the other players based on their cards
                for other_player in players:
                    if other_player != player:
                        other_player.score = self.calculate_score(other_player)
            else:
                player.score = 80
        elif action == 'first_drop':
            player.score = 20
        elif action == 'middle_drop':
            player.score = 40
        elif action == 'auto_drop':
            player.score = 40
        elif action == 'invalid_declare':
            player.score = 80

        # Calculate the winnings for the declaring player
        if action in ['declare', 'invalid_declare']:
            winner = player
            winnings = sum(p.score for p in players if p != winner) * self.rupee_value
            winner.winnings += winnings

    def check_game_objective(self, player):
        def is_sequence(cards):
            previous_rank_value = None
            for card in cards:
                if previous_rank_value is not None and card.rank_value != previous_rank_value + 1:
                    return False
                previous_rank_value = card.rank_value
            return True

        def is_pure_sequence(cards):
            for card in cards:
                if card.is_wild:
                    return False
            return True

        # Group cards by suit
        grouped_cards = {}
        for card in player.hand:
            if card.suit not in grouped_cards:
                grouped_cards[card.suit] = []
            grouped_cards[card.suit].append(card)

        # Sort cards by rank
        for suit, cards in grouped_cards.items():
            cards.sort(key=lambda card: card.rank_value)

        pure_sequence_found = False
        sequence_count = 0

        for suit, cards in grouped_cards.items():
            sequence_start = 0
            while sequence_start < len(cards) - 2:
                sequence_end = sequence_start + 2
                while sequence_end < len(cards) and is_sequence(cards[sequence_start:sequence_end + 1]):
                    sequence_end += 1

                if sequence_end - sequence_start >= 2:
                    if not pure_sequence_found and is_pure_sequence(cards[sequence_start:sequence_end]):
                        pure_sequence_found = True
                    sequence_count += 1

                sequence_start = sequence_end - 1

        return pure_sequence_found and sequence_count >= 2

    def calculate_score(self, player):
        # Calculate the score for a player based on their cards according to the Points Rummy rules.

        score = 0
        for card in player.hand:
            if card.rank in ["J", "Q", "K", "A"]:
                score += 10
            else:
                score += int(card.rank)
        return score
    
    def _select_player_controller(self, player):
        if isinstance(player, Human):
            controller = HumanController
        else:
            controller = AiController
        return controller

    def start_new_round(self):
        self.round.rotate_first_player()
        if not self.ai_only:
            self.confirm_start_new_round()
        self.round.prepare_new_round()
        self.round.deal_cards(self.players)
        self.play_game()

    @staticmethod
    def confirm_start_new_round():
        UserInput.create_input(MenuActionDialog.next_round())

    def end_round(self):
        self.score.update_player_scores()
        return RoundView.this_round_score(
            self.score.get_end_of_round_scores(),
            self.score.get_current_game_scores()
        )


# start game
if __name__ == "__main__":
    Play()
