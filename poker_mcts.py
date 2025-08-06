import random
import math
from typing import List, Tuple, Set, Optional, Dict
from enum import Enum
from itertools import combinations
from collections import Counter

class Suit(Enum):
    HEARTS = 'H'
    DIAMONDS = 'D'
    CLUBS = 'C'
    SPADES = 'S'

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.rank, self.suit))
    
    def __repr__(self):
        rank_str = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 
                   10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        return f"{rank_str[self.rank.value]}{self.suit.value}"

class Deck:
    def __init__(self, excluded_cards: Set[Card] = None):
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                card = Card(rank, suit)
                if excluded_cards is None or card not in excluded_cards:
                    self.cards.append(card)
        random.shuffle(self.cards)
    
    def draw(self, n: int = 1) -> List[Card]:
        if len(self.cards) < n:
            raise ValueError("Not enough cards in deck")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn
    
    def peek(self, n: int = 1) -> List[Card]:
        """Peek at top n cards without removing them"""
        if len(self.cards) < n:
            raise ValueError("Not enough cards in deck")
        return self.cards[:n]

class HandRank(Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class HandEvaluator:
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate a 5-card hand and return (hand_rank, tiebreakers)
        Tiebreakers are in descending order of importance
        """
        if len(cards) != 5:
            raise ValueError("Hand must contain exactly 5 cards")
        
        # Sort cards by rank (descending)
        sorted_cards = sorted(cards, key=lambda c: c.rank.value, reverse=True)
        ranks = [c.rank.value for c in sorted_cards]
        suits = [c.suit for c in sorted_cards]
        
        # Count ranks
        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = False
        if ranks == [14, 5, 4, 3, 2]:  # A-2-3-4-5 straight (wheel)
            is_straight = True
            straight_high = 5
        elif all(ranks[i] - ranks[i+1] == 1 for i in range(4)):
            is_straight = True
            straight_high = ranks[0]
        
        # Determine hand rank and tiebreakers
        if is_straight and is_flush:
            if ranks[0] == 14 and ranks[1] == 13:  # A-K-Q-J-T
                return HandRank.ROYAL_FLUSH, []
            else:
                return HandRank.STRAIGHT_FLUSH, [straight_high]
        elif counts == [4, 1]:
            # Four of a kind
            four_rank = [rank for rank, count in rank_counts.items() if count == 4][0]
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.FOUR_OF_KIND, [four_rank, kicker]
        elif counts == [3, 2]:
            # Full house
            three_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            return HandRank.FULL_HOUSE, [three_rank, pair_rank]
        elif is_flush:
            return HandRank.FLUSH, ranks
        elif is_straight:
            return HandRank.STRAIGHT, [straight_high]
        elif counts == [3, 1, 1]:
            # Three of a kind
            three_rank = [rank for rank, count in rank_counts.items() if count == 3][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.THREE_OF_KIND, [three_rank] + kickers
        elif counts == [2, 2, 1]:
            # Two pair
            pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
            kicker = [rank for rank, count in rank_counts.items() if count == 1][0]
            return HandRank.TWO_PAIR, pairs + [kicker]
        elif counts == [2, 1, 1, 1]:
            # One pair
            pair_rank = [rank for rank, count in rank_counts.items() if count == 2][0]
            kickers = sorted([rank for rank, count in rank_counts.items() if count == 1], reverse=True)
            return HandRank.PAIR, [pair_rank] + kickers
        else:
            # High card
            return HandRank.HIGH_CARD, ranks

    @staticmethod
    def best_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Find the best 5-card hand from 2 hole cards + 5 community cards"""
        all_cards = hole_cards + community_cards
        if len(all_cards) != 7:
            raise ValueError("Must have exactly 7 cards (2 hole + 5 community)")
        
        best_rank = HandRank.HIGH_CARD
        best_tiebreakers = []
        
        # Try all combinations of 5 cards from 7
        for hand in combinations(all_cards, 5):
            rank, tiebreakers = HandEvaluator.evaluate_hand(list(hand))
            if (rank.value > best_rank.value or 
                (rank.value == best_rank.value and tiebreakers > best_tiebreakers)):
                best_rank = rank
                best_tiebreakers = tiebreakers
        
        return best_rank, best_tiebreakers

    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[int]], hand2: Tuple[HandRank, List[int]]) -> int:
        """Compare two hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 for tie"""
        rank1, tiebreakers1 = hand1
        rank2, tiebreakers2 = hand2
        
        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1
        else:
            # Same rank, compare tiebreakers
            for t1, t2 in zip(tiebreakers1, tiebreakers2):
                if t1 > t2:
                    return 1
                elif t1 < t2:
                    return -1
            return 0  # Tie

class MCTSNode:
    def __init__(self, parent=None, game_state=None, action=None):
        self.parent = parent
        self.children = []
        self.game_state = game_state  # Current state of the game
        self.action = action  # Action that led to this state
        
        # MCTS statistics
        self.visits = 0
        self.wins = 0.0
        self.is_expanded = False
        
        # Track what cards are known at this level
        self.known_cards = set()  # Cards that are revealed
        self.available_cards = set()  # Cards still available to be drawn
        
    def is_leaf(self) -> bool:
        """Check if this node is a leaf (not expanded or terminal)"""
        return not self.is_expanded
    
    def is_terminal(self) -> bool:
        """Check if this node represents a terminal game state"""
        return (self.game_state is not None and 
                self.game_state.stage == 'showdown')
    
    def add_child(self, child_node):
        """Add a child node"""
        child_node.parent = self
        self.children.append(child_node)
    
    def update(self, result: float):
        """Update node statistics with simulation result"""
        self.visits += 1
        self.wins += result
    
    def ucb1_value(self, c: float = math.sqrt(2)) -> float:
        """Calculate UCB1 value for this node"""
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration
    
    def best_child(self, c: float = math.sqrt(2)):
        """Select the best child using UCB1"""
        if not self.children:
            return None
        return max(self.children, key=lambda child: child.ucb1_value(c))
    
    def most_visited_child(self):
        """Get the child with the most visits"""
        if not self.children:
            return None
        return max(self.children, key=lambda child: child.visits)

class GameState:
    def __init__(self, player_hole_cards: List[Card]):
        self.player_hole_cards = player_hole_cards
        self.opponent_hole_cards = None
        self.flop = None
        self.turn = None
        self.river = None
        self.stage = 'preflop'  # preflop, flop, turn, river, showdown
        
        # Track all known cards
        self.known_cards = set(player_hole_cards)
    
    def copy(self):
        """Create a copy of the game state"""
        new_state = GameState(self.player_hole_cards.copy())
        new_state.opponent_hole_cards = self.opponent_hole_cards.copy() if self.opponent_hole_cards else None
        new_state.flop = self.flop.copy() if self.flop else None
        new_state.turn = self.turn
        new_state.river = self.river
        new_state.stage = self.stage
        new_state.known_cards = self.known_cards.copy()
        return new_state
    
    def get_community_cards(self) -> List[Card]:
        """Get all community cards revealed so far"""
        community = []
        if self.flop:
            community.extend(self.flop)
        if self.turn:
            community.append(self.turn)
        if self.river:
            community.append(self.river)
        return community
    
    def advance_to_showdown(self, deck: Deck):
        """Complete the hand by drawing remaining community cards"""
        community = self.get_community_cards()
        
        if len(community) < 5:
            remaining_cards = deck.draw(5 - len(community))
            
            if len(community) == 0:
                # No flop yet
                self.flop = remaining_cards[:3]
                self.known_cards.update(self.flop)
                if len(remaining_cards) > 3:
                    self.turn = remaining_cards[3]
                    self.known_cards.add(self.turn)
                if len(remaining_cards) > 4:
                    self.river = remaining_cards[4]
                    self.known_cards.add(self.river)
            elif len(community) == 3:
                # Flop is set, need turn and river
                self.turn = remaining_cards[0]
                self.known_cards.add(self.turn)
                if len(remaining_cards) > 1:
                    self.river = remaining_cards[1]
                    self.known_cards.add(self.river)
            elif len(community) == 4:
                # Just need river
                self.river = remaining_cards[0]
                self.known_cards.add(self.river)
        
        self.stage = 'showdown'
    
    def evaluate_winner(self) -> int:
        """Evaluate who wins at showdown. Returns 1 for player win, -1 for opponent win, 0 for tie"""
        if self.stage != 'showdown':
            raise ValueError("Cannot evaluate winner before showdown")
        
        community_cards = self.get_community_cards()
        if len(community_cards) != 5:
            raise ValueError("Need exactly 5 community cards for showdown")
        
        player_hand = HandEvaluator.best_hand(self.player_hole_cards, community_cards)
        opponent_hand = HandEvaluator.best_hand(self.opponent_hole_cards, community_cards)
        
        return HandEvaluator.compare_hands(player_hand, opponent_hand)

class PokerMCTS:
    def __init__(self, exploration_constant: float = math.sqrt(2), max_children: int = 1000):
        self.c = exploration_constant
        self.max_children = max_children
    
    def search(self, root_state: GameState, iterations: int) -> float:
        """Run MCTS for the specified number of iterations"""
        root = MCTSNode(game_state=root_state.copy())
        
        for _ in range(iterations):
            # Selection: traverse tree using UCB1
            node = self._select(root)
            
            # Expansion: add children if not terminal
            if not node.is_terminal() and node.visits > 0:
                node = self._expand(node)
            
            # Simulation: random rollout to completion
            result = self._simulate(node)
            
            # Backpropagation: update statistics
            self._backpropagate(node, result)
        
        # Return win probability
        if root.visits == 0:
            return 0.5  # No information, assume 50%
        
        return root.wins / root.visits
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select a leaf node using UCB1"""
        current = node
        
        while not current.is_leaf() and not current.is_terminal():
            current = current.best_child(self.c)
            if current is None:
                break
        
        return current
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand the node by adding children"""
        if node.is_terminal():
            return node
        
        game_state = node.game_state
        stage = game_state.stage
        
        # Generate possible children based on current stage
        children = []
        
        if stage == 'preflop':
            # Add opponent hole card combinations
            children = self._generate_opponent_combinations(game_state)
        elif stage == 'flop_set':
            # Add flop combinations
            children = self._generate_flop_combinations(game_state)
        elif stage == 'turn_set':
            # Add turn card options
            children = self._generate_turn_combinations(game_state)
        elif stage == 'river_set':
            # Add river card options
            children = self._generate_river_combinations(game_state)
        
        # Limit to max_children by random sampling
        if len(children) > self.max_children:
            children = random.sample(children, self.max_children)
        
        # Create child nodes
        for child_state in children:
            child_node = MCTSNode(parent=node, game_state=child_state)
            node.add_child(child_node)
        
        node.is_expanded = True
        
        # Return a random child for simulation
        if node.children:
            return random.choice(node.children)
        return node
    
    def _simulate(self, node: MCTSNode) -> float:
        """Simulate a random game to completion"""
        game_state = node.game_state.copy()
        
        # Create deck excluding known cards
        deck = Deck(excluded_cards=game_state.known_cards)
        
        # If opponent hole cards not set, randomly assign them
        if game_state.opponent_hole_cards is None:
            game_state.opponent_hole_cards = deck.draw(2)
            game_state.known_cards.update(game_state.opponent_hole_cards)
            # Recreate deck to exclude opponent cards
            deck = Deck(excluded_cards=game_state.known_cards)
        
        # Complete the hand
        game_state.advance_to_showdown(deck)
        
        # Evaluate result
        result = game_state.evaluate_winner()
        
        # Convert to win probability (1 for win, 0.5 for tie, 0 for loss)
        if result > 0:
            return 1.0
        elif result == 0:
            return 0.5
        else:
            return 0.0
    
    def _backpropagate(self, node: MCTSNode, result: float):
        """Update statistics up the tree"""
        current = node
        while current is not None:
            current.update(result)
            current = current.parent
    
    def _generate_opponent_combinations(self, game_state: GameState) -> List[GameState]:
        """Generate possible opponent hole card combinations"""
        opponent_combinations = []
        deck = Deck(excluded_cards=game_state.known_cards)
        
        # Generate all possible 2-card combinations for opponent
        available_cards = deck.cards
        for i in range(len(available_cards)):
            for j in range(i + 1, len(available_cards)):
                new_state = game_state.copy()
                new_state.opponent_hole_cards = [available_cards[i], available_cards[j]]
                new_state.known_cards.update(new_state.opponent_hole_cards)
                new_state.stage = 'flop_set'
                opponent_combinations.append(new_state)
        
        return opponent_combinations
    
    def _generate_flop_combinations(self, game_state: GameState) -> List[GameState]:
        """Generate possible flop combinations"""
        flop_combinations = []
        deck = Deck(excluded_cards=game_state.known_cards)
        available_cards = deck.cards
        
        # Generate combinations of 3 cards for flop
        for combo in combinations(available_cards, 3):
            new_state = game_state.copy()
            new_state.flop = list(combo)
            new_state.known_cards.update(new_state.flop)
            new_state.stage = 'turn_set'
            flop_combinations.append(new_state)
        
        return flop_combinations
    
    def _generate_turn_combinations(self, game_state: GameState) -> List[GameState]:
        """Generate possible turn cards"""
        turn_combinations = []
        deck = Deck(excluded_cards=game_state.known_cards)
        
        for card in deck.cards:
            new_state = game_state.copy()
            new_state.turn = card
            new_state.known_cards.add(card)
            new_state.stage = 'river_set'
            turn_combinations.append(new_state)
        
        return turn_combinations
    
    def _generate_river_combinations(self, game_state: GameState) -> List[GameState]:
        """Generate possible river cards"""
        river_combinations = []
        deck = Deck(excluded_cards=game_state.known_cards)
        
        for card in deck.cards:
            new_state = game_state.copy()
            new_state.river = card
            new_state.known_cards.add(card)
            new_state.stage = 'showdown'
            river_combinations.append(new_state)
        
        return river_combinations

# Ground truth preflop win rates (2-player Texas Hold'em)
# Format: (rank1, rank2, suited): win_probability
PREFLOP_ODDS = {
    # Pocket pairs
    ('A', 'A', False): 0.853, ('K', 'K', False): 0.826, ('Q', 'Q', False): 0.799,
    ('J', 'J', False): 0.773, ('T', 'T', False): 0.747, ('9', '9', False): 0.720,
    ('8', '8', False): 0.693, ('7', '7', False): 0.666, ('6', '6', False): 0.639,
    ('5', '5', False): 0.612, ('4', '4', False): 0.585, ('3', '3', False): 0.559,
    ('2', '2', False): 0.532,
    
    # Ace combinations
    ('A', 'K', True): 0.669, ('A', 'K', False): 0.653,
    ('A', 'Q', True): 0.660, ('A', 'Q', False): 0.643,
    ('A', 'J', True): 0.651, ('A', 'J', False): 0.633,
    ('A', 'T', True): 0.641, ('A', 'T', False): 0.622,
    ('A', '9', True): 0.629, ('A', '9', False): 0.609,
    ('A', '8', True): 0.618, ('A', '8', False): 0.597,
    ('A', '7', True): 0.607, ('A', '7', False): 0.585,
    ('A', '6', True): 0.596, ('A', '6', False): 0.573,
    ('A', '5', True): 0.587, ('A', '5', False): 0.563,
    ('A', '4', True): 0.578, ('A', '4', False): 0.554,
    ('A', '3', True): 0.570, ('A', '3', False): 0.545,
    ('A', '2', True): 0.562, ('A', '2', False): 0.537,
    
    # King combinations
    ('K', 'Q', True): 0.628, ('K', 'Q', False): 0.610,
    ('K', 'J', True): 0.619, ('K', 'J', False): 0.600,
    ('K', 'T', True): 0.609, ('K', 'T', False): 0.589,
    ('K', '9', True): 0.597, ('K', '9', False): 0.576,
    ('K', '8', True): 0.586, ('K', '8', False): 0.564,
    ('K', '7', True): 0.575, ('K', '7', False): 0.552,
    ('K', '6', True): 0.564, ('K', '6', False): 0.540,
    ('K', '5', True): 0.554, ('K', '5', False): 0.529,
    ('K', '4', True): 0.544, ('K', '4', False): 0.519,
    ('K', '3', True): 0.535, ('K', '3', False): 0.509,
    ('K', '2', True): 0.527, ('K', '2', False): 0.500,
    
    # Queen combinations
    ('Q', 'J', True): 0.597, ('Q', 'J', False): 0.579,
    ('Q', 'T', True): 0.587, ('Q', 'T', False): 0.568,
    ('Q', '9', True): 0.575, ('Q', '9', False): 0.555,
    ('Q', '8', True): 0.564, ('Q', '8', False): 0.543,
    ('Q', '7', True): 0.553, ('Q', '7', False): 0.531,
    ('Q', '6', True): 0.542, ('Q', '6', False): 0.519,
    ('Q', '5', True): 0.532, ('Q', '5', False): 0.508,
    ('Q', '4', True): 0.522, ('Q', '4', False): 0.498,
    ('Q', '3', True): 0.513, ('Q', '3', False): 0.488,
    ('Q', '2', True): 0.505, ('Q', '2', False): 0.479,
    
    # Jack combinations  
    ('J', 'T', True): 0.565, ('J', 'T', False): 0.546,
    ('J', '9', True): 0.553, ('J', '9', False): 0.533,
    ('J', '8', True): 0.542, ('J', '8', False): 0.521,
    ('J', '7', True): 0.531, ('J', '7', False): 0.509,
    ('J', '6', True): 0.520, ('J', '6', False): 0.498,
    ('J', '5', True): 0.510, ('J', '5', False): 0.487,
    ('J', '4', True): 0.500, ('J', '4', False): 0.477,
    ('J', '3', True): 0.491, ('J', '3', False): 0.467,
    ('J', '2', True): 0.483, ('J', '2', False): 0.458,
    
    # Ten combinations
    ('T', '9', True): 0.531, ('T', '9', False): 0.511,
    ('T', '8', True): 0.520, ('T', '8', False): 0.499,
    ('T', '7', True): 0.509, ('T', '7', False): 0.488,
    ('T', '6', True): 0.498, ('T', '6', False): 0.476,
    ('T', '5', True): 0.488, ('T', '5', False): 0.465,
    ('T', '4', True): 0.478, ('T', '4', False): 0.455,
    ('T', '3', True): 0.469, ('T', '3', False): 0.445,
    ('T', '2', True): 0.461, ('T', '2', False): 0.436,
    
    # Nine combinations
    ('9', '8', True): 0.498, ('9', '8', False): 0.477,
    ('9', '7', True): 0.487, ('9', '7', False): 0.466,
    ('9', '6', True): 0.476, ('9', '6', False): 0.454,
    ('9', '5', True): 0.466, ('9', '5', False): 0.443,
    ('9', '4', True): 0.456, ('9', '4', False): 0.433,
    ('9', '3', True): 0.447, ('9', '3', False): 0.423,
    ('9', '2', True): 0.439, ('9', '2', False): 0.414,
    
    # Eight combinations
    ('8', '7', True): 0.465, ('8', '7', False): 0.444,
    ('8', '6', True): 0.454, ('8', '6', False): 0.432,
    ('8', '5', True): 0.444, ('8', '5', False): 0.421,
    ('8', '4', True): 0.434, ('8', '4', False): 0.411,
    ('8', '3', True): 0.425, ('8', '3', False): 0.401,
    ('8', '2', True): 0.417, ('8', '2', False): 0.392,
    
    # Seven combinations
    ('7', '6', True): 0.432, ('7', '6', False): 0.410,
    ('7', '5', True): 0.422, ('7', '5', False): 0.399,
    ('7', '4', True): 0.412, ('7', '4', False): 0.389,
    ('7', '3', True): 0.403, ('7', '3', False): 0.379,
    ('7', '2', True): 0.395, ('7', '2', False): 0.370,
    
    # Six combinations
    ('6', '5', True): 0.400, ('6', '5', False): 0.377,
    ('6', '4', True): 0.390, ('6', '4', False): 0.367,
    ('6', '3', True): 0.381, ('6', '3', False): 0.357,
    ('6', '2', True): 0.373, ('6', '2', False): 0.348,
    
    # Five combinations
    ('5', '4', True): 0.368, ('5', '4', False): 0.345,
    ('5', '3', True): 0.359, ('5', '3', False): 0.335,
    ('5', '2', True): 0.351, ('5', '2', False): 0.326,
    
    # Four combinations
    ('4', '3', True): 0.337, ('4', '3', False): 0.313,
    ('4', '2', True): 0.329, ('4', '2', False): 0.304,
    
    # Three-Two
    ('3', '2', True): 0.307, ('3', '2', False): 0.282,
}

def card_to_rank_str(card: Card) -> str:
    """Convert card rank to string representation"""
    rank_map = {14: 'A', 13: 'K', 12: 'Q', 11: 'J', 10: 'T', 
                9: '9', 8: '8', 7: '7', 6: '6', 5: '5', 4: '4', 3: '3', 2: '2'}
    return rank_map[card.rank.value]

def get_preflop_odds(hole_cards: List[Card]) -> float:
    """Get ground truth preflop odds for given hole cards"""
    if len(hole_cards) != 2:
        raise ValueError("Must provide exactly 2 hole cards")
    
    card1, card2 = hole_cards
    rank1_str = card_to_rank_str(card1)
    rank2_str = card_to_rank_str(card2)
    
    # Ensure consistent ordering (higher rank first)
    if card1.rank.value < card2.rank.value:
        rank1_str, rank2_str = rank2_str, rank1_str
    
    # Check if suited
    is_suited = card1.suit == card2.suit
    
    # Look up in preflop odds table
    key = (rank1_str, rank2_str, is_suited)
    return PREFLOP_ODDS.get(key, 0.5)  # Default to 50% if not found

def parse_hole_cards(card_str: str) -> List[Card]:
    """Parse hole cards from string like 'AsKh' or 'TcTd'"""
    if len(card_str) != 4:
        raise ValueError("Card string must be exactly 4 characters (e.g., 'AsKh')")
    
    rank_map = {'A': Rank.ACE, 'K': Rank.KING, 'Q': Rank.QUEEN, 'J': Rank.JACK, 
                'T': Rank.TEN, '9': Rank.NINE, '8': Rank.EIGHT, '7': Rank.SEVEN,
                '6': Rank.SIX, '5': Rank.FIVE, '4': Rank.FOUR, '3': Rank.THREE, '2': Rank.TWO}
    
    suit_map = {'s': Suit.SPADES, 'h': Suit.HEARTS, 'd': Suit.DIAMONDS, 'c': Suit.CLUBS}
    
    try:
        card1 = Card(rank_map[card_str[0].upper()], suit_map[card_str[1].lower()])
        card2 = Card(rank_map[card_str[2].upper()], suit_map[card_str[3].lower()])
        return [card1, card2]
    except KeyError as e:
        raise ValueError(f"Invalid card character: {e}")

def estimate_win_probability(hole_cards: List[Card], iterations: int = 10000) -> float:
    """Estimate win probability using MCTS"""
    game_state = GameState(hole_cards)
    mcts = PokerMCTS()
    return mcts.search(game_state, iterations)

def main():
    """Main function to test the MCTS poker estimator"""
    print("Texas Hold'em MCTS Win Probability Estimator")
    print("=" * 50)
    
    # Test with some example hands
    test_hands = [
        "AsAh",  # Pocket Aces
        "KsKh",  # Pocket Kings
        "AsKs",  # Suited AK
        "AsKh",  # Offsuit AK
        "QsJs",  # Suited QJ
        "7s2h",  # Weak hand
    ]
    
    for hand_str in test_hands:
        try:
            hole_cards = parse_hole_cards(hand_str)
            
            # Get ground truth
            ground_truth = get_preflop_odds(hole_cards)
            
            # Estimate with MCTS
            print(f"\nAnalyzing {hand_str}...")
            estimated = estimate_win_probability(hole_cards, iterations=1000)
            
            # Calculate difference
            difference = abs(estimated - ground_truth)
            
            print(f"Ground Truth: {ground_truth:.3f}")
            print(f"MCTS Estimate: {estimated:.3f}")
            print(f"Difference: {difference:.3f}")
            
        except Exception as e:
            print(f"Error analyzing {hand_str}: {e}")

if __name__ == "__main__":
    main()