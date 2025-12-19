import math
import random
from collections import defaultdict
from typing import Dict, List, TypedDict

from .game import Action, GameState


class HistoryPoint(TypedDict):
    simulations: int
    expected_score: float


class ResultAction(TypedDict):
    expected_score: float
    action: Action
    visit_count: int
    history: List[HistoryPoint]


class Node:
    def __init__(
        self, state: GameState, parent: "Node" = None, action_taken: Action = None
    ):
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        self.children = {}  # type: dict[Action, Node]
        self.N = 0  # Visit count
        self.Q = 0.0  # Total score

        # A copy of available actions to track which ones have been expanded
        self.unvisited_actions = list(state.get_available_actions())

    def is_fully_expanded(self) -> bool:
        """Checks if all available actions from this node have been expanded."""
        return len(self.unvisited_actions) == 0

    def is_terminal_node(self) -> bool:
        """Checks if the game state at this node is a terminal state."""
        return self.state.stopped_round

    def __repr__(self):
        return f"Node(Q={self.Q:.2f}, N={self.N}, Actions Left={len(self.unvisited_actions)})"


class MCTS:
    def __init__(self, initial_game_state: GameState, c_param: float = math.sqrt(2)):
        self.root = Node(initial_game_state)
        self.c_param = c_param

    def _select(self) -> Node:
        """
        Selection phase: Traverse the tree to find a node to expand or simulate from.
        Uses UCB1 formula to balance exploration and exploitation.
        """
        current_node = self.root

        # If the current node is not fully expanded, return it for expansion
        while current_node.is_fully_expanded() and not current_node.is_terminal_node():
            best_ucb = -float("inf")
            best_child = None

            for action, child in current_node.children.items():
                if child.is_terminal_node():
                    continue

                # UCB1 formula: Q/N + c * sqrt(ln(Parent_N) / N)
                if child.N == 0:
                    ucb = float(
                        "inf"
                    )  # Prioritize unvisited children for immediate exploration
                else:
                    ucb = (child.Q / child.N) + self.c_param * math.sqrt(
                        math.log(current_node.N) / child.N
                    )

                if ucb > best_ucb:
                    best_ucb = ucb
                    best_child = child
            if best_child is None:
                return current_node  # No valid child found, return current node
            current_node = best_child
        # If the root is not fully expanded, always return it for expansion
        return current_node

    def _expand(self, node: Node) -> Node:
        """
        Expansion phase: Create a new child node for an unvisited action.
        """
        if node.is_terminal_node() or node.is_fully_expanded():
            # If the node is terminal or fully expanded, expansion is not possible/needed.
            return node

        # Choose a random unvisited action to expand
        action = random.choice(node.unvisited_actions)
        node.unvisited_actions.remove(action)

        new_state = node.state.execute_action(action)
        new_child = Node(new_state, parent=node, action_taken=action)
        node.children[action] = new_child
        return new_child

    def _simulate(self, node: Node) -> float:
        """
        Simulation (Rollout) phase: Play out a random game from the given node's state
        until a terminal state is reached, and return the final score.
        """
        current_rollout_state = node.state
        while not current_rollout_state.stopped_round:
            available_actions = current_rollout_state.get_available_actions()
            if (
                not available_actions
            ):  # No more actions, game might be implicitly stopped
                break
            random_action = random.choice(available_actions)
            current_rollout_state = current_rollout_state.execute_action(random_action)

        return current_rollout_state.score

    def _backpropagate(self, node: Node, score: float):
        """
        Backpropagation phase: Update visit counts and total scores for all nodes
        on the path from the simulated node up to the root.
        """
        current_node = node
        while current_node is not None:
            current_node.N += 1
            current_node.Q += score
            current_node = current_node.parent

    def run(
        self, num_simulations: int, monitor_interval: int = 100
    ) -> List[ResultAction]:
        """
        Runs the MCTS algorithm for a specified number of simulations
        and returns the best action from the root.
        """
        history_log: Dict[Action, List[HistoryPoint]] = defaultdict(list)

        for i in range(1, num_simulations + 1):
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
            score = self._simulate(node_to_simulate_from)

            # 4. Backpropagation
            self._backpropagate(node_to_simulate_from, score)

            # Track history periodically
            if i % monitor_interval == 0:
                for action, child in self.root.children.items():
                    if child.N > 0:
                        avg_score = child.Q / child.N
                        history_log[action].append(
                            {"simulations": i, "expected_score": avg_score}
                        )

        # After all simulations, choose the action from the root with the highest average score (Q/N)
        # This is a common strategy, sometimes referred to as 'greedy' choice at the end.
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

                # Retrieve history for this action
                action_history = history_log.get(action, [])

                results.append(
                    ResultAction(
                        expected_score=avg_score,
                        action=action,
                        visit_count=child.N,
                        history=action_history,
                    )
                )
        return results
