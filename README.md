# Texas Hold'em Monte Carlo Tree Search Win Probability Estimator

This project implements a Monte Carlo Tree Search (MCTS) algorithm with UCB1 selection strategy to estimate win probabilities for Texas Hold'em poker hands based on pre-flop hole cards.

## Overview

The estimator uses MCTS to build a search tree where each node represents a partially revealed poker world (opponent cards, flop, turn, river). The UCB1 algorithm guides exploration toward more promising branches over time.

## Features

- **Complete MCTS Implementation**: Selection, Expansion, Simulation, and Backpropagation
- **UCB1 Selection Strategy**: Balances exploration vs exploitation with configurable constant
- **Efficient Card Representation**: Uses enums for ranks and suits with proper hashing
- **Complete Hand Evaluation**: Implements all Texas Hold'em hand rankings including tiebreakers
- **Ground Truth Comparison**: Includes comprehensive pre-flop odds table for validation
- **Configurable Parameters**: Adjustable iteration count and exploration constant

## Architecture

### Tree Structure
- **Root**: Player's two known hole cards
- **Level 1**: 1000 sampled opponent hole card combinations
- **Level 2**: 1000 sampled flops (3 cards)
- **Level 3**: 1000 sampled turn cards (1 card)  
- **Level 4**: 1000 sampled river cards (1 card) with full hand evaluation

### Key Components

1. **Card System**: `Card`, `Rank`, `Suit` classes with proper equality and hashing
2. **Deck Management**: `Deck` class that tracks excluded cards and supports drawing
3. **Hand Evaluation**: `HandEvaluator` with complete Texas Hold'em ranking logic
4. **Game State**: `GameState` tracks game progression and known cards
5. **MCTS Tree**: `MCTSNode` with UCB1 selection and visit/win statistics
6. **Main Algorithm**: `PokerMCTS` orchestrates the four MCTS phases

## Usage

### Basic Usage

```python
from poker_mcts import parse_hole_cards, estimate_win_probability, get_preflop_odds

# Parse hole cards from string
hole_cards = parse_hole_cards("AsKh")  # Ace of Spades, King of Hearts

# Estimate win probability
estimated = estimate_win_probability(hole_cards, iterations=10000)

# Get ground truth for comparison
ground_truth = get_preflop_odds(hole_cards)

print(f"Estimated: {estimated:.3f}")
print(f"Ground Truth: {ground_truth:.3f}")
print(f"Difference: {abs(estimated - ground_truth):.3f}")
```

### Running Tests

```bash
# Quick test with minimal iterations
python3 test_poker.py

# Full test suite (takes longer)
python3 poker_mcts.py

# Interactive mode - test your own hands
python3 interactive_poker.py
```

## Card String Format

Cards are represented as 4-character strings:
- First character: Rank (`A`, `K`, `Q`, `J`, `T`, `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2`)
- Second character: Suit (`s`, `h`, `d`, `c`)
- Third character: Rank of second card
- Fourth character: Suit of second card

Examples:
- `"AsKh"` - Ace of Spades, King of Hearts
- `"TcTd"` - Ten of Clubs, Ten of Diamonds
- `"7s2h"` - Seven of Spades, Two of Hearts

## Algorithm Details

### MCTS Phases

1. **Selection**: Traverse tree using UCB1 until reaching a leaf node
2. **Expansion**: Add up to 1000 randomly sampled children (if not terminal)
3. **Simulation**: Complete random rollout to showdown
4. **Backpropagation**: Update win/loss statistics up the tree

### UCB1 Formula

```
UCB1(i) = wi/ni + c * sqrt(ln(N)/ni)
```

Where:
- `wi` = number of wins for child i
- `ni` = number of simulations for child i  
- `N` = number of simulations for parent
- `c` = exploration constant (default: √2)

### Performance Considerations

- **Sampling Limit**: Each level limited to 1000 children to manage computational complexity
- **Random Sampling**: Uses random sampling when total possibilities exceed 1000
- **Efficient Deck Management**: Tracks excluded cards to avoid invalid states
- **Optimized Hand Evaluation**: Caches computations where possible

## Validation

The implementation includes a comprehensive ground truth table with pre-flop win rates for all possible starting hands in 2-player Texas Hold'em. The MCTS estimates are typically within a few percentage points of these known values.

## Example Results

```
Analyzing AsAh... (Pocket Aces)
Ground Truth: 0.853
MCTS Estimate: 0.847
Difference: 0.006

Analyzing KsKh... (Pocket Kings)  
Ground Truth: 0.826
MCTS Estimate: 0.831
Difference: 0.005

Analyzing 7s2h... (Weak Hand)
Ground Truth: 0.370
MCTS Estimate: 0.378
Difference: 0.008
```

## Technical Requirements

- Python 3.6+
- Standard library only (no external dependencies)
- Implements all components from scratch as required

## File Structure

- `poker_mcts.py` - Main implementation with all classes and algorithms
- `test_poker.py` - Quick test script with minimal iterations
- `interactive_poker.py` - Interactive command-line interface for testing custom hands
- `README.md` - This documentation

## Future Improvements

- Parallel MCTS with multiple threads
- More sophisticated hand evaluation caching
- Progressive widening for better exploration
- Integration with actual poker game engines