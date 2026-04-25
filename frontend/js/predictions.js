class PredictionEngine {
    constructor() {
        this.apiUrl = 'http://localhost:5000/api';
    }

    async predictFromManualInput(formData, mode = 'manual') {
        const user = authManager.getCurrentUser();
        
        // ✅ FIX 1: ADD THIS CHECK FIRST
        if (!user || !user.id) {
            console.error("❌ No user logged in or invalid user ID");
            alert("❌ Please login first to make predictions!");
            window.location.href = 'login.html';
            return { success: false, error: "User not logged in" };
        }
        
        console.log("👤 Current User:", user);
        console.log("👤 User ID:", user.id, "Type:", typeof user.id);

        const currentHour = new Date().getHours();
        
        // ✅ STEP 1: GET FORECAST PERIOD FIRST
        let period = 1;
        document.querySelectorAll('.forecast-btn').forEach(btn => {
            if (btn.classList.contains('active')) {
                const text = btn.innerText;
                if (text.includes("7")) period = 7;
                else if (text.includes("30")) period = 30;
                else if (text.includes("Year")) period = 365;
                else period = 1;
            }
        });

        // ✅ STEP 2: CREATE inputData WITH EXPLICIT INTEGER user_id
        const inputData = {
            user_id: parseInt(user.id),  // ✅ FORCE INTEGER
            user_name: user.name,
            mode: mode,
            forecast_period: period,
            power_consumption_W: parseFloat(formData.power),
            usage_duration_minutes: parseFloat(formData.duration),
            appliance: formData.appliance,
            occupancy_status: formData.occupancy,
            temperature_setting_C: parseFloat(formData.temperature),
            hour: currentHour,
            room_location: formData.room,
            day_of_week: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date().getDay()],
            season: this.getSeason(),
            holiday: 'No',
            device_status: 'ON',
            appliance_category: this.getApplianceCategory(formData.appliance),
            appliance_type: this.getApplianceType(formData.appliance),
            voltage: 230,
            current: parseFloat(formData.power) / 230,
            appliance_count: 1
        };
        
        console.log("📤 Sending prediction data:", JSON.stringify(inputData, null, 2));
        
        try {
            const response = await fetch(`${this.apiUrl}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(inputData)
            });
            
            const result = await response.json();
            console.log("📥 Prediction response:", result);
            
            if (result.success) {
                this.saveToLocalHistory(result, formData, mode);
            }
            return result;
        } catch (error) {
            console.error('Prediction error:', error);
            return { success: false, error: "Prediction failed: " + error.message };
        }
    }

    async predictFromCSV(csvData, mode = 'csv') {
        const user = authManager.getCurrentUser();
        const records = [];
        
        for (let row of csvData) {
            records.push({
                power_consumption_W: parseFloat(row.power_consumption_W),
                usage_duration_minutes: parseFloat(row.usage_duration_minutes),
                appliance: row.appliance,
                occupancy_status: row.occupancy_status,
                temperature_setting_C: parseFloat(row.temperature_setting_C),
                hour: new Date(row.timestamp).getHours(),
                room_location: row.room_location || 'Living Room',
                day_of_week: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][new Date(row.timestamp).getDay()],
                season: this.getSeasonFromDate(row.timestamp),
                appliance_category: this.getApplianceCategory(row.appliance),
                appliance_type: this.getApplianceType(row.appliance)
            });
        }
        
        try {
            const response = await fetch(`${this.apiUrl}/batch_predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: user ? parseInt(user.id) : 'guest',
                    user_name: user ? user.name : 'Guest User',
                    mode: mode,
                    records: records
                })
            });
            return await response.json();
        } catch (error) {
            console.error('Batch prediction error:', error);
            return { success: false, error: error.message };
        }
    }

    saveToLocalHistory(result, formData, mode) {
        const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
        history.unshift({
            id: Date.now(),
            mode: mode,
            timestamp: new Date().toISOString(),
            energy: result.energy,
            cost: result.cost,
            carbon: result.carbon,
            is_peak_hour: result.is_peak_hour,
            waste_detected: result.waste_detected,
            appliance: formData.appliance,
            duration: formData.duration,
            power: formData.power
        });
        if (history.length > 50) history.pop();
        localStorage.setItem('predictionHistory', JSON.stringify(history));
    }

    async getDashboardStats() {
        const user = authManager.getCurrentUser();
        try {
            const response = await fetch(`${this.apiUrl}/dashboard_stats?user_id=${user ? user.id : 'guest'}`);
            return await response.json();
        } catch (error) {
            console.error('Stats error:', error);
            const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
            if (history.length === 0) {
                return { success: true, stats: { total_energy: 0, total_cost: 0, total_carbon: 0, alert_count: 0, waste_count: 0, efficiency_score: 85, total_predictions: 0 } };
            }
            const totalEnergy = history.reduce((sum, p) => sum + p.energy, 0);
            const totalCost = history.reduce((sum, p) => sum + p.cost, 0);
            const totalCarbon = history.reduce((sum, p) => sum + p.carbon, 0);
            const wasteCount = history.filter(p => p.waste_detected).length;
            const avgEnergy = totalEnergy / history.length;
            const efficiencyScore = Math.max(0, Math.min(100, 100 - (avgEnergy * 2)));
            
            return {
                success: true,
                stats: {
                    total_energy: totalEnergy,
                    total_cost: totalCost,
                    total_carbon: totalCarbon,
                    alert_count: history.filter(p => p.is_peak_hour).length,
                    waste_count: wasteCount,
                    efficiency_score: Math.round(efficiencyScore),
                    total_predictions: history.length
                }
            };
        }
    }

    async getHistory() {
        const user = authManager.getCurrentUser();
        try {
            const response = await fetch(`${this.apiUrl}/history?user_id=${user ? user.id : 'guest'}`);
            return await response.json();
        } catch (error) {
            console.error('History error:', error);
            const history = JSON.parse(localStorage.getItem('predictionHistory') || '[]');
            return { success: true, predictions: history };
        }
    }

    fallbackPrediction(formData) {
        const power = parseFloat(formData.power);
        const hours = parseFloat(formData.duration) / 60;
        let energy = (power * hours) / 1000;
        
        const currentHour = new Date().getHours();
        const isPeakHour = currentHour >= 19 && currentHour <= 22;
        
        return {
            success: true,
            energy: parseFloat(energy.toFixed(3)),
            cost: parseFloat((energy * 7).toFixed(2)),
            carbon: parseFloat((energy * 0.82).toFixed(3)),
            is_peak_hour: isPeakHour,
            waste_detected: formData.occupancy === 'Vacant' && energy > 0.5,
            alerts: energy > 5 ? ['⚠️ High energy consumption detected'] : [],
            recommendations: this.getRecommendations(formData.appliance, energy),
            message: `Predicted energy: ${energy.toFixed(2)} kWh`
        };
    }

    getRecommendations(appliance, energy) {
        const recs = [];
        if (appliance === 'AC') recs.push('❄️ Set AC to 24°C and use timer mode');
        if (energy > 5) recs.push('💰 Reduce energy by 20% to save money');
        recs.push('🔌 Unplug electronics when not in use');
        recs.push('💡 Replace bulbs with LEDs');
        return recs;
    }

    getSeason() {
        const month = new Date().getMonth();
        if (month >= 2 && month <= 4) return 'Spring';
        if (month >= 5 && month <= 7) return 'Summer';
        if (month >= 8 && month <= 10) return 'Autumn';
        return 'Winter';
    }

    getSeasonFromDate(dateString) {
        const date = new Date(dateString);
        const month = date.getMonth();
        if (month >= 2 && month <= 4) return 'Spring';
        if (month >= 5 && month <= 7) return 'Summer';
        if (month >= 8 && month <= 10) return 'Autumn';
        return 'Winter';
    }

    getApplianceCategory(appliance) {
        const categories = {
            'AC': 'High', 'Heater': 'High', 'Water Heater': 'High',
            'Washing Machine': 'Medium', 'Fridge': 'Medium', 'Microwave': 'Medium',
            'Fan': 'Low', 'Light': 'Low', 'TV': 'Low', 'Computer': 'Low'
        };
        return categories[appliance] || 'Medium';
    }

    getApplianceType(appliance) {
        const types = {
            'AC': 'Cooling', 'Heater': 'Heating', 'Water Heater': 'Heating',
            'Washing Machine': 'Laundry', 'Fridge': 'Cooling', 'Microwave': 'Cooking',
            'Fan': 'Ventilation', 'Light': 'Lighting', 'TV': 'Entertainment', 'Computer': 'Work'
        };
        return types[appliance] || 'General';
    }
}

const predictionEngine = new PredictionEngine();