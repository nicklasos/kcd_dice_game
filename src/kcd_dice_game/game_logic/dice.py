"""
Dice module for the KCD dice game.
Contains classes for representing dice and sets of dice.
"""
import random
from typing import List, Optional

from kcd_dice_game.utils.logger import logger
from kcd_dice_game.utils.config import Config


class Dice:
    """
    Represents a single die with a value (1-6) and a state (kept or not kept).
    """
    def __init__(self, value: Optional[int] = None):
        """
        Initialize a die with an optional value.
        If no value is provided, the die will be rolled.
        
        Args:
            value: Optional initial value (1-6)
        
        Raises:
            ValueError: If the provided value is not between 1 and 6
        """
        self._kept = False
        if value is not None:
            if not 1 <= value <= 6:
                raise ValueError("Dice value must be between 1 and 6")
            self._value = value
        else:
            self._value = self.roll()
    
    @property
    def value(self) -> int:
        """Get the current value of the die."""
        return self._value
    
    @property
    def kept(self) -> bool:
        """Check if the die is currently kept."""
        return self._kept
    
    def keep(self) -> None:
        """Mark the die as kept."""
        self._kept = True
        logger.debug(f"Die with value {self._value} marked as kept")
    
    def release(self) -> None:
        """Mark the die as not kept."""
        self._kept = False
        logger.debug(f"Die with value {self._value} marked as not kept")
    
    def roll(self) -> int:
        """
        Roll the die to get a random value between 1 and 6.
        
        Returns:
            The new value of the die
        """
        self._value = random.randint(1, 6)
        logger.debug(f"Die rolled: {self._value}")
        return self._value
    
    def __repr__(self) -> str:
        """String representation of the die."""
        status = "kept" if self._kept else "available"
        return f"Dice({self._value}, {status})"


class DiceSet:
    """
    Represents a set of dice for the game.
    """
    def __init__(self, count: Optional[int] = None):
        """
        Initialize a set of dice.
        
        Args:
            count: Number of dice in the set (default: from config)
        """
        config = Config()
        self._dice_count = count or config.get("game_config.dice_count", 6)
        self._dice: List[Dice] = [Dice() for _ in range(self._dice_count)]
        logger.info(f"Created dice set with {self._dice_count} dice")
    
    @property
    def dice(self) -> List[Dice]:
        """Get all dice in the set."""
        return self._dice
    
    @property
    def kept_dice(self) -> List[Dice]:
        """Get all kept dice in the set."""
        return [die for die in self._dice if die.kept]
    
    @property
    def available_dice(self) -> List[Dice]:
        """Get all available (not kept) dice in the set."""
        return [die for die in self._dice if not die.kept]
    
    @property
    def values(self) -> List[int]:
        """Get the values of all dice in the set."""
        return [die.value for die in self._dice]
    
    @property
    def kept_values(self) -> List[int]:
        """Get the values of all kept dice in the set."""
        return [die.value for die in self._dice if die.kept]
    
    @property
    def available_values(self) -> List[int]:
        """Get the values of all available dice in the set."""
        return [die.value for die in self._dice if not die.kept]
    
    def roll_all(self) -> List[int]:
        """
        Roll all dice in the set.
        
        Returns:
            List of new dice values
        """
        for die in self._dice:
            die.roll()
            die.release()  # Reset kept status
        
        logger.info(f"Rolled all dice: {self.values}")
        return self.values
    
    def roll_available(self) -> List[int]:
        """
        Roll only the available (not kept) dice.
        
        Returns:
            List of new values for the available dice
        """
        available_dice = self.available_dice
        if not available_dice:
            logger.warning("Attempted to roll available dice, but all dice are kept")
            return []
        
        for die in available_dice:
            die.roll()
        
        logger.info(f"Rolled available dice: {self.available_values}")
        return self.available_values
    
    def keep_dice(self, indices: List[int]) -> None:
        """
        Mark specific dice as kept.
        
        Args:
            indices: List of indices of dice to keep
            
        Raises:
            IndexError: If an index is out of range
            ValueError: If a die is already kept
        """
        for idx in indices:
            if not 0 <= idx < len(self._dice):
                raise IndexError(f"Dice index {idx} out of range")
            
            die = self._dice[idx]
            if die.kept:
                raise ValueError(f"Die at index {idx} is already kept")
            
            die.keep()
        
        logger.info(f"Kept dice at indices {indices}")
    
    def keep_dice_with_value(self, value: int) -> List[int]:
        """
        Mark all available dice with a specific value as kept.
        
        Args:
            value: The value to keep
            
        Returns:
            List of indices of newly kept dice
        """
        kept_indices = []
        for idx, die in enumerate(self._dice):
            if not die.kept and die.value == value:
                die.keep()
                kept_indices.append(idx)
        
        if kept_indices:
            logger.info(f"Kept dice with value {value} at indices {kept_indices}")
        else:
            logger.warning(f"No available dice with value {value} to keep")
        
        return kept_indices
    
    def release_all(self) -> None:
        """Release all dice (mark as not kept)."""
        for die in self._dice:
            die.release()
        logger.info("Released all dice")
    
    def is_all_kept(self) -> bool:
        """
        Check if all dice are kept.
        
        Returns:
            True if all dice are kept, False otherwise
        """
        return all(die.kept for die in self._dice)
    
    def reset(self) -> None:
        """Reset the dice set to initial state (all dice rolled and not kept)."""
        self.roll_all()
        logger.info("Reset dice set")
    
    def __repr__(self) -> str:
        """String representation of the dice set."""
        dice_str = ", ".join(str(die) for die in self._dice)
        return f"DiceSet([{dice_str}])"
