#!/usr/bin/env python3
"""
Optimization script to find the best parallel configuration
"""

import multiprocessing
import time

from src.game import GameState
from src.parallel_tree import ParallelMCTS


def create_test_game_state():
    """Create a test game state for optimization"""
    return GameState(hand=[])


def test_configuration(num_simulations, num_workers, batch_size):
    """Test a specific configuration"""
    game_state = create_test_game_state()
    mcts = ParallelMCTS(game_state, num_workers=num_workers)

    start_time = time.perf_counter()
    results = mcts.run_parallel(num_simulations, batch_size=batch_size)
    end_time = time.perf_counter()

    parallel_time = end_time - start_time
    simulations_per_second = num_simulations / parallel_time

    mcts.close()
    return parallel_time, simulations_per_second, results


def main():
    """Main optimization test"""
    print("MCTS Parallel Configuration Optimization")
    print("=" * 60)

    num_simulations = 5000  # Use more simulations for better measurement
    cpu_count = multiprocessing.cpu_count()

    print(f"CPU cores available: {cpu_count}")
    print(f"Testing with {num_simulations} simulations")
    print()

    # Test different configurations
    configs = []

    # Test different worker counts
    for workers in [2, 4, 6, 8]:
        # Test different batch sizes
        for batch_size in [50, 100, 200, 500]:
            configs.append({"num_workers": workers, "batch_size": batch_size})

    results = []

    for i, config in enumerate(configs, 1):
        print(
            f"Testing config {i}/{len(configs)}: workers={config['num_workers']}, batch_size={config['batch_size']}"
        )

        try:
            time_taken, sims_per_sec, _ = test_configuration(
                num_simulations, config["num_workers"], config["batch_size"]
            )

            results.append(
                {
                    "config": config,
                    "time": time_taken,
                    "sims_per_sec": sims_per_sec,
                    "efficiency": sims_per_sec / config["num_workers"],
                }
            )

            print(
                f"  Time: {time_taken:.3f}s, Sims/s: {sims_per_sec:.0f}, Efficiency: {sims_per_sec/config['num_workers']:.0f} sims/s/core"
            )

        except Exception as e:
            print(f"  Error: {e}")
            continue

    # Sort by performance (highest simulations per second)
    results.sort(key=lambda x: x["sims_per_sec"], reverse=True)

    print("\n" + "=" * 60)
    print("TOP PERFORMING CONFIGURATIONS:")
    print("=" * 60)

    for i, result in enumerate(results[:5], 1):
        config = result["config"]
        print(f"{i}. Workers: {config['num_workers']}, Batch: {config['batch_size']}")
        print(f"   Time: {result['time']:.3f}s, Sims/s: {result['sims_per_sec']:.0f}")
        print(f"   Efficiency: {result['efficiency']:.0f} sims/s/core")
        print()

    # Find the most efficient configuration
    results.sort(key=lambda x: x["efficiency"], reverse=True)
    best_efficient = results[0]

    print("MOST EFFICIENT CONFIGURATION (per core):")
    print("=" * 60)
    config = best_efficient["config"]
    print(f"Workers: {config['num_workers']}, Batch: {config['batch_size']}")
    print(
        f"Time: {best_efficient['time']:.3f}s, Sims/s: {best_efficient['sims_per_sec']:.0f}"
    )
    print(f"Efficiency: {best_efficient['efficiency']:.0f} sims/s/core")


if __name__ == "__main__":
    main()
