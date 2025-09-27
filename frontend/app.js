document.getElementById('simulations').addEventListener('input', function(e) {
    document.getElementById('sim-value').textContent = e.target.value;
});

document.getElementById('game-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const hand = document.getElementById('hand').value.split(',').map(Number);
    const diceThrowRaw = document.getElementById('dice_throw').value;
    const dice_throw = diceThrowRaw ? diceThrowRaw.split(',').map(Number) : null;
    const num_simulations = Number(document.getElementById('simulations').value);

    const response = await fetch('/api/run_mcts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hand, dice_throw, num_simulations })
    });
    const data = await response.json();
    const tbody = document.querySelector('#results-table tbody');
    tbody.innerHTML = '';
    data.actions.forEach(action => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${action.action}</td><td>${action.expected_score}</td><td>${action.visit_count}</td>`;
        tbody.appendChild(tr);
    });
});
