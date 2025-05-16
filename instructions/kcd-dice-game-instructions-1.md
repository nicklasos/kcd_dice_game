# Kingdom Come: Deliverance Dice Game - Game Logic Module

## Overview

This document provides instructions for implementing the game logic module of the Kingdom Come: Deliverance dice game assistant. This module will handle all game rules, scoring, player management, and state tracking, independent of the visual interface.

! Important tip: use src/utils/config.py to load and save game configuration.

## Project Setup

- [x] Initialize project with Poetry
```bash
poetry init --name kcd_dice_game --description "KCD dice game assistant" --author "Your Name" --python "^3.10"
poetry add pytest pytest-cov loguru pydantic
```

- [x] Create the project structure:
```
kcd_dice_game/
├── config/
│   └── game_config.json     # Game configuration file
├── src/
│   ├── game_logic/
│   │   ├── __init__.py
│   │   ├── dice.py          # Dice representation
│   │   ├── player.py        # Player class
│   │   ├── scoring.py       # Scoring rules
│   │   ├── game.py          # Main game class
│   │   └── exceptions.py    # Custom exceptions
│   └── utils/
│       └── logger.py        # Logging utility
├── tests/
│   └── game_logic/
│       ├── test_dice.py
│       ├── test_player.py
│       ├── test_scoring.py
│       └── test_game.py
├── .gitignore
├── LICENSE
├── Makefile
├── pytest.ini
└── README.md
```

## Implementation Tasks

### 1. Game Configuration

- [x] Create a `game_config.json` file with the following structure:
```json
{
    "max_score": 5000,
    "scoring_rules": {
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
    "multipliers": {
        "four_of_kind": 2,
        "five_of_kind": 3,
        "six_of_kind": 4
    },
    "dice_count": 6
}
```

- [x] Implement a config loader that uses Pydantic models to validate and load this configuration

### 2. Logger Setup

- [x] Create a logging utility that:
  - Uses loguru for structured logging
  - Logs to console for DEBUG and above
  - Logs to file for INFO and above
  - Includes timestamps and log levels
  - Can be imported and used by other modules

### 3. Dice Module (TDD Approach)

- [x] Write tests for a `Dice` class that:
  - Represents a single die with a value (1-6)
  - Has a state (kept or not kept)
  - Can be rolled to get a random value
  - Validates that values are within allowed range

- [x] Write tests for a `DiceSet` class that:
  - Contains a collection of Dice objects
  - Can roll all dice or only non-kept dice
  - Can track which dice are kept vs. available
  - Can reset all dice to initial state
  - Can report if all dice are kept (full clear condition)

- [x] Implement the `Dice` and `DiceSet` classes according to tests

### 4. Scoring Module (TDD Approach)

- [x] Write tests for a `ScoreCalculator` class that:
  - Calculates scores based on the game's rules:
    - Single 1s = 100 points each
    - Single 5s = 50 points each
    - Three of a kind:
      - Three 1s = 1000 points
      - Three 2s = 200 points
      - Three 3s = 300 points
      - Three 4s = 400 points
      - Three 5s = 500 points
      - Three 6s = 600 points
    - Four of a kind = 2x three of a kind score
    - Five of a kind = 3x three of a kind score
    - Six of a kind = 4x three of a kind score
    - Straight (1-6) = 1500 points
    - Three pairs = 1000 points
  - Can detect if a roll has any scoring dice
  - Can identify all possible scoring combinations from a roll

- [x] Implement the `ScoreCalculator` class according to tests

### 5. Player Module (TDD Approach)

- [x] Write tests for a `Player` class that:
  - Stores player name
  - Tracks current turn score
  - Tracks total game score
  - Has methods to:
    - Add points to current turn
    - Bank current turn score (add to total)
    - Reset current turn score (on bust)
    - Check if player has won (reached max_score)

- [x] Implement the `Player` class according to tests

### 6. Game State Module (TDD Approach)

- [x] Write tests for a `Game` class that:
  - Manages the overall game state
  - Tracks multiple players and current player
  - Contains a DiceSet for gameplay
  - Handles turn logic:
    - Starting a turn (rolling all dice)
    - Keeping scoring dice
    - Rolling remaining dice
    - Checking for "bust" condition (no scoring dice)
    - Checking for "full clear" condition (all dice scored)
    - Banking points and ending turn
    - Transitioning to next player
  - Uses custom exceptions for invalid moves
  - Determines when game is over

- [x] Implement the `Game` class according to tests

### 7. Exception Handling

- [x] Create custom exceptions for the game:
  - `InvalidMoveException` - For illegal player actions
  - `GameRuleException` - For violations of game rules
  - `GameStateException` - For invalid state transitions

- [x] Use these exceptions consistently throughout the codebase
- [x] Ensure tests verify exception handling

### 8. Command Line Interface (Optional)

- [x] Create a simple CLI for testing game logic
- [x] Allow for:
  - Adding players
  - Simulating dice rolls
  - Selecting which dice to keep
  - Displaying score
  - Navigating through game turns

## Testing Requirements

- [x] Use pytest for all tests
- [x] Aim for at least 90% code coverage
- [x] Include edge cases in tests:
  - Perfect rolls (all scoring)
  - Bust scenarios (no scoring dice)
  - Complex scoring combinations
  - Game win conditions
  - Invalid moves/states

## Completion Criteria

The Game Logic module is complete when:

1. All tests pass with >90% coverage
2. Game configuration can be loaded from file
3. Dice can be rolled and kept
4. Scoring calculations are accurate for all combinations
5. Game state correctly manages turns, scoring, and win conditions
6. The module uses proper logging throughout
7. Code follows PEP 8 style guidelines
