/**
 * API Service for communicating with Flask backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class ApiService {
    constructor() {
        this.baseURL = API_BASE_URL;
    }

    async healthCheck() {
        const response = await fetch(`${this.baseURL}/api/health`);
        return response.json();
    }

    async getPriceData(startDate = null, endDate = null) {
        let url = `${this.baseURL}/api/price`;
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        const response = await fetch(url);
        return response.json();
    }

    async getEvents(eventType = null, startDate = null, endDate = null) {
        let url = `${this.baseURL}/api/events`;
        const params = new URLSearchParams();
        
        if (eventType && eventType !== 'all') params.append('type', eventType);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        const response = await fetch(url);
        return response.json();
    }

    async getChangePoints() {
        const response = await fetch(`${this.baseURL}/api/change-points`);
        return response.json();
    }

    async getStatistics() {
        const response = await fetch(`${this.baseURL}/api/statistics`);
        return response.json();
    }

    async getVolatility() {
        const response = await fetch(`${this.baseURL}/api/volatility`);
        return response.json();
    }

    async getEventImpact(eventName) {
        const response = await fetch(`${this.baseURL}/api/event-impact/${encodeURIComponent(eventName)}`);
        return response.json();
    }

    async searchEvents(query) {
        const response = await fetch(`${this.baseURL}/api/search-events?q=${encodeURIComponent(query)}`);
        return response.json();
    }
}

export default new ApiService();