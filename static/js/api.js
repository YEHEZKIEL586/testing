/**
 * API Communication Module
 * Handles all API requests with proper error handling, loading states, and response processing
 */

class APIClient {
    constructor() {
        this.baseURL = '';
        this.defaultHeaders = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
        this.requestInterceptors = [];
        this.responseInterceptors = [];
        this.init();
    }

    init() {
        // Add default response interceptor for error handling
        this.addResponseInterceptor(
            (response) => response,
            (error) => this.handleGlobalError(error)
        );
    }

    // Request interceptors
    addRequestInterceptor(onFulfilled, onRejected) {
        this.requestInterceptors.push({ onFulfilled, onRejected });
    }

    // Response interceptors
    addResponseInterceptor(onFulfilled, onRejected) {
        this.responseInterceptors.push({ onFulfilled, onRejected });
    }

    // Apply request interceptors
    async applyRequestInterceptors(config) {
        for (const interceptor of this.requestInterceptors) {
            try {
                if (interceptor.onFulfilled) {
                    config = await interceptor.onFulfilled(config);
                }
            } catch (error) {
                if (interceptor.onRejected) {
                    return interceptor.onRejected(error);
                }
                throw error;
            }
        }
        return config;
    }

    // Apply response interceptors
    async applyResponseInterceptors(response) {
        for (const interceptor of this.responseInterceptors) {
            try {
                if (interceptor.onFulfilled) {
                    response = await interceptor.onFulfilled(response);
                }
            } catch (error) {
                if (interceptor.onRejected) {
                    return interceptor.onRejected(error);
                }
                throw error;
            }
        }
        return response;
    }

    // Core request method
    async request(url, options = {}) {
        try {
            // Prepare request config
            let config = {
                url: this.baseURL + url,
                method: options.method || 'GET',
                headers: { ...this.defaultHeaders, ...options.headers },
                ...options
            };

            // Apply request interceptors
            config = await this.applyRequestInterceptors(config);

            // Make the request
            const response = await fetch(config.url, {
                method: config.method,
                headers: config.headers,
                body: config.body,
                credentials: 'same-origin',
                ...config
            });

            // Process response
            let processedResponse = await this.processResponse(response);
            
            // Apply response interceptors
            processedResponse = await this.applyResponseInterceptors(processedResponse);

            return processedResponse;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    // Process response
    async processResponse(response) {
        const contentType = response.headers.get('content-type');
        let data;

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const error = new Error(data.message || `HTTP ${response.status}: ${response.statusText}`);
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return {
            data,
            status: response.status,
            statusText: response.statusText,
            headers: response.headers
        };
    }

    // HTTP Methods
    async get(url, params = {}, options = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${url}?${queryString}` : url;
        
        return this.request(fullUrl, {
            method: 'GET',
            ...options
        });
    }

    async post(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: data instanceof FormData ? data : JSON.stringify(data),
            headers: data instanceof FormData ? {} : undefined,
            ...options
        });
    }

    async put(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'PUT',
            body: data instanceof FormData ? data : JSON.stringify(data),
            headers: data instanceof FormData ? {} : undefined,
            ...options
        });
    }

    async patch(url, data = {}, options = {}) {
        return this.request(url, {
            method: 'PATCH',
            body: data instanceof FormData ? data : JSON.stringify(data),
            headers: data instanceof FormData ? {} : undefined,
            ...options
        });
    }

    async delete(url, options = {}) {
        return this.request(url, {
            method: 'DELETE',
            ...options
        });
    }

    // File upload
    async upload(url, file, additionalData = {}, onProgress = null) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        const options = {
            method: 'POST',
            body: formData,
            headers: {} // Let browser set content-type for FormData
        };

        // Add progress tracking if supported
        if (onProgress && typeof onProgress === 'function') {
            // Note: Fetch API doesn't support upload progress natively
            // This would require XMLHttpRequest for progress tracking
            return this.uploadWithProgress(url, formData, onProgress);
        }

        return this.request(url, options);
    }

    // Upload with progress (using XMLHttpRequest)
    uploadWithProgress(url, formData, onProgress) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    onProgress(percentComplete, e.loaded, e.total);
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve({ data: response, status: xhr.status });
                    } catch (error) {
                        resolve({ data: xhr.responseText, status: xhr.status });
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Upload failed: Network error'));
            });

            xhr.open('POST', this.baseURL + url);
            
            // Add default headers (except Content-Type for FormData)
            Object.keys(this.defaultHeaders).forEach(key => {
                if (key !== 'Content-Type') {
                    xhr.setRequestHeader(key, this.defaultHeaders[key]);
                }
            });

            xhr.send(formData);
        });
    }

    // Global error handler
    handleGlobalError(error) {
        console.error('Global API Error:', error);
        
        // Show user-friendly error messages
        if (error.status === 401) {
            window.showToast('Authentication Error', 'Please log in again', 'error');
        } else if (error.status === 403) {
            window.showToast('Permission Error', 'You don\'t have permission to perform this action', 'error');
        } else if (error.status === 404) {
            window.showToast('Not Found', 'The requested resource was not found', 'error');
        } else if (error.status === 429) {
            window.showToast('Rate Limited', 'Too many requests. Please try again later', 'warning');
        } else if (error.status >= 500) {
            window.showToast('Server Error', 'Something went wrong on our end. Please try again', 'error');
        } else if (!navigator.onLine) {
            window.showToast('Network Error', 'Please check your internet connection', 'error');
        }

        throw error;
    }

    // Retry mechanism
    async retryRequest(requestFn, maxRetries = 3, delay = 1000) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await requestFn();
            } catch (error) {
                if (attempt === maxRetries) {
                    throw error;
                }
                
                // Exponential backoff
                const waitTime = delay * Math.pow(2, attempt - 1);
                await this.sleep(waitTime);
            }
        }
    }

    // Utility method for delays
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Batch requests
    async batch(requests) {
        try {
            const promises = requests.map(request => {
                const { url, method = 'GET', data, options = {} } = request;
                return this.request(url, { method, body: data, ...options });
            });

            const results = await Promise.allSettled(promises);
            
            return results.map((result, index) => ({
                request: requests[index],
                success: result.status === 'fulfilled',
                data: result.status === 'fulfilled' ? result.value.data : null,
                error: result.status === 'rejected' ? result.reason : null
            }));
        } catch (error) {
            console.error('Batch request error:', error);
            throw error;
        }
    }

    // Cancel request (using AbortController)
    createCancelToken() {
        return new AbortController();
    }

    // Request with timeout
    async requestWithTimeout(url, options = {}, timeout = 30000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await this.request(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
}

// API Endpoints
class SocialMediaAPI extends APIClient {
    constructor() {
        super();
        this.endpoints = {
            // Dashboard
            dashboard: {
                stats: '/api/dashboard/stats',
                activity: '/api/dashboard/activity'
            },
            
            // Accounts
            accounts: {
                list: '/api/accounts',
                create: '/api/accounts',
                get: (id) => `/api/accounts/${id}`,
                update: (id) => `/api/accounts/${id}`,
                delete: (id) => `/api/accounts/${id}`,
                test: (id) => `/api/accounts/${id}/test`,
                reauth: (id) => `/api/accounts/${id}/reauth`
            },
            
            // Guest Sites
            guestSites: {
                list: '/api/guest-sites',
                create: '/api/guest-sites',
                get: (id) => `/api/guest-sites/${id}`,
                update: (id) => `/api/guest-sites/${id}`,
                delete: (id) => `/api/guest-sites/${id}`,
                test: '/api/guest-sites/test',
                bulkTest: '/api/guest-sites/bulk-test'
            },
            
            // Posts
            posts: {
                list: '/api/posts',
                create: '/api/posts',
                get: (id) => `/api/posts/${id}`,
                update: (id) => `/api/posts/${id}`,
                delete: (id) => `/api/posts/${id}`,
                publish: (id) => `/api/posts/${id}/publish`,
                schedule: (id) => `/api/posts/${id}/schedule`
            },
            
            // Content
            content: {
                list: '/api/content',
                create: '/api/content',
                generate: '/api/content/generate',
                improve: '/api/content/improve',
                scrape: '/api/content/scrape'
            },
            
            // Automation
            automation: {
                status: '/api/automation/status',
                start: '/api/automation/start',
                stop: '/api/automation/stop',
                schedules: '/api/automation/schedules',
                logs: '/api/automation/logs'
            },
            
            // Notifications
            notifications: {
                list: '/api/notifications',
                create: '/api/notifications',
                markRead: (id) => `/api/notifications/${id}/read`,
                markAllRead: '/api/notifications/mark-all-read',
                new: '/api/notifications/new'
            },
            
            // Settings
            settings: {
                get: '/api/settings',
                update: '/api/settings',
                export: '/api/settings/export',
                import: '/api/settings/import'
            }
        };
    }

    // Dashboard methods
    async getDashboardStats() {
        const response = await this.get(this.endpoints.dashboard.stats);
        return response.data;
    }

    async getDashboardActivity() {
        const response = await this.get(this.endpoints.dashboard.activity);
        return response.data;
    }

    // Account methods
    async getAccounts(params = {}) {
        const response = await this.get(this.endpoints.accounts.list, params);
        return response.data;
    }

    async createAccount(accountData) {
        const response = await this.post(this.endpoints.accounts.create, accountData);
        return response.data;
    }

    async getAccount(id) {
        const response = await this.get(this.endpoints.accounts.get(id));
        return response.data;
    }

    async updateAccount(id, accountData) {
        const response = await this.put(this.endpoints.accounts.update(id), accountData);
        return response.data;
    }

    async deleteAccount(id) {
        const response = await this.delete(this.endpoints.accounts.delete(id));
        return response.data;
    }

    async testAccount(id) {
        const response = await this.post(this.endpoints.accounts.test(id));
        return response.data;
    }

    async reauthAccount(id) {
        const response = await this.post(this.endpoints.accounts.reauth(id));
        return response.data;
    }

    // Guest site methods
    async getGuestSites(params = {}) {
        const response = await this.get(this.endpoints.guestSites.list, params);
        return response.data;
    }

    async createGuestSite(siteData) {
        const response = await this.post(this.endpoints.guestSites.create, siteData);
        return response.data;
    }

    async testGuestSite(siteData) {
        const response = await this.post(this.endpoints.guestSites.test, siteData);
        return response.data;
    }

    async bulkTestGuestSites() {
        const response = await this.post(this.endpoints.guestSites.bulkTest);
        return response.data;
    }

    // Post methods
    async getPosts(params = {}) {
        const response = await this.get(this.endpoints.posts.list, params);
        return response.data;
    }

    async createPost(postData) {
        const response = await this.post(this.endpoints.posts.create, postData);
        return response.data;
    }

    async getPost(id) {
        const response = await this.get(this.endpoints.posts.get(id));
        return response.data;
    }

    async updatePost(id, postData) {
        const response = await this.put(this.endpoints.posts.update(id), postData);
        return response.data;
    }

    async deletePost(id) {
        const response = await this.delete(this.endpoints.posts.delete(id));
        return response.data;
    }

    async publishPost(id) {
        const response = await this.post(this.endpoints.posts.publish(id));
        return response.data;
    }

    // Content methods
    async generateContent(contentData) {
        const response = await this.post(this.endpoints.content.generate, contentData);
        return response.data;
    }

    async improveContent(contentData) {
        const response = await this.post(this.endpoints.content.improve, contentData);
        return response.data;
    }

    async scrapeContent(url) {
        const response = await this.post(this.endpoints.content.scrape, { url });
        return response.data;
    }

    // Automation methods
    async getAutomationStatus() {
        const response = await this.get(this.endpoints.automation.status);
        return response.data;
    }

    async startAutomation(config = {}) {
        const response = await this.post(this.endpoints.automation.start, config);
        return response.data;
    }

    async stopAutomation() {
        const response = await this.post(this.endpoints.automation.stop);
        return response.data;
    }

    // Notification methods
    async getNotifications(params = {}) {
        const response = await this.get(this.endpoints.notifications.list, params);
        return response.data;
    }

    async markNotificationAsRead(id) {
        const response = await this.post(this.endpoints.notifications.markRead(id));
        return response.data;
    }

    async markAllNotificationsAsRead() {
        const response = await this.post(this.endpoints.notifications.markAllRead);
        return response.data;
    }

    // Settings methods
    async getSettings() {
        const response = await this.get(this.endpoints.settings.get);
        return response.data;
    }

    async updateSettings(settings) {
        const response = await this.put(this.endpoints.settings.update, settings);
        return response.data;
    }
}

// Initialize API client
document.addEventListener('DOMContentLoaded', () => {
    window.api = new SocialMediaAPI();
    
    // Add loading state interceptor
    window.api.addRequestInterceptor(
        (config) => {
            // Show loading for non-background requests
            if (!config.background) {
                window.app?.showLoading();
            }
            return config;
        }
    );

    window.api.addResponseInterceptor(
        (response) => {
            // Hide loading
            window.app?.hideLoading();
            return response;
        },
        (error) => {
            // Hide loading on error
            window.app?.hideLoading();
            throw error;
        }
    );
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIClient, SocialMediaAPI };
}

