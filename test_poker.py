from poker_mcts import *

def quick_test():
    """Quick test with minimal iterations"""
    print("Quick MCTS Test")
    print("=" * 30)
    
    # Test with pocket aces
    try:
        hole_cards = parse_hole_cards("AsAh")
        print(f"Testing with Pocket Aces: {hole_cards[0]} {hole_cards[1]}")
        
        # Ground truth
        ground_truth = get_preflop_odds(hole_cards)
        print(f"Ground Truth: {ground_truth:.3f}")
        
        # Quick MCTS estimate with fewer iterations
        estimated = estimate_win_probability(hole_cards, iterations=100)
        print(f"MCTS Estimate (100 iterations): {estimated:.3f}")
        
        difference = abs(estimated - ground_truth)
        print(f"Difference: {difference:.3f}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()