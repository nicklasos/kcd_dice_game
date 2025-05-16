"""
Tests for the dice module.
"""

import pytest
from unittest.mock import patch

from kcd_dice_game.game_logic.dice import Dice, DiceSet


class TestDice:
    """Test cases for the Dice class."""

    def test_init_with_value(self):
        """Test initializing a die with a specific value."""
        die = Dice(3)
        assert die.value == 3
        assert not die.kept

    def test_init_with_invalid_value(self):
        """Test initializing a die with an invalid value raises ValueError."""
        with pytest.raises(ValueError):
            Dice(0)
        with pytest.raises(ValueError):
            Dice(7)

    @patch("random.randint", return_value=4)
    def test_init_without_value(self, mock_randint):
        """Test initializing a die without a value rolls it."""
        die = Dice()
        assert die.value == 4
        assert not die.kept
        mock_randint.assert_called_once_with(1, 6)

    def test_keep_and_release(self):
        """Test keeping and releasing a die."""
        die = Dice(5)

        # Initially not kept
        assert not die.kept

        # Keep the die
        die.keep()
        assert die.kept

        # Release the die
        die.release()
        assert not die.kept

    @patch("random.randint", return_value=2)
    def test_roll(self, mock_randint):
        """Test rolling a die."""
        die = Dice(5)
        assert die.value == 5

        # Roll the die
        new_value = die.roll()
        assert new_value == 2
        assert die.value == 2
        mock_randint.assert_called_once_with(1, 6)

    def test_repr(self):
        """Test string representation of a die."""
        die = Dice(6)
        assert "Dice(6, available)" in repr(die)

        die.keep()
        assert "Dice(6, kept)" in repr(die)


class TestDiceSet:
    """Test cases for the DiceSet class."""

    @patch("kcd_dice_game.utils.config.Config.get", return_value=6)
    def test_init_default_count(self, mock_get):
        """Test initializing a dice set with default count from config."""
        dice_set = DiceSet()
        assert len(dice_set.dice) == 6
        mock_get.assert_called_once_with("game_config.dice_count", 6)

    def test_init_custom_count(self):
        """Test initializing a dice set with a custom count."""
        dice_set = DiceSet(4)
        assert len(dice_set.dice) == 4

    def test_dice_properties(self):
        """Test the dice properties (dice, kept_dice, available_dice)."""
        dice_set = DiceSet(3)

        # Initially all dice are available
        assert len(dice_set.dice) == 3
        assert len(dice_set.kept_dice) == 0
        assert len(dice_set.available_dice) == 3

        # Keep one die
        dice_set.dice[0].keep()
        assert len(dice_set.kept_dice) == 1
        assert len(dice_set.available_dice) == 2

        # Keep another die
        dice_set.dice[1].keep()
        assert len(dice_set.kept_dice) == 2
        assert len(dice_set.available_dice) == 1

    def test_values_properties(self):
        """Test the values properties (values, kept_values, available_values)."""
        with patch("random.randint", side_effect=[1, 2, 3]):
            dice_set = DiceSet(3)

        # Check initial values
        assert dice_set.values == [1, 2, 3]
        assert dice_set.kept_values == []
        assert dice_set.available_values == [1, 2, 3]

        # Keep first die
        dice_set.dice[0].keep()
        assert dice_set.kept_values == [1]
        assert dice_set.available_values == [2, 3]

        # Keep second die
        dice_set.dice[1].keep()
        assert dice_set.kept_values == [1, 2]
        assert dice_set.available_values == [3]

    @patch("random.randint", side_effect=[4, 5, 6])
    def test_roll_all(self, mock_randint):
        """Test rolling all dice."""
        with patch("random.randint", side_effect=[1, 2, 3]):
            dice_set = DiceSet(3)

        # Keep a die
        dice_set.dice[0].keep()

        # Roll all dice
        new_values = dice_set.roll_all()
        assert new_values == [4, 5, 6]
        assert dice_set.values == [4, 5, 6]

        # All dice should be released after rolling all
        assert len(dice_set.kept_dice) == 0
        assert len(dice_set.available_dice) == 3

    @patch("random.randint", side_effect=[5, 6])
    def test_roll_available(self, mock_randint):
        """Test rolling only available dice."""
        with patch("random.randint", side_effect=[1, 2, 3]):
            dice_set = DiceSet(3)

        # Keep first die
        dice_set.dice[0].keep()

        # Roll available dice
        new_values = dice_set.roll_available()
        assert new_values == [5, 6]
        assert dice_set.values == [1, 5, 6]

        # First die should still be kept
        assert dice_set.kept_values == [1]
        assert dice_set.available_values == [5, 6]

    def test_roll_available_all_kept(self):
        """Test rolling available dice when all dice are kept."""
        dice_set = DiceSet(2)

        # Keep all dice
        for die in dice_set.dice:
            die.keep()

        # Try to roll available dice
        new_values = dice_set.roll_available()
        assert new_values == []

    def test_keep_dice(self):
        """Test keeping specific dice by indices."""
        dice_set = DiceSet(4)

        # Keep dice at indices 1 and 3
        dice_set.keep_dice([1, 3])

        # Check which dice are kept
        assert not dice_set.dice[0].kept
        assert dice_set.dice[1].kept
        assert not dice_set.dice[2].kept
        assert dice_set.dice[3].kept

    def test_keep_dice_invalid_index(self):
        """Test keeping dice with invalid index raises IndexError."""
        dice_set = DiceSet(3)

        with pytest.raises(IndexError):
            dice_set.keep_dice([3])  # Index out of range

    def test_keep_dice_already_kept(self):
        """Test keeping dice that are already kept raises ValueError."""
        dice_set = DiceSet(3)

        # Keep a die
        dice_set.keep_dice([0])

        # Try to keep it again
        with pytest.raises(ValueError):
            dice_set.keep_dice([0])

    @patch("random.randint", side_effect=[1, 2, 3, 1, 5])
    def test_keep_dice_with_value(self, mock_randint):
        """Test keeping all dice with a specific value."""
        dice_set = DiceSet(5)

        # Keep all dice with value 1
        kept_indices = dice_set.keep_dice_with_value(1)

        # Should have kept indices 0 and 3
        assert kept_indices == [0, 3]
        assert dice_set.dice[0].kept
        assert not dice_set.dice[1].kept
        assert not dice_set.dice[2].kept
        assert dice_set.dice[3].kept
        assert not dice_set.dice[4].kept

    def test_release_all(self):
        """Test releasing all dice."""
        dice_set = DiceSet(3)

        # Keep all dice
        for die in dice_set.dice:
            die.keep()

        # Release all dice
        dice_set.release_all()

        # Check that all dice are released
        assert len(dice_set.kept_dice) == 0
        assert len(dice_set.available_dice) == 3

    def test_is_all_kept(self):
        """Test checking if all dice are kept."""
        dice_set = DiceSet(3)

        # Initially no dice are kept
        assert not dice_set.is_all_kept()

        # Keep one die
        dice_set.dice[0].keep()
        assert not dice_set.is_all_kept()

        # Keep all dice
        for die in dice_set.dice:
            if not die.kept:
                die.keep()

        assert dice_set.is_all_kept()

    @patch("random.randint", side_effect=[4, 5, 6])
    def test_reset(self, mock_randint):
        """Test resetting the dice set."""
        with patch("random.randint", side_effect=[1, 2, 3]):
            dice_set = DiceSet(3)

        # Keep all dice
        for die in dice_set.dice:
            die.keep()

        # Reset the dice set
        dice_set.reset()

        # All dice should be rolled and released
        assert dice_set.values == [4, 5, 6]
        assert len(dice_set.kept_dice) == 0
        assert len(dice_set.available_dice) == 3
