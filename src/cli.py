"""
Command Line Interface for the KCD dice game.
This module provides a simple CLI for testing the game logic.
"""
import sys
from typing import List, Optional

from src.game_logic import Game, InvalidMoveException, GameRuleException, GameStateException
from src.utils.logger import logger


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
        print("Welcome to the Kingdom Come: Deliverance Dice Game!")
        print("Type 'help' to see available commands.")
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"Unknown command: {cmd}. Type 'help' to see available commands.")
            
            except (InvalidMoveException, GameRuleException, GameStateException) as e:
                print(f"Game error: {str(e)}")
            except KeyboardInterrupt:
                print("\nExiting game...")
                break
            except Exception as e:
                logger.exception("Unexpected error")
                print(f"An error occurred: {str(e)}")
    
    def show_help(self, args: List[str]):
        """Show available commands."""
        print("\nAvailable commands:")
        print("  help                - Show this help message")
        print("  add <player_name>   - Add a new player")
        print("  start               - Start a new turn")
        print("  roll                - Roll available dice")
        print("  keep <indices>      - Keep dice at specified indices (e.g., 'keep 0 2 4')")
        print("  bank                - Bank points and end turn")
        print("  state               - Show current game state")
        print("  exit                - Exit the game")
        
        # Show available actions based on current game state
        actions = self.game.get_available_actions()
        print("\nAvailable actions in current state:", ", ".join(actions))
    
    def add_player(self, args: List[str]):
        """Add a new player to the game."""
        if not args:
            print("Please provide a player name. Usage: add <player_name>")
            return
        
        player_name = " ".join(args)
        player = self.game.add_player(player_name)
        print(f"Added player: {player.name}")
    
    def start_turn(self, args: List[str]):
        """Start a new turn."""
        dice_values = self.game.start_turn()
        print(f"Started turn for {self.game.current_player.name}")
        self._print_dice(dice_values)
        
        # Check if the roll has any scoring dice
        if not self.game._turn_started:
            print(f"Bust! No scoring dice. Turn ended for {self.game.current_player.name}")
    
    def roll_again(self, args: List[str]):
        """Roll available dice."""
        dice_values = self.game.roll_again()
        print("Rolled available dice:")
        self._print_dice(self.game.dice_set.values)
        
        # Check if the roll has any scoring dice
        if not self.game._turn_started:
            print(f"Bust! No scoring dice. Turn ended for {self.game.current_player.name}")
    
    def keep_dice(self, args: List[str]):
        """Keep dice at specified indices."""
        if not args:
            print("Please provide dice indices to keep. Usage: keep <indices>")
            return
        
        try:
            indices = [int(idx) for idx in args]
        except ValueError:
            print("Invalid indices. Please provide numbers only.")
            return
        
        score = self.game.keep_dice(indices)
        print(f"Kept dice at indices {indices} for {score} points")
        print(f"Current turn score: {self.game.current_player.turn_score}")
        
        # Check if all dice are kept (full clear)
        if not self.game.dice_set.kept_dice and self.game._turn_started:
            print("Full clear! All dice have been scored. You can roll all dice again.")
        
        self._print_dice(self.game.dice_set.values)
    
    def bank_points(self, args: List[str]):
        """Bank points and end turn."""
        total_score = self.game.bank()
        player_name = self.game.current_player.name
        print(f"{player_name} banked points. Total score: {total_score}")
        
        if self.game.is_game_over:
            print(f"Game over! {player_name} has won with {total_score} points!")
            self.show_state([])
            sys.exit(0)
    
    def show_state(self, args: List[str]):
        """Show current game state."""
        state = self.game.get_game_state()
        
        print("\nCurrent Game State:")
        print("-------------------")
        
        print("Players:")
        for player in state["players"]:
            current = "* " if player["name"] == state["current_player"] else "  "
            print(f"{current}{player['name']}: Turn: {player['turn_score']}, Total: {player['total_score']}")
        
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


if __name__ == "__main__":
    cli = GameCLI()
    cli.run()
