document.addEventListener('DOMContentLoaded', function() {
    let currentData;
    
    async function renderStats(data) {
        currentData = data;
        const teams = Object.keys(data.possession);
        const [team1, team2] = teams;
        
        //document.querySelector('.match-title').textContent = `${Math.round(data.start_time / 60)}' - ${Math.round(data.end_time / 60)}'`;
        
        const container = document.getElementById('stats-content');
        container.innerHTML = '';
        
        const statsToRender = [
            { key: 'possession', label: 'Possession', suffix: '%' },
            { key: 'shots', label: 'Shots' },
            { key: 'passes', label: 'Passes' },
            { key: 'pass_accuracy', label: 'Pass %', suffix: '%' },
            { key: 'fouls', label: 'Fouls' },
            { key: 'yellow_cards', label: 'Yellow Cards' },
            { key: 'red_cards', label: 'Red Cards' },
            { key: 'offsides', label: 'Offsides' },
            { key: 'corners', label: 'Corners' },
            { key: 'goals', label: 'Goals' }
        ];
        
        statsToRender.forEach(item => {
            const val1 = data[item.key][team1] || 0;
            const val2 = data[item.key][team2] || 0;
            const suffix = item.suffix || '';
            
            const badStats = ['fouls', 'yellow_cards', 'red_cards', 'offsides'];
            const isBadStat = badStats.includes(item.key);
            
            const class1 = isBadStat ? (val1 < val2 ? 'winner-bubble' : '') : (val1 > val2 ? 'winner-bubble' : '');
            const class2 = isBadStat ? (val2 < val1 ? 'winner-bubble' : '') : (val2 > val1 ? 'winner-bubble' : '');
            
            container.innerHTML += `
                <div class="stat-row">
                    <div class="stat-value ${class1}">${val1}${suffix}</div>
                    <div class="stat-label">${item.label}</div>
                    <div class="stat-value ${class2}">${val2}${suffix}</div>
                </div>
            `;
        });
        
        const heatmapImg = document.getElementById('heatmap-img');
        if (data.heatmap_b64) {
            heatmapImg.src = `data:image/png;base64,${data.heatmap_b64}`;
            heatmapImg.style.display = 'block';
        } else {
            heatmapImg.style.display = 'none';
        }
        
        const passNetworkImg = document.getElementById('pass-network-img');
        if (data.pass_network_b64) {
            passNetworkImg.src = `data:image/png;base64,${data.pass_network_b64}`;
            passNetworkImg.style.display = 'block';
        } else {
            passNetworkImg.style.display = 'none';
        }
    }
    
    async function loadMatchData(start = 0, end = 5400) {
        try {
            const params = new URLSearchParams({start, end});
            const response = await fetch(`/api/match-stats/?${params}`);
            const data = await response.json();
            renderStats(data);
        } catch (error) {
            console.error('Error:', error);
            document.getElementById('stats-content').innerHTML = '<p>Error loading stats.</p>';
        }
    }
    
    const startSlider = document.getElementById('start-slider');
    const endSlider = document.getElementById('end-slider');
    const updateBtn = document.getElementById('update-stats');
    
    if (startSlider && endSlider && updateBtn) {
        startSlider.oninput = () => {
            document.getElementById('start-label').textContent = `${Math.floor(startSlider.value)}'`;
        };
        endSlider.oninput = () => {
            document.getElementById('end-label').textContent = `${Math.floor(endSlider.value)}'`;
        };
        
        updateBtn.onclick = () => {
            const startSec = parseInt(startSlider.value) * 60;
            const endSec = parseInt(endSlider.value) * 60;
            loadMatchData(startSec, endSec);
        };
    }
    
    loadMatchData();
});
