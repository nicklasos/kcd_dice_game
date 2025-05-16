"""
Tests for the game module.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.game_logic.game import Game
from src.game_logic.exceptions import InvalidMoveException, GameRuleException, GameStateException


class TestGame:
    """Test cases for the Game class."""

    @pytest.fixture
    def game(self):
        """Create a Game instance with mocked dependencies."""
        with patch('src.game_logic.game.DiceSet') as mock_dice_set_class, \
             patch('src.game_logic.game.ScoreCalculator') as mock_score_calc_class:
            
            # Mock DiceSet
            mock_dice_set = MagicMock()
            mock_dice_set_class.return_value = mock_dice_set
            
            # Mock ScoreCalculator
            mock_score_calc = MagicMock()
            mock_score_calc_class.return_value = mock_score_calc
            
            game = Game()
            
            # Set up the mocks on the game instance
            game._dice_set = mock_dice_set
            game._score_calculator = mock_score_calc
            
            yield game, mock_dice_set, mock_score_calc

    def test_init(self, game):
        """Test initializing a game."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        assert game_instance._players == []
        assert game_instance._current_player_idx == 0
        assert not game_instance._turn_started
        assert not game_instance._game_over
        assert game_instance._dice_set is mock_dice_set
        assert game_instance._score_calculator is mock_score_calc

    def test_add_player(self, game):
        """Test adding a player to the game."""
        game_instance, _, _ = game
        
        # Add a player
        player = game_instance.add_player("Player1")
        assert player.name == "Player1"
        assert len(game_instance.players) == 1
        assert game_instance.current_player.name == "Player1"
        
        # Add another player
        player2 = game_instance.add_player("Player2")
        assert player2.name == "Player2"
        assert len(game_instance.players) == 2
        assert game_instance.current_player.name == "Player1"  # Still the first player

    def test_add_player_duplicate_name(self, game):
        """Test adding a player with a duplicate name raises ValueError."""
        game_instance, _, _ = game
        
        game_instance.add_player("Player1")
        
        with pytest.raises(ValueError):
            game_instance.add_player("Player1")

    def test_add_player_after_start(self, game):
        """Test adding a player after the game has started raises GameStateException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start the game
        game_instance.add_player("Player1")
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Try to add another player
        with pytest.raises(GameStateException):
            game_instance.add_player("Player2")

    def test_start_turn(self, game):
        """Test starting a turn."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player
        game_instance.add_player("Player1")
        
        # Mock dice roll
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        
        # Start turn
        dice_values = game_instance.start_turn()
        
        assert dice_values == [1, 2, 3, 4, 5, 6]
        assert game_instance._turn_started
        mock_dice_set.roll_all.assert_called_once()
        mock_score_calc.has_scoring_dice.assert_called_once_with([1, 2, 3, 4, 5, 6])

    def test_start_turn_no_players(self, game):
        """Test starting a turn with no players raises GameStateException."""
        game_instance, _, _ = game
        
        with pytest.raises(GameStateException):
            game_instance.start_turn()

    def test_start_turn_already_started(self, game):
        """Test starting a turn when one is already in progress raises GameRuleException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Try to start another turn
        with pytest.raises(GameRuleException):
            game_instance.start_turn()

    def test_start_turn_bust(self, game):
        """Test starting a turn with no scoring dice (bust)."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player
        game_instance.add_player("Player1")
        
        # Mock dice roll with no scoring dice
        mock_dice_set.roll_all.return_value = [2, 3, 4, 6, 6, 6]
        mock_score_calc.has_scoring_dice.return_value = False
        
        # Start turn (should bust)
        dice_values = game_instance.start_turn()
        
        assert dice_values == [2, 3, 4, 6, 6, 6]
        assert not game_instance._turn_started  # Turn should end on bust

    def test_keep_dice(self, game):
        """Test keeping dice and calculating score."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        player = game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice
        mock_dice = [MagicMock() for _ in range(6)]
        for i, die in enumerate(mock_dice):
            die.value = i + 1
            die.kept = False
        mock_dice_set.dice = mock_dice
        mock_dice_set.available_values = [1, 2, 3, 4, 5, 6]
        
        # Set up scoring
        mock_score_calc.get_scorable_dice_indices.return_value = {0, 4}  # Indices of scorable dice (1 and 5)
        mock_score_calc.calculate_score.return_value = 150  # 100 for 1, 50 for 5
        
        # Keep dice
        score = game_instance.keep_dice([0, 4])  # Keep 1 and 5
        
        assert score == 150
        mock_dice_set.keep_dice.assert_called_once_with([0, 4])
        mock_score_calc.calculate_score.assert_called_once_with([1, 5])
        assert player.turn_score == 150

    def test_keep_dice_turn_not_started(self, game):
        """Test keeping dice when turn hasn't started raises GameStateException."""
        game_instance, _, _ = game
        
        # Add a player but don't start a turn
        game_instance.add_player("Player1")
        
        with pytest.raises(GameStateException):
            game_instance.keep_dice([0, 1])

    def test_keep_dice_invalid_indices(self, game):
        """Test keeping dice with invalid indices raises InvalidMoveException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with an invalid index
        mock_dice_set.dice = [MagicMock() for _ in range(6)]
        mock_dice_set.__getitem__.side_effect = IndexError
        
        with pytest.raises(InvalidMoveException):
            game_instance.keep_dice([10])  # Invalid index

    def test_keep_dice_already_kept(self, game):
        """Test keeping dice that are already kept raises InvalidMoveException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with one already kept
        mock_dice = [MagicMock() for _ in range(6)]
        mock_dice[0].kept = True  # First die is already kept
        mock_dice_set.dice = mock_dice
        
        with pytest.raises(InvalidMoveException):
            game_instance.keep_dice([0])  # Try to keep an already kept die

    def test_keep_dice_non_scoring(self, game):
        """Test keeping non-scoring dice raises InvalidMoveException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice
        mock_dice = [MagicMock() for _ in range(6)]
        for i, die in enumerate(mock_dice):
            die.value = i + 1
            die.kept = False
        mock_dice_set.dice = mock_dice
        mock_dice_set.available_values = [1, 2, 3, 4, 5, 6]
        
        # Set up scoring - only indices 0 and 4 are scorable
        mock_score_calc.get_scorable_dice_indices.return_value = {0, 4}
        
        # Try to keep non-scoring dice
        with pytest.raises(InvalidMoveException):
            game_instance.keep_dice([1, 2])  # Try to keep non-scoring dice (2 and 3)

    def test_keep_dice_full_clear(self, game):
        """Test keeping all dice (full clear)."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        player = game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice
        mock_dice = [MagicMock() for _ in range(6)]
        for i, die in enumerate(mock_dice):
            die.value = i + 1
            die.kept = False
        mock_dice_set.dice = mock_dice
        mock_dice_set.available_values = [1, 2, 3, 4, 5, 6]
        
        # Set up scoring - all dice are scorable (straight)
        mock_score_calc.get_scorable_dice_indices.return_value = {0, 1, 2, 3, 4, 5}
        mock_score_calc.calculate_score.return_value = 1500  # Straight
        
        # Set up full clear check
        mock_dice_set.is_all_kept.return_value = True
        
        # Keep all dice
        score = game_instance.keep_dice([0, 1, 2, 3, 4, 5])
        
        assert score == 1500
        mock_dice_set.keep_dice.assert_called_once_with([0, 1, 2, 3, 4, 5])
        mock_dice_set.is_all_kept.assert_called_once()
        mock_dice_set.release_all.assert_called_once()  # Should release all dice on full clear
        assert player.turn_score == 1500

    def test_roll_again(self, game):
        """Test rolling available dice again."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice for rolling again
        mock_dice_set.available_dice = [MagicMock() for _ in range(4)]  # 4 available dice
        mock_dice_set.roll_available.return_value = [2, 3, 4, 6]
        mock_dice_set.available_values = [2, 3, 4, 6]
        
        # Roll again
        dice_values = game_instance.roll_again()
        
        assert dice_values == [2, 3, 4, 6]
        mock_dice_set.roll_available.assert_called_once()
        mock_score_calc.has_scoring_dice.assert_called_with([2, 3, 4, 6])

    def test_roll_again_turn_not_started(self, game):
        """Test rolling again when turn hasn't started raises GameStateException."""
        game_instance, _, _ = game
        
        # Add a player but don't start a turn
        game_instance.add_player("Player1")
        
        with pytest.raises(GameStateException):
            game_instance.roll_again()

    def test_roll_again_no_available_dice(self, game):
        """Test rolling again with no available dice (all kept)."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with all kept
        mock_dice_set.available_dice = []
        mock_dice_set.dice = [MagicMock() for _ in range(6)]
        mock_dice_set.roll_available.return_value = [1, 2, 3, 4, 5, 6]  # After releasing all
        mock_dice_set.available_values = [1, 2, 3, 4, 5, 6]
        
        # Roll again - should release all dice first
        dice_values = game_instance.roll_again()
        
        mock_dice_set.release_all.assert_called_once()
        mock_dice_set.roll_available.assert_called_once()
        assert dice_values == [1, 2, 3, 4, 5, 6]

    def test_roll_again_bust(self, game):
        """Test rolling again with no scoring dice (bust)."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        player = game_instance.add_player("Player1")
        player.add_to_turn(100)  # Add some points to lose on bust
        
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice for rolling again with no scoring dice
        mock_dice_set.available_dice = [MagicMock() for _ in range(4)]
        mock_dice_set.roll_available.return_value = [2, 3, 4, 6]
        mock_dice_set.available_values = [2, 3, 4, 6]
        mock_score_calc.has_scoring_dice.return_value = False  # No scoring dice
        
        # Roll again (should bust)
        dice_values = game_instance.roll_again()
        
        assert dice_values == [2, 3, 4, 6]
        assert not game_instance._turn_started  # Turn should end on bust
        assert player.turn_score == 0  # Turn score should be reset

    def test_bank(self, game):
        """Test banking points and ending turn."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        player = game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with some kept
        mock_dice = [MagicMock() for _ in range(6)]
        mock_dice[0].kept = True
        mock_dice[4].kept = True
        mock_dice_set.dice = mock_dice
        mock_dice_set.kept_dice = [mock_dice[0], mock_dice[4]]
        
        # Add points to the player's turn
        player.add_to_turn(150)
        
        # Bank points
        total_score = game_instance.bank()
        
        assert total_score == 150
        assert player.total_score == 150
        assert player.turn_score == 0
        assert not game_instance._turn_started  # Turn should end
        mock_dice_set.release_all.assert_called_once()  # Should release all dice

    def test_bank_turn_not_started(self, game):
        """Test banking when turn hasn't started raises GameStateException."""
        game_instance, _, _ = game
        
        # Add a player but don't start a turn
        game_instance.add_player("Player1")
        
        with pytest.raises(GameStateException):
            game_instance.bank()

    def test_bank_no_kept_dice(self, game):
        """Test banking with no kept dice raises GameRuleException."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with none kept
        mock_dice_set.kept_dice = []
        
        # Try to bank
        with pytest.raises(GameRuleException):
            game_instance.bank()

    def test_bank_win(self, game):
        """Test banking points and winning the game."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        player = game_instance.add_player("Player1")
        mock_dice_set.roll_all.return_value = [1, 2, 3, 4, 5, 6]
        mock_score_calc.has_scoring_dice.return_value = True
        game_instance.start_turn()
        
        # Set up mock dice with some kept
        mock_dice = [MagicMock() for _ in range(6)]
        mock_dice[0].kept = True
        mock_dice_set.dice = mock_dice
        mock_dice_set.kept_dice = [mock_dice[0]]
        
        # Add enough points to win
        player.add_to_turn(5000)
        
        # Mock has_won to return True
        with patch.object(player, 'has_won', return_value=True):
            # Bank points
            total_score = game_instance.bank()
            
            assert total_score == 5000
            assert game_instance._game_over  # Game should be over

    def test_bust(self, game):
        """Test busting (losing turn score)."""
        game_instance, mock_dice_set, _ = game
        
        # Add a player and add some points
        player = game_instance.add_player("Player1")
        player.add_to_turn(300)
        
        # Start turn flag
        game_instance._turn_started = True
        
        # Bust
        game_instance.bust()
        
        assert player.turn_score == 0  # Turn score should be reset
        assert not game_instance._turn_started  # Turn should end
        mock_dice_set.release_all.assert_called_once()  # Should release all dice

    def test_end_turn(self, game):
        """Test ending a turn and moving to the next player."""
        game_instance, mock_dice_set, _ = game
        
        # Add two players
        game_instance.add_player("Player1")
        game_instance.add_player("Player2")
        
        # Start turn flag
        game_instance._turn_started = True
        
        # End turn
        game_instance._end_turn()
        
        assert not game_instance._turn_started  # Turn should end
        assert game_instance._current_player_idx == 1  # Should move to second player
        mock_dice_set.release_all.assert_called_once()  # Should release all dice
        
        # End turn again
        game_instance._turn_started = True
        game_instance._end_turn()
        
        assert game_instance._current_player_idx == 0  # Should wrap around to first player

    def test_get_game_state(self, game):
        """Test getting the current game state."""
        game_instance, mock_dice_set, _ = game
        
        # Add a player
        player = game_instance.add_player("Player1")
        player.add_to_turn(200)
        
        # Set up mock dice
        mock_dice = [MagicMock() for _ in range(6)]
        for i, die in enumerate(mock_dice):
            die.value = i + 1
            die.kept = i < 2  # First two dice are kept
        mock_dice_set.dice = mock_dice
        
        # Start turn
        game_instance._turn_started = True
        
        # Get game state
        state = game_instance.get_game_state()
        
        assert len(state["players"]) == 1
        assert state["players"][0]["name"] == "Player1"
        assert state["players"][0]["turn_score"] == 200
        assert state["current_player"] == "Player1"
        assert len(state["dice"]) == 6
        assert state["dice"][0]["value"] == 1
        assert state["dice"][0]["kept"] is True
        assert state["dice"][2]["value"] == 3
        assert state["dice"][2]["kept"] is False
        assert state["turn_started"] is True
        assert state["game_over"] is False

    def test_get_available_actions_no_players(self, game):
        """Test getting available actions with no players."""
        game_instance, _, _ = game
        
        actions = game_instance.get_available_actions()
        assert actions == ["add_player"]

    def test_get_available_actions_game_over(self, game):
        """Test getting available actions when game is over."""
        game_instance, _, _ = game
        
        # Add a player
        game_instance.add_player("Player1")
        
        # End the game
        game_instance._game_over = True
        
        actions = game_instance.get_available_actions()
        assert actions == ["new_game"]

    def test_get_available_actions_turn_not_started(self, game):
        """Test getting available actions when turn hasn't started."""
        game_instance, _, _ = game
        
        # Add a player
        game_instance.add_player("Player1")
        
        actions = game_instance.get_available_actions()
        assert actions == ["start_turn"]

    def test_get_available_actions_during_turn(self, game):
        """Test getting available actions during a turn."""
        game_instance, mock_dice_set, mock_score_calc = game
        
        # Add a player and start a turn
        game_instance.add_player("Player1")
        game_instance._turn_started = True
        
        # Set up mock dice with none kept and some scoring dice
        mock_dice_set.available_dice = [MagicMock() for _ in range(6)]
        mock_dice_set.kept_dice = []
        mock_score_calc.has_scoring_dice.return_value = True
        
        # Get available actions
        actions = game_instance.get_available_actions()
        assert actions == ["keep_dice"]
        
        # Set up mock dice with some kept
        mock_dice_set.kept_dice = [MagicMock()]
        
        # Get available actions
        actions = game_instance.get_available_actions()
        assert set(actions) == {"bank", "roll_again", "keep_dice"}
