// Initialize and render chart for a binder
function initChart(canvas, binderName) {
    // Fetch binder data
    fetch(`/api/binder/${binderName}/data`)
        .then(response => response.json())
        .then(data => {
            renderChart(canvas, data);
        })
        .catch(error => console.error('Error fetching data for chart:', error));
}

// Render chart with the provided data
function renderChart(canvas, binderData) {
    const transactions = binderData.transactions || [];
    const categories = binderData.categories || {};
    
    if (transactions.length === 0) {
        // No transactions to display
        canvas.style.display = 'none';
        const noDataElement = document.createElement('div');
        noDataElement.className = 'alert alert-light text-center';
        noDataElement.textContent = 'Nessuna transazione da visualizzare';
        canvas.parentNode.appendChild(noDataElement);
        return;
    }
    
    // Group transactions by category
    const categoriesData = {};
    const categoryColors = {};
    
    // Initialize categories
    Object.keys(categories).forEach(category => {
        categoriesData[category] = 0;
        categoryColors[category] = categories[category].color || '#6c757d';
    });
    
    // Sum amounts by category
    transactions.forEach(transaction => {
        const category = transaction.category;
        if (category && typeof transaction.amount === 'number') {
            if (!categoriesData[category]) {
                categoriesData[category] = 0;
            }
            categoriesData[category] += transaction.amount;
        }
    });
    
    // Prepare chart data
    const chartLabels = Object.keys(categoriesData);
    const chartData = Object.values(categoriesData);
    const chartColors = chartLabels.map(category => categoryColors[category] || '#6c757d');
    
    // Create the chart
    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Importo',
                data: chartData,
                backgroundColor: chartColors,
                borderColor: chartColors.map(color => adjustColor(color, -20)),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + ' €';
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.raw.toFixed(2) + ' €';
                        }
                    }
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

// Helper function to adjust color brightness
function adjustColor(color, amount) {
    let usePound = false;
    
    if (color[0] === '#') {
        color = color.slice(1);
        usePound = true;
    }
    
    const num = parseInt(color, 16);
    
    let r = (num >> 16) + amount;
    r = Math.max(Math.min(255, r), 0);
    
    let g = ((num >> 8) & 0x00FF) + amount;
    g = Math.max(Math.min(255, g), 0);
    
    let b = (num & 0x0000FF) + amount;
    b = Math.max(Math.min(255, b), 0);
    
    return (usePound ? '#' : '') + (g | (r << 8) | (b << 16)).toString(16).padStart(6, '0');
}
