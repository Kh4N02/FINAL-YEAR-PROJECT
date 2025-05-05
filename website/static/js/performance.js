async function fetchPerformanceData() {
    try {
        const response = await fetch('../../data/pakistan_t20_recent_20250213_032057.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        if (!data.players || data.players.length === 0) {
            throw new Error('No player data available');
        }
        
        console.log('Loaded players:', data.players); // Debug log
        
        displayAllRoundPerformances(data.players);
        displayBattingPerformances(data.players);
        displayBowlingPerformances(data.players);
    } catch (error) {
        console.error('Error fetching data:', error);
        displayError('Failed to load performance data. Please try again later.');
    }
}

function displayError(message) {
    const tables = ['#allround-stats', '#batting-stats', '#bowling-stats'];
    tables.forEach(tableId => {
        const tbody = document.querySelector(`${tableId} tbody`);
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-danger">
                    ${message}
                </td>
            </tr>
        `;
    });
}

function displayAllRoundPerformances(players) {
    const allRounders = players.filter(player => 
        player.batting.innings > 0 && player.bowling.innings > 0
    );
    
    const tbody = document.querySelector('#allround-stats tbody');
    tbody.innerHTML = allRounders.map(player => {
        const battingAvg = player.batting.innings > 0 
            ? (player.batting.runs / player.batting.innings).toFixed(2) 
            : 0;
        const strikeRate = player.batting.balls > 0 
            ? ((player.batting.runs / player.batting.balls) * 100).toFixed(2) 
            : 0;
        const economy = player.bowling.overs > 0 
            ? (player.bowling.runs / player.bowling.overs).toFixed(2) 
            : 0;
            
        return `
            <tr>
                <td>${player.name}</td>
                <td>${player.matches}</td>
                <td>${player.batting.runs}</td>
                <td>${battingAvg}</td>
                <td>${strikeRate}</td>
                <td>${player.bowling.wickets}</td>
                <td>${economy}</td>
                <td>${player.bowling.best}</td>
            </tr>
        `;
    }).join('');
}

function displayBattingPerformances(players) {
    const batsmen = players.filter(player => player.batting.innings > 0);
    
    const tbody = document.querySelector('#batting-stats tbody');
    tbody.innerHTML = batsmen.map(player => {
        const average = (player.batting.runs / player.batting.innings).toFixed(2);
        const strikeRate = player.batting.balls > 0 
            ? ((player.batting.runs / player.batting.balls) * 100).toFixed(2) 
            : 0;
            
        return `
            <tr>
                <td>${player.name}</td>
                <td>${player.matches}</td>
                <td>${player.batting.runs}</td>
                <td>${average}</td>
                <td>${strikeRate}</td>
                <td>${player.batting.highest}</td>
            </tr>
        `;
    }).join('');
}

function displayBowlingPerformances(players) {
    const bowlers = players.filter(player => player.bowling.innings > 0);
    
    const tbody = document.querySelector('#bowling-stats tbody');
    tbody.innerHTML = bowlers.map(player => {
        const economy = player.bowling.overs > 0 
            ? (player.bowling.runs / player.bowling.overs).toFixed(2) 
            : 0;
            
        return `
            <tr>
                <td>${player.name}</td>
                <td>${player.matches}</td>
                <td>${player.bowling.wickets}</td>
                <td>${economy}</td>
                <td>${player.bowling.best}</td>
            </tr>
        `;
    }).join('');
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', fetchPerformanceData); 