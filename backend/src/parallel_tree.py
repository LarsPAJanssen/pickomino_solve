import logging
import math
import multiprocessing
import random
from typing import List

from src.game import GameState
from src.tree import MCTS, Node, ResultAction

logger = logging.getLogger(__name__)


def simulate_worker(node_state: GameState) -> float:
    """
    Worker function for parallel simulation that can be pickled.
    Creates a temporary node from the state and simulates.
    """
    temp_node = Node(node_state)
    return simulate_single(temp_node)


def simulate_single(node: Node) -> float:
    """
    Single simulation (Rollout) phase: Play out a random game from the given node's state
    until a terminal state is reached, and return the final score.
    """
    current_rollout_state = node.state
    while not current_rollout_state.stopped_round:
        available_actions = current_rollout_state.get_available_actions()
        if not available_actions:  # No more actions, game might be implicitly stopped
            break
        random_action = random.choice(available_actions)
        current_rollout_state = current_rollout_state.execute_action(random_action)

    return current_rollout_state.score


class ParallelMCTS(MCTS):
    def __init__(
        self,
        initial_game_state: GameState,
        c_param: float = math.sqrt(2),
        num_workers: int = None,
    ):
        super().__init__(initial_game_state, c_param)
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self._simulation_pool = None

    def run_parallel(
        self, num_simulations: int, batch_size: int = 100
    ) -> List[ResultAction]:
        """
        Runs the MCTS algorithm with parallel simulation for a specified number of simulations.
        Uses batched parallel processing to minimize overhead.
        """
        # Initialize multiprocessing pool if not already done
        if self._simulation_pool is None:
            logger.info(
                f"Initializing simulation pool with {self.num_workers} workers."
            )
            self._simulation_pool = multiprocessing.Pool(self.num_workers)

        for batch_start in range(0, num_simulations, batch_size):
            batch_end = min(batch_start + batch_size, num_simulations)
            batch_size_actual = batch_end - batch_start

            simulation_states = []
            nodes_to_update = []

            # Prepare batch of simulations
            for _ in range(batch_size_actual):
                # 1. Selection
                leaf_node = self._select()

                # 2. Expansion
                if not leaf_node.is_terminal_node():
                    node_to_simulate = self._expand(leaf_node)
                else:
                    node_to_simulate = leaf_node

                simulation_states.append(node_to_simulate.state)
                nodes_to_update.append(node_to_simulate)

            # 3. Parallel Simulation
            scores = self._simulation_pool.map(simulate_worker, simulation_states)

            # 4. Backpropagation
            for node, score in zip(nodes_to_update, scores):
                self._backpropagate(node, score)

        # After all simulations, choose the action from the root with the highest average score (Q/N)
        if not self.root.children:
            # If no simulations or no actions from root were expanded, return None or handle as error
            raise Exception("root does not have children")

        results = []
        if self.root.children:
            for action, child in self.root.children.items():
                if child.N > 0:  # Only consider actions that have been visited
                    avg_score = child.Q / child.N
                else:
                    avg_score = 0  # If not visited, consider its score as 0
                results.append(
                    ResultAction(
                        expected_score=avg_score, action=action, visit_count=child.N
                    )
                )
        return results

    def run_sequential(self, num_simulations: int) -> List[ResultAction]:
        """
        Runs the MCTS algorithm sequentially for comparison.
        """
        for _ in range(num_simulations):
            # 1. Selection
            leaf_node = self._select()

            # 2. Expansion (only if not a terminal node and not fully expanded)
            if not leaf_node.is_terminal_node():
                # If the leaf node is not fully expanded, expand one child.
                # If it is fully expanded (and not terminal), _select would have taken us deeper.
                # So if we reach here and it's not terminal, we must expand.
                node_to_simulate_from = self._expand(leaf_node)
            else:
                # If it's a terminal node, we simulate from itself (score is already final)
                node_to_simulate_from = leaf_node

            # 3. Simulation
            score = simulate_single(node_to_simulate_from)

            # 4. Backpropagation
            self._backpropagate(node_to_simulate_from, score)

        # After all simulations, choose the action from the root with the highest average score (Q/N)
        if not self.root.children:
            # If no simulations or no actions from root were expanded, return None or handle as error
            raise Exception("root does not have children")

        results = []
        if self.root.children:
            for action, child in self.root.children.items():
                if child.N > 0:  # Only consider actions that have been visited
                    avg_score = child.Q / child.N
                else:
                    avg_score = 0  # If not visited, consider its score as 0
                results.append(
                    ResultAction(
                        expected_score=avg_score, action=action, visit_count=child.N
                    )
                )
        return results

    def close(self):
        """Clean up the multiprocessing pool."""
        if self._simulation_pool is not None:
            self._simulation_pool.close()
            self._simulation_pool.join()
            self._simulation_pool = None
