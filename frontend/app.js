let chartInstance = null;
const COLORS = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'];

document.getElementById('simulations').addEventListener('input', function (e) {
    document.getElementById('sim-value').textContent = e.target.value;
});

document.getElementById('game-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    const handInput = document.getElementById('hand').value.trim();
    const hand = handInput ? handInput.split(',').map(Number) : [];

    const diceThrowRaw = document.getElementById('dice_throw').value.trim();
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

    // Prepare datasets for chart
    const datasets = [];

    data.actions.forEach((action, index) => {
        // Table row
        const tr = document.createElement('tr');
        // Format expected score to 3 decimals
        const score = typeof action.expected_score === 'number' ? action.expected_score.toFixed(3) : action.expected_score;
        tr.innerHTML = `<td>${action.action}</td><td>${score}</td><td>${action.visit_count}</td>`;
        tbody.appendChild(tr);

        // Chart dataset
        if (action.history && action.history.length > 0) {
            datasets.push({
                label: action.action,
                data: action.history.map(h => ({ x: h.simulations, y: h.expected_score })),
                borderColor: COLORS[index % COLORS.length],
                fill: false,
                tension: 0.1
            });
        }
    });

    renderChart(datasets);
});

function renderChart(datasets) {
    const ctx = document.getElementById('convergence-chart').getContext('2d');

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Simulations'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Expected Score'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Action Score Convergence'
                }
            }
        }
    });
}
