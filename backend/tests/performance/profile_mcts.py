#!/usr/bin/env python3
"""
Profiling script for MCTS implementation to identify bottlenecks
"""

import cProfile
import io
import pstats
import time

from src.game import GameState
from src.tree import MCTS


def create_test_game_state():
    """Create a test game state for profiling"""
    # GameState requires a hand (list of dice values)
    # Start with an empty hand for initial state
    return GameState(hand=[])


def profile_mcts():
    """Profile the MCTS implementation"""
    game_state = create_test_game_state()
    mcts = MCTS(game_state)

    # Profile the run method
    pr = cProfile.Profile()
    pr.enable()

    # Run with a reasonable number of simulations
    _ = mcts.run(1000)

    pr.disable()

    # Print profiling results
    s = io.StringIO()
    sortby = "cumulative"
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())


def time_components():
    """Time individual components of MCTS"""
    game_state = create_test_game_state()
    mcts = MCTS(game_state)

    # Use more iterations for better timing accuracy
    iterations = 1000

    # Time selection
    start = time.perf_counter()
    for _ in range(iterations):
        mcts._select()
    select_time = time.perf_counter() - start

    # Time expansion
    node = mcts._select()
    start = time.perf_counter()
    expansion_count = 0
    for _ in range(iterations):
        if not node.is_terminal_node() and not node.is_fully_expanded():
            mcts._expand(node)
            expansion_count += 1
    expand_time = time.perf_counter() - start

    # Time simulation
    start = time.perf_counter()
    for _ in range(iterations):
        mcts._simulate(node)
    simulate_time = time.perf_counter() - start

    # Time backpropagation
    start = time.perf_counter()
    for _ in range(iterations):
        mcts._backpropagate(node, 50.0)
    backprop_time = time.perf_counter() - start

    print(f"Selection time ({iterations}x): {select_time:.6f}s")
    print(f"Expansion time ({expansion_count}x): {expand_time:.6f}s")
    print(f"Simulation time ({iterations}x): {simulate_time:.6f}s")
    print(f"Backpropagation time ({iterations}x): {backprop_time:.6f}s")

    total = select_time + expand_time + simulate_time + backprop_time
    if total > 0:
        print("\nPercentage breakdown:")
        print(f"Selection: {select_time/total*100:.1f}%")
        print(f"Expansion: {expand_time/total*100:.1f}%")
        print(f"Simulation: {simulate_time/total*100:.1f}%")
        print(f"Backpropagation: {backprop_time/total*100:.1f}%")
    else:
        print("\nAll operations completed too quickly to measure accurately")
        print("Simulation is likely the bottleneck based on MCTS characteristics")


if __name__ == "__main__":
    print("Profiling MCTS implementation...")
    print("=" * 50)

    print("\n1. Timing individual components:")
    time_components()

    print("\n2. Full profile:")
    profile_mcts()
