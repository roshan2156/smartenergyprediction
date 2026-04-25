class Utils {
    static formatDate(date) {
        return new Date(date).toLocaleString();
    }

    static formatDateShort(date) {
        return new Date(date).toLocaleDateString();
    }

    static formatTime(date) {
        return new Date(date).toLocaleTimeString();
    }

    static formatCurrency(amount) {
        return `₹${parseFloat(amount).toFixed(2)}`;
    }

    static formatEnergy(energy) {
        return `${parseFloat(energy).toFixed(2)} kWh`;
    }

    static formatCarbon(carbon) {
        return `${parseFloat(carbon).toFixed(2)} kg`;
    }

    static formatNumber(num, decimals = 2) {
        return parseFloat(num).toFixed(decimals);
    }

    static getEfficiencyScore(energy, maxEnergy = 10) {
        const score = Math.max(0, Math.min(100, 100 - (energy / maxEnergy) * 100));
        return Math.round(score);
    }

    static getEfficiencyColor(score) {
        if (score >= 80) return 'success';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    static getPeakHourStatus(hour) {
        if (hour >= 19 && hour <= 22) {
            return { isPeak: true, message: '⚠️ Peak Hour (7-10 PM)', color: 'warning' };
        }
        return { isPeak: false, message: '✅ Off-Peak Hour', color: 'success' };
    }

    static downloadCSV(data, filename) {
        const csv = this.convertToCSV(data);
        const blob = new Blob(["\uFEFF" + csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    static convertToCSV(data) {
        if (!data || data.length === 0) return '';
        const headers = Object.keys(data[0]);
        const rows = data.map(obj => headers.map(header => {
            let value = obj[header] || '';
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                value = `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(','));
        return [headers.join(','), ...rows].join('\n');
    }

    static showToast(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, { delay: duration });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => toast.remove());
    }

    static showLoading(show = true) {
        let loader = document.getElementById('globalLoader');
        if (show) {
            if (!loader) {
                loader = document.createElement('div');
                loader.id = 'globalLoader';
                loader.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.7);
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                `;
                loader.innerHTML = `
                    <div class="text-center">
                        <div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p class="text-white mt-2">Processing...</p>
                    </div>
                `;
                document.body.appendChild(loader);
            } else {
                loader.style.display = 'flex';
            }
        } else {
            if (loader) loader.style.display = 'none';
        }
    }

    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            this.showToast('Failed to copy', 'danger');
        });
    }

    static getCurrentDateTime() {
        return new Date().toISOString();
    }

    static truncate(str, length = 50) {
        if (str.length <= length) return str;
        return str.substring(0, length) + '...';
    }

    static groupBy(array, key) {
        return array.reduce((result, item) => {
            const groupKey = item[key];
            if (!result[groupKey]) result[groupKey] = [];
            result[groupKey].push(item);
            return result;
        }, {});
    }

    static calculateTotalEnergy(predictions) {
        return predictions.reduce((sum, p) => sum + (parseFloat(p.energy) || 0), 0);
    }

    static calculateTotalCost(predictions) {
        return predictions.reduce((sum, p) => sum + (parseFloat(p.cost) || 0), 0);
    }

    static calculateTotalCarbon(predictions) {
        return predictions.reduce((sum, p) => sum + (parseFloat(p.carbon) || 0), 0);
    }
}

const utils = Utils;