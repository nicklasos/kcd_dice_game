"""
Command Line Interface for the KCD dice game.
This module provides a simple CLI for testing the game logic.
"""
import sys
from typing import List, Optional

from kcd_dice_game.game_logic import Game, InvalidMoveException, GameRuleException, GameStateException
from kcd_dice_game.utils.logger import logger


class GameCLI:
    """
    Command Line Interface for the KCD dice game.
    """
    def __init__(self):
        """Initialize the CLI with a new game."""
        self.game = Game()
        self.commands = {
            "help": self.show_help,
            "add": self.add_player,
            "start": self.start_turn,
            "roll": self.roll_again,
            "keep": self.keep_dice,
            "bank": self.bank_points,
            "state": self.show_state,
            "exit": self.exit_game
        }
    
    def run(self):
        """Run the CLI game loop."""
        print("Welcome to the KCD Dice Game CLI!")
        print("Type 'help' for a list of commands.")
        
        while True:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"Unknown command: {cmd}")
                    self.show_help([])
            except (InvalidMoveException, GameRuleException, GameStateException) as e:
                print(f"Game error: {e}")
            except KeyboardInterrupt:
                print("\nExiting game...")
                break
            except Exception as e:
                logger.exception(f"Unexpected error: {e}")
                print(f"An unexpected error occurred: {e}")
    
    def show_help(self, args: List[str]):
        """Show help information."""
        print("\nAvailable commands:")
        print("  help                  - Show this help message")
        print("  add <name>            - Add a player to the game")
        print("  start                 - Start a new turn")
        print("  roll                  - Roll the dice again")
        print("  keep <indices...>     - Keep dice at the specified indices (0-5)")
        print("  bank                  - Bank the current points and end the turn")
        print("  state                 - Show the current game state")
        print("  exit                  - Exit the game")
    
    def add_player(self, args: List[str]):
        """Add a player to the game."""
        if not args:
            print("Error: Player name required")
            return
        
        name = " ".join(args)
        self.game.add_player(name)
        print(f"Added player: {name}")
    
    def start_turn(self, args: List[str]):
        """Start a new turn."""
        try:
            self.game.start_turn()
            current_player = self.game.get_current_player()
            print(f"{current_player.name}'s turn started!")
            self._print_dice(self.game.dice_set.get_values())
        except GameStateException as e:
            print(f"Cannot start turn: {e}")
    
    def roll_again(self, args: List[str]):
        """Roll the dice again."""
        try:
            result = self.game.roll_again()
            print("Rolled dice:")
            self._print_dice(result)
            
            # Show current score
            print(f"Current turn score: {self.game.current_turn_score}")
        except GameStateException as e:
            print(f"Cannot roll: {e}")
    
    def keep_dice(self, args: List[str]):
        """Keep dice at the specified indices."""
        if not args:
            print("Error: Dice indices required")
            return
        
        try:
            indices = [int(idx) for idx in args]
            self.game.keep_dice(indices)
            print("Kept dice at indices:", ", ".join(args))
            self._print_dice(self.game.dice_set.get_values())
            print(f"Current turn score: {self.game.current_turn_score}")
        except ValueError:
            print("Error: Invalid dice indices")
        except GameStateException as e:
            print(f"Cannot keep dice: {e}")
    
    def bank_points(self, args: List[str]):
        """Bank the current points and end the turn."""
        try:
            points = self.game.bank_points()
            current_player = self.game.get_current_player()
            print(f"Banked {points} points for {current_player.name}")
            print(f"{current_player.name}'s total score: {current_player.score}")
            
            # Check if game is over
            if self.game.is_game_over():
                winner = self.game.get_winner()
                print(f"\nGame over! {winner.name} wins with {winner.score} points!")
        except GameStateException as e:
            print(f"Cannot bank points: {e}")
    
    def show_state(self, args: List[str]):
        """Show the current game state."""
        state = self.game.get_state()
        
        print("\nGame State:")
        print(f"Current player: {state['current_player']}")
        print(f"Current turn score: {state['current_turn_score']}")
        
        print("\nPlayers:")
        for player in state["players"]:
            print(f"  {player['name']}: {player['score']} points")
        
        print("\nDice:")
        for i, die in enumerate(state["dice"]):
            status = "kept" if die["kept"] else "available"
            print(f"  Die {i}: {die['value']} ({status})")
        
        print(f"\nTurn started: {state['turn_started']}")
        print(f"Game over: {state['game_over']}")
        
        # Show available actions
        actions = self.game.get_available_actions()
        print("\nAvailable actions:", ", ".join(actions))
    
    def exit_game(self, args: List[str]):
        """Exit the game."""
        print("Thanks for playing!")
        sys.exit(0)
    
    def _print_dice(self, dice_values: List[int]):
        """Print the current dice values with their indices."""
        print("Current dice:")
        for i, die in enumerate(self.game.dice_set.dice):
            status = "kept" if die.kept else "available"
            print(f"  Die {i}: {die.value} ({status})")


def main():
    """Entry point for the CLI."""
    cli = GameCLI()
    cli.run()


if __name__ == "__main__":
    main()
