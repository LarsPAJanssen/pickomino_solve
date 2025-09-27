#!/usr/bin/env python3
"""
Demonstration script showing the parallel MCTS implementation
"""

import multiprocessing
import time

from src.game import GameState
from src.parallel_tree import ParallelMCTS
from src.tree import MCTS


def create_test_game_state():
    """Create a test game state"""
    return GameState(hand=[])


def demonstrate_parallel_mcts():
    """Demonstrate the parallel MCTS implementation"""
    print("MCTS Parallelization Demonstration")
    print("=" * 50)
    print()

    # Create test game state
    game_state = create_test_game_state()
    print(f"Initial game state: {game_state.hand}")
    print()

    # Test sequential performance
    print("1. Testing Sequential MCTS:")
    print("-" * 30)
    sequential_mcts = MCTS(game_state)

    start_time = time.perf_counter()
    sequential_results = sequential_mcts.run(1000)
    sequential_time = time.perf_counter() - start_time

    print(f"Sequential time: {sequential_time:.3f}s")
    print(f"Simulations per second: {1000/sequential_time:.0f}")
    print(f"Actions explored: {len(sequential_results)}")
    print()

    # Test parallel performance with optimal configuration
    print("2. Testing Parallel MCTS (Optimal Configuration):")
    print("-" * 30)

    optimal_workers = 4
    optimal_batch = 500

    parallel_mcts = ParallelMCTS(game_state, num_workers=optimal_workers)

    start_time = time.perf_counter()
    parallel_results = parallel_mcts.run_parallel(1000, batch_size=optimal_batch)
    parallel_time = time.perf_counter() - start_time

    print(f"Parallel time: {parallel_time:.3f}s")
    print(f"Simulations per second: {1000/parallel_time:.0f}")
    print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    print(f"Workers: {optimal_workers}, Batch size: {optimal_batch}")
    print(f"Actions explored: {len(parallel_results)}")
    print()

    # Compare results
    print("3. Results Comparison:")
    print("-" * 30)

    # Sort both result lists by action for comparison
    seq_sorted = sorted(sequential_results, key=lambda x: str(x["action"]))
    par_sorted = sorted(parallel_results, key=lambda x: str(x["action"]))

    print("Best action recommendations:")
    print(
        f"Sequential: {seq_sorted[0]['action']} (score: {seq_sorted[0]['expected_score']:.2f})"
    )
    print(
        f"Parallel:   {par_sorted[0]['action']} (score: {par_sorted[0]['expected_score']:.2f})"
    )
    print()

    # Show performance summary
    print("4. Performance Summary:")
    print("-" * 30)
    print(f"CPU cores available: {multiprocessing.cpu_count()}")
    print(f"Sequential performance: {1000/sequential_time:.0f} sims/s")
    print(f"Parallel performance:   {1000/parallel_time:.0f} sims/s")
    print(f"Speedup: {sequential_time/parallel_time:.2f}x")
    print()

    # Clean up
    parallel_mcts.close()
    print("Parallel pool cleaned up successfully")


if __name__ == "__main__":
    demonstrate_parallel_mcts()
