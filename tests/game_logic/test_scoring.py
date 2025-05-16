"""
Tests for the scoring module.
"""
import pytest
from unittest.mock import patch, MagicMock
from collections import Counter

from kcd_dice_game.game_logic.scoring import ScoreCalculator


class TestScoreCalculator:
    """Test cases for the ScoreCalculator class."""

    @pytest.fixture
    def score_calculator(self):
        """Create a ScoreCalculator with mocked config."""
        with patch('kcd_dice_game.utils.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            # Set up mock scoring rules
            mock_config.get.side_effect = lambda key, default=None: {
                "game_config.scoring_rules": {
                    "single_1": 100,
                    "single_5": 50,
                    "three_1": 1000,
                    "three_2": 200,
                    "three_3": 300,
                    "three_4": 400,
                    "three_5": 500,
                    "three_6": 600,
                    "straight": 1500,
                    "three_pairs": 1000
                },
                "game_config.multipliers": {
                    "four_of_kind": 2,
                    "five_of_kind": 3,
                    "six_of_kind": 4
                }
            }.get(key, default)
            
            calculator = ScoreCalculator()
            yield calculator

    def test_is_straight(self, score_calculator):
        """Test detecting a straight (1-6)."""
        # Valid straight
        assert score_calculator._is_straight(Counter([1, 2, 3, 4, 5, 6]))
        
        # Not a straight (duplicate value)
        assert not score_calculator._is_straight(Counter([1, 2, 3, 4, 5, 5]))
        
        # Not a straight (missing value)
        assert not score_calculator._is_straight(Counter([1, 2, 3, 4, 6]))
        
        # Not a straight (too many dice)
        assert not score_calculator._is_straight(Counter([1, 2, 3, 4, 5, 6, 6]))

    def test_is_three_pairs(self, score_calculator):
        """Test detecting three pairs."""
        # Valid three pairs
        assert score_calculator._is_three_pairs(Counter([1, 1, 2, 2, 3, 3]))
        assert score_calculator._is_three_pairs(Counter([2, 2, 4, 4, 6, 6]))
        
        # Not three pairs (one pair and four of a kind)
        assert not score_calculator._is_three_pairs(Counter([1, 1, 2, 2, 2, 2]))
        
        # Not three pairs (three of a kind)
        assert not score_calculator._is_three_pairs(Counter([1, 1, 1, 2, 2, 3]))
        
        # Not three pairs (all different)
        assert not score_calculator._is_three_pairs(Counter([1, 2, 3, 4, 5, 6]))
        
        # Not three pairs (too few dice)
        assert not score_calculator._is_three_pairs(Counter([1, 1, 2, 2]))

    def test_calculate_score_empty(self, score_calculator):
        """Test calculating score for empty dice list."""
        assert score_calculator.calculate_score([]) == 0

    def test_calculate_score_straight(self, score_calculator):
        """Test calculating score for a straight."""
        assert score_calculator.calculate_score([1, 2, 3, 4, 5, 6]) == 1500
        assert score_calculator.calculate_score([6, 5, 4, 3, 2, 1]) == 1500  # Order doesn't matter

    def test_calculate_score_three_pairs(self, score_calculator):
        """Test calculating score for three pairs."""
        assert score_calculator.calculate_score([1, 1, 2, 2, 3, 3]) == 1000
        assert score_calculator.calculate_score([4, 4, 5, 5, 6, 6]) == 1000

    def test_calculate_score_single_values(self, score_calculator):
        """Test calculating score for single 1s and 5s."""
        # Single 1
        assert score_calculator.calculate_score([1]) == 100
        
        # Single 5
        assert score_calculator.calculate_score([5]) == 50
        
        # Multiple single 1s and 5s
        assert score_calculator.calculate_score([1, 1, 5]) == 250  # 2*100 + 50
        assert score_calculator.calculate_score([1, 5, 5, 5]) == 250  # 100 + 3*50

    def test_calculate_score_three_of_a_kind(self, score_calculator):
        """Test calculating score for three of a kind."""
        # Three 1s
        assert score_calculator.calculate_score([1, 1, 1]) == 1000
        
        # Three 2s
        assert score_calculator.calculate_score([2, 2, 2]) == 200
        
        # Three 3s
        assert score_calculator.calculate_score([3, 3, 3]) == 300
        
        # Three 4s
        assert score_calculator.calculate_score([4, 4, 4]) == 400
        
        # Three 5s
        assert score_calculator.calculate_score([5, 5, 5]) == 500
        
        # Three 6s
        assert score_calculator.calculate_score([6, 6, 6]) == 600

    def test_calculate_score_four_of_a_kind(self, score_calculator):
        """Test calculating score for four of a kind."""
        # Four 1s (2x three of a kind score)
        assert score_calculator.calculate_score([1, 1, 1, 1]) == 2000  # 2 * 1000
        
        # Four 3s
        assert score_calculator.calculate_score([3, 3, 3, 3]) == 600  # 2 * 300
        
        # Four 5s
        assert score_calculator.calculate_score([5, 5, 5, 5]) == 1000  # 2 * 500

    def test_calculate_score_five_of_a_kind(self, score_calculator):
        """Test calculating score for five of a kind."""
        # Five 1s (3x three of a kind score)
        assert score_calculator.calculate_score([1, 1, 1, 1, 1]) == 3000  # 3 * 1000
        
        # Five 4s
        assert score_calculator.calculate_score([4, 4, 4, 4, 4]) == 1200  # 3 * 400

    def test_calculate_score_six_of_a_kind(self, score_calculator):
        """Test calculating score for six of a kind."""
        # Six 1s (4x three of a kind score)
        assert score_calculator.calculate_score([1, 1, 1, 1, 1, 1]) == 4000  # 4 * 1000
        
        # Six 6s
        assert score_calculator.calculate_score([6, 6, 6, 6, 6, 6]) == 2400  # 4 * 600

    def test_calculate_score_mixed(self, score_calculator):
        """Test calculating score for mixed combinations."""
        # Three 2s and two 1s
        assert score_calculator.calculate_score([2, 2, 2, 1, 1]) == 400  # 200 + 2*100
        
        # Three 5s and one 1
        assert score_calculator.calculate_score([5, 5, 5, 1]) == 600  # 500 + 100
        
        # Three 3s and three 5s (not three pairs, but two sets of three of a kind)
        assert score_calculator.calculate_score([3, 3, 3, 5, 5, 5]) == 800  # 300 + 500

    def test_calculate_score_non_scoring(self, score_calculator):
        """Test calculating score for non-scoring dice."""
        # Non-scoring dice (2, 3, 4, 6)
        assert score_calculator.calculate_score([2]) == 0
        assert score_calculator.calculate_score([3, 4]) == 0
        assert score_calculator.calculate_score([2, 3, 4, 6]) == 0
        
        # Mix of scoring and non-scoring
        assert score_calculator.calculate_score([1, 2, 3, 4]) == 100  # Only the 1 scores

    def test_has_scoring_dice(self, score_calculator):
        """Test checking if there are any scoring dice."""
        # Empty list
        assert not score_calculator.has_scoring_dice([])
        
        # Scoring dice
        assert score_calculator.has_scoring_dice([1])
        assert score_calculator.has_scoring_dice([5])
        assert score_calculator.has_scoring_dice([1, 2, 3, 4, 5, 6])  # Straight
        assert score_calculator.has_scoring_dice([2, 2, 2])  # Three of a kind
        assert score_calculator.has_scoring_dice([1, 1, 2, 2, 3, 3])  # Three pairs
        
        # Non-scoring dice
        assert not score_calculator.has_scoring_dice([2])
        assert not score_calculator.has_scoring_dice([3, 4, 6])
        assert not score_calculator.has_scoring_dice([2, 3, 4, 6, 6])

    def test_get_scorable_dice_indices(self, score_calculator):
        """Test getting indices of scorable dice."""
        # Empty list
        assert score_calculator.get_scorable_dice_indices([]) == set()
        
        # All dice are scorable (straight)
        assert score_calculator.get_scorable_dice_indices([1, 2, 3, 4, 5, 6]) == {0, 1, 2, 3, 4, 5}
        
        # All dice are scorable (three pairs)
        assert score_calculator.get_scorable_dice_indices([1, 1, 2, 2, 3, 3]) == {0, 1, 2, 3, 4, 5}
        
        # Some dice are scorable (1s and 5s)
        assert score_calculator.get_scorable_dice_indices([1, 2, 3, 5, 6]) == {0, 3}
        
        # Some dice are scorable (three of a kind)
        assert score_calculator.get_scorable_dice_indices([2, 2, 2, 3, 4]) == {0, 1, 2}
        
        # No dice are scorable
        assert score_calculator.get_scorable_dice_indices([2, 3, 4, 6]) == set()
