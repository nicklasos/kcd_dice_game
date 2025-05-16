"""
Tests for the player module.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.game_logic.player import Player


class TestPlayer:
    """Test cases for the Player class."""

    @pytest.fixture
    def player(self):
        """Create a Player with mocked config."""
        with patch('src.utils.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock max score
            mock_config.get.return_value = 5000
            
            player = Player("TestPlayer")
            yield player

    def test_init(self, player):
        """Test initializing a player."""
        assert player.name == "TestPlayer"
        assert player.total_score == 0
        assert player.turn_score == 0

    def test_add_to_turn(self, player):
        """Test adding points to the current turn."""
        # Add points to turn
        turn_score = player.add_to_turn(100)
        assert turn_score == 100
        assert player.turn_score == 100
        
        # Add more points
        turn_score = player.add_to_turn(50)
        assert turn_score == 150
        assert player.turn_score == 150
        
        # Total score should not change
        assert player.total_score == 0

    def test_add_to_turn_negative(self, player):
        """Test adding negative points raises ValueError."""
        with pytest.raises(ValueError):
            player.add_to_turn(-50)

    def test_bank_points(self, player):
        """Test banking points from turn to total score."""
        # Add points to turn
        player.add_to_turn(200)
        
        # Bank points
        total_score = player.bank_points()
        assert total_score == 200
        assert player.total_score == 200
        
        # Turn score should be reset
        assert player.turn_score == 0
        
        # Add more points and bank again
        player.add_to_turn(300)
        total_score = player.bank_points()
        assert total_score == 500
        assert player.total_score == 500
        assert player.turn_score == 0

    def test_reset_turn(self, player):
        """Test resetting the turn score."""
        # Add points to turn
        player.add_to_turn(150)
        assert player.turn_score == 150
        
        # Reset turn
        player.reset_turn()
        assert player.turn_score == 0
        
        # Total score should not change
        assert player.total_score == 0

    def test_has_won_not_reached(self, player):
        """Test has_won when max score is not reached."""
        # Add points but not enough to win
        player.add_to_turn(2000)
        player.bank_points()
        
        assert not player.has_won()

    def test_has_won_reached(self, player):
        """Test has_won when max score is reached."""
        # Add enough points to win
        player.add_to_turn(5000)
        player.bank_points()
        
        assert player.has_won()

    def test_has_won_exceeded(self, player):
        """Test has_won when max score is exceeded."""
        # Add more points than needed to win
        player.add_to_turn(6000)
        player.bank_points()
        
        assert player.has_won()

    def test_repr(self, player):
        """Test string representation of a player."""
        player.add_to_turn(300)
        player.bank_points()
        player.add_to_turn(150)
        
        repr_str = repr(player)
        assert "TestPlayer" in repr_str
        assert "turn: 150" in repr_str
        assert "total: 300" in repr_str
