"""
Player module for the KCD dice game.
Contains the Player class for managing player state during the game.
"""
from utils.logger import logger
from utils.config import Config


class Player:
    """
    Represents a player in the KCD dice game.
    Tracks player name, current turn score, and total game score.
    """
    def __init__(self, name: str):
        """
        Initialize a player with the given name.
        
        Args:
            name: Player's name
        """
        self._name = name
        self._total_score = 0
        self._turn_score = 0
        
        # Load max score from config
        config = Config()
        self._max_score = config.get("game_config.max_score", 5000)
        
        logger.info(f"Created player '{name}' with max score {self._max_score}")
    
    @property
    def name(self) -> str:
        """Get the player's name."""
        return self._name
    
    @property
    def total_score(self) -> int:
        """Get the player's total score."""
        return self._total_score
    
    @property
    def turn_score(self) -> int:
        """Get the player's current turn score."""
        return self._turn_score
    
    def add_to_turn(self, points: int) -> int:
        """
        Add points to the current turn score.
        
        Args:
            points: Number of points to add
            
        Returns:
            New turn score
            
        Raises:
            ValueError: If points is negative
        """
        if points < 0:
            raise ValueError("Cannot add negative points")
        
        self._turn_score += points
        logger.info(f"Player '{self._name}' added {points} points to turn (now {self._turn_score})")
        return self._turn_score
    
    def bank_points(self) -> int:
        """
        Bank the current turn score by adding it to the total score.
        
        Returns:
            New total score
        """
        self._total_score += self._turn_score
        logger.info(f"Player '{self._name}' banked {self._turn_score} points (total now {self._total_score})")
        self._turn_score = 0
        return self._total_score
    
    def reset_turn(self) -> None:
        """Reset the current turn score to 0 (on bust)."""
        previous_score = self._turn_score
        self._turn_score = 0
        logger.info(f"Player '{self._name}' lost {previous_score} points (turn reset)")
    
    def has_won(self) -> bool:
        """
        Check if the player has won by reaching or exceeding the max score.
        
        Returns:
            True if the player has won, False otherwise
        """
        has_won = self._total_score >= self._max_score
        if has_won:
            logger.info(f"Player '{self._name}' has won with {self._total_score} points!")
        return has_won
    
    def __repr__(self) -> str:
        """String representation of the player."""
        return f"Player('{self._name}', turn: {self._turn_score}, total: {self._total_score})"
