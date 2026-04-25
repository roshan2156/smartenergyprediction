class ChartManager {
    constructor() {
        this.charts = {};
    }

    createDailyTrendChart(canvasId, data = null, labels = null) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        
        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Energy (kWh)',
                    data: data || [42, 38, 45, 52, 58, 65, 48],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46,204,113,0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.raw} kWh`;
                            }
                        }
                    }
                }
            }
        });
    }

    createApplianceChart(canvasId, data = null, labels = null) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        
        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels || ['AC', 'Fridge', 'Washing Machine', 'Fan', 'Light', 'TV', 'Heater'],
                datasets: [{
                    data: data || [42, 18, 12, 10, 8, 6, 4],
                    backgroundColor: ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#e67e22'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { position: 'bottom' },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.raw} kWh`;
                            }
                        }
                    }
                }
            }
        });
    }

    createPeakHourChart(canvasId, data = null) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        
        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['12AM-4AM', '4AM-8AM', '8AM-12PM', '12PM-4PM', '4PM-8PM', '8PM-12AM'],
                datasets: [{
                    label: 'Energy (kWh)',
                    data: data || [15, 12, 28, 35, 42, 58],
                    backgroundColor: '#f39c12',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Energy (kWh)' }
                    }
                }
            }
        });
    }

    createMonthlyChart(canvasId, data = null) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        
        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Energy (kWh)',
                    data: data || [320, 340, 380, 420, 480, 520, 550, 540, 490, 440, 380, 340],
                    backgroundColor: '#3498db',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    }

    createPredictionChart(canvasId, data = null, confidenceData = null) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return;
        
        if (this.charts[canvasId]) this.charts[canvasId].destroy();
        
        const datasets = [{
            label: 'Predicted Energy (kWh)',
            data: data || [42, 44, 46, 48, 45, 43, 41],
            borderColor: '#9b59b6',
            backgroundColor: 'rgba(155,89,182,0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true
        }];
        
        if (confidenceData) {
            datasets.push({
                label: 'Confidence Interval',
                data: confidenceData,
                borderColor: 'rgba(155,89,182,0.3)',
                backgroundColor: 'rgba(155,89,182,0.05)',
                borderWidth: 1,
                borderDash: [5, 5],
                fill: false
            });
        }
        
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'],
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw} kWh`;
                            }
                        }
                    }
                }
            }
        });
    }

    updateChart(canvasId, newData) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].data.datasets[0].data = newData;
            this.charts[canvasId].update();
        }
    }
}

const chartManager = new ChartManager();