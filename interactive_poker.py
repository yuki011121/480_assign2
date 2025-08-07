from poker_mcts import parse_hole_cards, estimate_win_probability, get_preflop_odds

def interactive_poker_estimator():
    """Interactive command-line interface for poker win probability estimation"""
    print("=" * 60)
    print("Texas Hold'em MCTS Win Probability Estimator - Interactive Mode")
    print("=" * 60)
    print()
    print("Enter your hole cards using 4-character format:")
    print("  - Ranks: A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2")
    print("  - Suits: s (spades), h (hearts), d (diamonds), c (clubs)")
    print("  - Example: AsKh (Ace of Spades, King of Hearts)")
    print("  - Example: TcTd (Pocket Tens)")
    print()
    print("Type 'quit' or 'exit' to stop.")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("Enter your hole cards (or 'quit'): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Thanks for using the poker estimator!")
                break
            
            if len(user_input) != 4:
                print("Error: Please enter exactly 4 characters (e.g., 'AsKh')")
                continue
            
            # Parse the hole cards
            hole_cards = parse_hole_cards(user_input)
            
            print(f"\nAnalyzing: {hole_cards[0]} {hole_cards[1]}")
            print("-" * 40)
            
            # Get ground truth
            ground_truth = get_preflop_odds(hole_cards)
            print(f"Ground Truth Win Rate: {ground_truth:.1%}")
            
            # Ask user for number of iterations
            iterations_input = input("Enter number of MCTS iterations (default 1000): ").strip()
            try:
                iterations = int(iterations_input) if iterations_input else 1000
                if iterations <= 0:
                    iterations = 1000
                    print("Using default 1000 iterations.")
            except ValueError:
                iterations = 1000
                print("Invalid input. Using default 1000 iterations.")
            
            # Estimate with MCTS
            print(f"\nRunning MCTS with {iterations} iterations...")
            estimated = estimate_win_probability(hole_cards, iterations=iterations)
            
            # Show results
            print(f"MCTS Estimate: {estimated:.1%}")
            difference = abs(estimated - ground_truth)
            print(f"Difference: {difference:.1%}")
            
            # Provide interpretation
            if ground_truth > 0.7:
                strength = "Very Strong"
            elif ground_truth > 0.6:
                strength = "Strong"
            elif ground_truth > 0.5:
                strength = "Above Average"
            elif ground_truth > 0.4:
                strength = "Below Average"
            else:
                strength = "Weak"
            
            print(f"Hand Strength: {strength}")
            print()
            
        except ValueError as e:
            print(f"Error parsing cards: {e}")
            print("Please use the correct format (e.g., 'AsKh')")
            print()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            print()

if __name__ == "__main__":
    interactive_poker_estimator()
