from src.game import Action, GameState
from src.tree import MCTS


# Helper to create a state that leads to a terminal state
class TerminalTestGameState(GameState):
    def __init__(self, hand=None, dice_throw=None, score=0, stopped_round=False):
        if hand is None:
            hand = []
        super().__init__(hand, dice_throw, score)
        self.stopped_round = stopped_round

    def get_available_actions(self):
        if self.stopped_round:
            return []
        # Return a STOP action that makes it terminal
        return [Action(Action.STOP)]

    def execute_action(self, action):
        if action.name == Action.STOP:
            # Return a terminal state
            return TerminalTestGameState(
                hand=self.hand, score=self.score, stopped_round=True
            )
        return self


def test_terminal_node_visits():
    """
    Test that MCTS visits terminal nodes and they accumulate visit counts (N).
    """
    # Create a state where the only action is STOP, which leads to a terminal state
    state = TerminalTestGameState(hand=[6] * 8, score=40)

    mcts = MCTS(state)
    simulations = 50
    mcts.run(num_simulations=simulations)

    root = mcts.root

    # We expect the root to have 1 child (STOP)
    assert len(root.children) == 1
    stop_action = Action(Action.STOP)
    assert stop_action in root.children

    child = root.children[stop_action]
    assert child.is_terminal_node()

    # The child should have been visited roughly the same amount as the root (minus maybe 1 for initial expansion)
    # The previous bug prevented the child from being selected, so N would be 1.
    # With the fix, N should be close to simulations (e.g. 50).
    print(f"Root N: {root.N}, Child N: {child.N}")
    assert child.N > 1, "Terminal child node should be visited more than once"
    assert (
        child.N >= simulations - 1
    ), "Terminal child node should capture almost all visits"
