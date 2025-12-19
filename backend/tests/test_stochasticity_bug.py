from src.game import GameState
from src.tree import MCTS, Action


def test_roll_determinism_bug():
    """
    This test demonstrates that the current MCTS implementation incorrectly caches
    the result of a stochastic ROLL action.

    Expected behavior (in a correct MCTS for stochastic games):
    - Expanding 'ROLL' multiple times (or simulating it) should result in different game states
      (different dice throws) effectively or branch into chance nodes.

    Current behavior (Bug):
    - The 'ROLL' action is treated as a standard action.
    - Once expanded, the resulting child node (with a specific random dice throw) is stored in `node.children`.
    - All subsequent visits to 'ROLL' go to this EXACT same child node.
    - The AI effectively solves a deterministic game where the dice rolls are pre-seeded by the first visit.
    """
    # Start with an empty hand, so ROLL is legal
    state = GameState(hand=[])
    mcts = MCTS(state)

    # Run simulations to force expansion of ROLL
    mcts.run(num_simulations=10)

    root = mcts.root
    roll_action = Action(Action.ROLL)

    assert roll_action in root.children, "ROLL should have been expanded"
    child_node_1 = root.children[roll_action]
    dice_throw_1 = child_node_1.state.dice_throw
    print(f"First ROLL outcome: {dice_throw_1}")

    # Run MANY more simulations.
    # In a correct implementation (Open Loop or Chance Nodes), we should re-evaluate ROLL
    # and potentially see different outcomes mixed in, or at least different paths.
    # But here we check if the child node remains the singleton authority.
    mcts.run(num_simulations=100)

    child_node_2 = root.children[roll_action]
    dice_throw_2 = child_node_2.state.dice_throw
    print(f"Second ROLL outcome: {dice_throw_2}")

    # Verify that it is the SAME object/outcome
    assert child_node_1 is child_node_2
    assert dice_throw_1 == dice_throw_2

    print("Confirmed: The MCTS is reusing the cached stochastic outcome.")
