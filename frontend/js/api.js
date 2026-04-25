const API_BASE_URL = 'http://localhost:5000/api';

class EnergyAPI {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async predict(inputData) {
        try {
            const response = await fetch(`${this.baseUrl}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(inputData)
            });
            const result = await response.json();
            return result;
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    }

    async batchPredict(records, userId, userName, mode = 'csv') {
        try {
            const response = await fetch(`${this.baseUrl}/batch_predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: userId,
                    user_name: userName,
                    mode: mode,
                    records: records
                })
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, error: error.message };
        }
    }

    async getHistory(userId) {
        try {
            const response = await fetch(`${this.baseUrl}/history?user_id=${userId}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { success: false, predictions: [] };
        }
    }

    async getDashboardStats(userId) {
        try {
            const response = await fetch(`${this.baseUrl}/dashboard_stats?user_id=${userId}`);
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { success: false };
        }
    }

    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            return await response.json();
        } catch (error) {
            return { status: 'offline' };
        }
    }

    async exportPredictions(userId) {
        try {
            const response = await fetch(`${this.baseUrl}/export_predictions?user_id=${userId}`);
            return await response.json();
        } catch (error) {
            console.error('Export Error:', error);
            return { success: false };
        }
    }
}

const energyAPI = new EnergyAPI();