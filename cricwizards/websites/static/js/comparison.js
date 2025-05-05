document.addEventListener('DOMContentLoaded', function() {
    const player1Select = document.getElementById('player1-select');
    const player2Select = document.getElementById('player2-select');
    const comparisonResults = document.getElementById('comparison-results');
    
    function updateComparison() {
        const player1 = player1Select.value;
        const player2 = player2Select.value;
        
        if (!player1 || !player2) {
            comparisonResults.classList.add('d-none');
            return;
        }
        
        // Show loading state
        comparisonResults.classList.remove('d-none');
        
        // Fetch comparison data
        fetch(`/get_player_comparison?team_id=1&player1=${player1}&player2=${player2}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                
                // Update Player 1 stats
                document.getElementById('player1-name').textContent = data.player1.name;
                document.getElementById('player1-runs').textContent = data.player1.batting.runs;
                document.getElementById('player1-avg').textContent = data.player1.batting.average;
                document.getElementById('player1-sr').textContent = data.player1.batting.strike_rate;
                document.getElementById('player1-wkts').textContent = data.player1.bowling.wickets;
                document.getElementById('player1-econ').textContent = data.player1.bowling.economy;
                document.getElementById('player1-bowl-avg').textContent = data.player1.bowling.average;
                
                // Update Player 2 stats
                document.getElementById('player2-name').textContent = data.player2.name;
                document.getElementById('player2-runs').textContent = data.player2.batting.runs;
                document.getElementById('player2-avg').textContent = data.player2.batting.average;
                document.getElementById('player2-sr').textContent = data.player2.batting.strike_rate;
                document.getElementById('player2-wkts').textContent = data.player2.bowling.wickets;
                document.getElementById('player2-econ').textContent = data.player2.bowling.economy;
                document.getElementById('player2-bowl-avg').textContent = data.player2.bowling.average;
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Failed to load comparison data');
            });
    }
    
    player1Select.addEventListener('change', updateComparison);
    player2Select.addEventListener('change', updateComparison);
}); 