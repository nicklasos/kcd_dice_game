"""
Game module for the KCD dice game.
Contains the main Game class that manages the overall game state.
"""
from typing import List, Optional, Dict, Any, Tuple

from game_logic.dice import DiceSet
from game_logic.player import Player
from game_logic.scoring import ScoreCalculator
from game_logic.exceptions import InvalidMoveException, GameRuleException, GameStateException
from utils.logger import logger


class Game:
    """
    Main game class that manages the overall game state.
    Handles turn logic, player management, and game rules.
    """
    def __init__(self):
        """Initialize a new game with no players."""
        self._players: List[Player] = []
        self._current_player_idx: int = 0
        self._dice_set: DiceSet = DiceSet()
        self._score_calculator: ScoreCalculator = ScoreCalculator()
        self._turn_started: bool = False
        self._game_over: bool = False
        
        logger.info("New game initialized")
    
    @property
    def players(self) -> List[Player]:
        """Get the list of players in the game."""
        return self._players.copy()
    
    @property
    def current_player(self) -> Optional[Player]:
        """Get the current player."""
        if not self._players:
            return None
        return self._players[self._current_player_idx]
    
    @property
    def dice_set(self) -> DiceSet:
        """Get the dice set used in the game."""
        return self._dice_set
    
    @property
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self._game_over
    
    def add_player(self, name: str) -> Player:
        """
        Add a new player to the game.
        
        Args:
            name: Player's name
            
        Returns:
            The newly created Player object
            
        Raises:
            GameStateException: If the game has already started
            ValueError: If a player with the same name already exists
        """
        if self._turn_started:
            raise GameStateException("Cannot add players after the game has started")
        
        # Check for duplicate names
        if any(player.name == name for player in self._players):
            raise ValueError(f"A player with the name '{name}' already exists")
        
        player = Player(name)
        self._players.append(player)
        logger.info(f"Added player '{name}' to the game")
        return player
    
    def start_turn(self) -> List[int]:
        """
        Start a new turn for the current player by rolling all dice.
        
        Returns:
            List of dice values from the roll
            
        Raises:
            GameStateException: If there are no players or the game is over
            GameRuleException: If the turn has already started
        """
        if not self._players:
            raise GameStateException("Cannot start turn with no players")
        
        if self._game_over:
            raise GameStateException("Game is already over")
        
        if self._turn_started:
            raise GameRuleException("Turn has already started")
        
        self._turn_started = True
        dice_values = self._dice_set.roll_all()
        
        # Check if the roll has any scoring dice
        if not self._score_calculator.has_scoring_dice(dice_values):
            logger.info(f"Player '{self.current_player.name}' busted on initial roll")
            self.bust()
            return dice_values
        
        logger.info(f"Started turn for player '{self.current_player.name}' with roll {dice_values}")
        return dice_values
    
    def keep_dice(self, indices: List[int]) -> int:
        """
        Keep the dice at the specified indices and calculate the score.
        
        Args:
            indices: List of indices of dice to keep
            
        Returns:
            Score for the kept dice
            
        Raises:
            GameStateException: If the turn hasn't started or the game is over
            InvalidMoveException: If the dice cannot be kept (not scoring)
        """
        if not self._turn_started:
            raise GameStateException("Turn has not started")
        
        if self._game_over:
            raise GameStateException("Game is already over")
        
        # Get the values of the dice to keep
        try:
            dice_to_keep = [self._dice_set.dice[idx] for idx in indices]
        except IndexError:
            raise InvalidMoveException("Invalid dice index")
        
        # Check if any of the dice are already kept
        if any(die.kept for die in dice_to_keep):
            raise InvalidMoveException("Cannot keep dice that are already kept")
        
        # Get the values of the dice to keep
        values_to_keep = [die.value for die in dice_to_keep]
        
        # Check if these dice are scorable
        scorable_indices = self._score_calculator.get_scorable_dice_indices(self._dice_set.available_values)
        if not all(idx in scorable_indices for idx in indices):
            raise InvalidMoveException("Cannot keep non-scoring dice")
        
        # Keep the dice
        self._dice_set.keep_dice(indices)
        
        # Calculate score for the kept dice
        score = self._score_calculator.calculate_score(values_to_keep)
        
        # Add score to current player's turn
        self.current_player.add_to_turn(score)
        
        logger.info(f"Player '{self.current_player.name}' kept dice at indices {indices} for {score} points")
        
        # Check if all dice are kept (full clear)
        if self._dice_set.is_all_kept():
            logger.info(f"Player '{self.current_player.name}' achieved full clear")
            self._dice_set.release_all()  # Release all dice for continued play
        
        return score
    
    def roll_again(self) -> List[int]:
        """
        Roll the available (not kept) dice.
        
        Returns:
            List of new dice values for the available dice
            
        Raises:
            GameStateException: If the turn hasn't started or the game is over
            GameRuleException: If there are no available dice to roll
        """
        if not self._turn_started:
            raise GameStateException("Turn has not started")
        
        if self._game_over:
            raise GameStateException("Game is already over")
        
        available_dice = self._dice_set.available_dice
        if not available_dice:
            # All dice are kept, release them for a new roll (full clear)
            self._dice_set.release_all()
            available_dice = self._dice_set.dice
        
        dice_values = self._dice_set.roll_available()
        
        # Check if the roll has any scoring dice
        if not self._score_calculator.has_scoring_dice(self._dice_set.available_values):
            logger.info(f"Player '{self.current_player.name}' busted on roll")
            self.bust()
            return dice_values
        
        logger.info(f"Player '{self.current_player.name}' rolled again: {dice_values}")
        return dice_values
    
    def bank(self) -> int:
        """
        Bank the current player's turn score and end their turn.
        
        Returns:
            The player's new total score
            
        Raises:
            GameStateException: If the turn hasn't started or the game is over
            GameRuleException: If no dice have been kept this turn
        """
        if not self._turn_started:
            raise GameStateException("Turn has not started")
        
        if self._game_over:
            raise GameStateException("Game is already over")
        
        if not self._dice_set.kept_dice:
            raise GameRuleException("Cannot bank without keeping any dice")
        
        # Bank the points
        total_score = self.current_player.bank_points()
        
        # Check if the player has won
        if self.current_player.has_won():
            self._game_over = True
            logger.info(f"Game over! Player '{self.current_player.name}' has won with {total_score} points")
        else:
            # End turn and move to next player
            self._end_turn()
        
        return total_score
    
    def bust(self) -> None:
        """
        Handle a bust (no scoring dice in a roll).
        Resets the current player's turn score and ends their turn.
        """
        self.current_player.reset_turn()
        self._end_turn()
        logger.info(f"Player '{self.current_player.name}' busted and lost their turn score")
    
    def _end_turn(self) -> None:
        """
        End the current player's turn and move to the next player.
        """
        self._turn_started = False
        self._dice_set.release_all()
        
        # Move to the next player
        self._current_player_idx = (self._current_player_idx + 1) % len(self._players)
        logger.info(f"Turn ended, next player is '{self.current_player.name}'")
    
    def get_game_state(self) -> Dict[str, Any]:
        """
        Get the current game state as a dictionary.
        
        Returns:
            Dictionary containing the current game state
        """
        return {
            "players": [
                {
                    "name": player.name,
                    "turn_score": player.turn_score,
                    "total_score": player.total_score
                }
                for player in self._players
            ],
            "current_player": self.current_player.name if self.current_player else None,
            "dice": [
                {
                    "value": die.value,
                    "kept": die.kept
                }
                for die in self._dice_set.dice
            ],
            "turn_started": self._turn_started,
            "game_over": self._game_over
        }
    
    def get_available_actions(self) -> List[str]:
        """
        Get a list of available actions for the current game state.
        
        Returns:
            List of available action names
        """
        actions = []
        
        if not self._players:
            actions.append("add_player")
            return actions
        
        if self._game_over:
            actions.append("new_game")
            return actions
        
        if not self._turn_started:
            actions.append("start_turn")
            return actions
        
        # During a turn
        if self._dice_set.available_dice and self._score_calculator.has_scoring_dice(self._dice_set.available_values):
            actions.append("keep_dice")
        
        if self._dice_set.kept_dice:
            actions.append("bank")
            actions.append("roll_again")
        
        return actions
