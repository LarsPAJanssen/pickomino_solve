#!/usr/bin/env python3
"""
Performance comparison script for sequential vs parallel MCTS
"""

import multiprocessing
import time

from src.game import GameState
from src.parallel_tree import ParallelMCTS
from src.tree import MCTS


def create_test_game_state():
    """Create a test game state for performance testing"""
    return GameState(hand=[])


def test_sequential_performance(num_simulations=1000):
    """Test sequential MCTS performance"""
    print(f"Testing sequential MCTS with {num_simulations} simulations...")
    game_state = create_test_game_state()
    mcts = MCTS(game_state)

    start_time = time.perf_counter()
    results = mcts.run(num_simulations)
    end_time = time.perf_counter()

    sequential_time = end_time - start_time
    print(f"Sequential time: {sequential_time:.4f}s")
    print(f"Simulations per second: {num_simulations/sequential_time:.2f}")

    return sequential_time, results


def test_parallel_performance(num_simulations=1000, num_workers=None, batch_size=100):
    """Test parallel MCTS performance"""
    print(
        f"Testing parallel MCTS with {num_simulations} simulations, {num_workers or multiprocessing.cpu_count()} workers..."
    )
    game_state = create_test_game_state()
    mcts = ParallelMCTS(game_state, num_workers=num_workers)

    start_time = time.perf_counter()
    results = mcts.run_parallel(num_simulations, batch_size=batch_size)
    end_time = time.perf_counter()

    parallel_time = end_time - start_time
    print(f"Parallel time: {parallel_time:.4f}s")
    print(f"Simulations per second: {num_simulations/parallel_time:.2f}")

    mcts.close()
    return parallel_time, results


def compare_results(seq_results, par_results):
    """Compare results from sequential and parallel runs"""
    print("\nComparing results...")

    # Sort both result lists by action for comparison
    seq_sorted = sorted(seq_results, key=lambda x: str(x["action"]))
    par_sorted = sorted(par_results, key=lambda x: str(x["action"]))

    print(f"Sequential found {len(seq_sorted)} actions")
    print(f"Parallel found {len(par_sorted)} actions")

    # Check if same actions were explored
    seq_actions = {str(r["action"]) for r in seq_sorted}
    par_actions = {str(r["action"]) for r in par_sorted}

    if seq_actions == par_actions:
        print("✓ Both methods explored the same actions")
    else:
        print("✗ Different actions explored:")
        print(f"  Sequential only: {seq_actions - par_actions}")
        print(f"  Parallel only: {par_actions - seq_actions}")

    # Compare statistics for common actions
    common_actions = seq_actions & par_actions
    print(f"\nComparing {len(common_actions)} common actions:")

    for action_str in common_actions:
        seq_result = next(r for r in seq_sorted if str(r["action"]) == action_str)
        par_result = next(r for r in par_sorted if str(r["action"]) == action_str)

        score_diff = abs(seq_result["expected_score"] - par_result["expected_score"])
        visit_diff = abs(seq_result["visit_count"] - par_result["visit_count"])

        if score_diff > 0.1 or visit_diff > 5:
            print(f"  {action_str}:")
            print(
                f"    Score: seq={seq_result['expected_score']:.2f}, par={par_result['expected_score']:.2f}, diff={score_diff:.2f}"
            )
            print(
                f"    Visits: seq={seq_result['visit_count']}, par={par_result['visit_count']}, diff={visit_diff}"
            )


def main():
    """Main performance test"""
    print("MCTS Performance Comparison")
    print("=" * 50)

    num_simulations = 2000  # Use more simulations for better measurement

    # Test sequential
    seq_time, seq_results = test_sequential_performance(num_simulations)

    print("\n" + "-" * 50)

    # Test parallel with different configurations
    configs = [
        {"num_workers": 2, "batch_size": 50},
        {"num_workers": 4, "batch_size": 100},
        {"num_workers": 8, "batch_size": 200},
    ]

    best_speedup = 0
    best_config = None

    for config in configs:
        print(f"\nTesting config: {config}")
        par_time, par_results = test_parallel_performance(
            num_simulations, config["num_workers"], config["batch_size"]
        )

        speedup = seq_time / par_time
        print(f"Speedup: {speedup:.2f}x")

        if speedup > best_speedup:
            best_speedup = speedup
            best_config = config
            best_results = par_results

    print("\n" + "=" * 50)
    print(f"Best speedup: {best_speedup:.2f}x with config: {best_config}")

    # Compare results from best parallel config with sequential
    compare_results(seq_results, best_results)

    print("\nSummary:")
    print(f"Sequential: {seq_time:.4f}s ({num_simulations/seq_time:.2f} sims/s)")
    print(f"Parallel:   {par_time:.4f}s ({num_simulations/par_time:.2f} sims/s)")
    print(f"Speedup:    {seq_time/par_time:.2f}x")


if __name__ == "__main__":
    main()
