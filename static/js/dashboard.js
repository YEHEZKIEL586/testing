// Dashboard specific JavaScript
class DashboardManager {
    constructor() {
        this.charts = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.loadDashboardData();
        this.initCharts();
        this.setupRefreshInterval();
        this.setupEventListeners();
    }

    async loadDashboardData() {
        try {
            window.app.showLoading();
            
            const response = await fetch('/api/dashboard/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.stats);
                this.updateCharts(data.charts);
                this.updateRecentPosts(data.recent_posts);
                this.updatePlatformStats(data.platform_stats);
            } else {
                throw new Error(data.message || 'Failed to load dashboard data');
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showErrorState();
        } finally {
            window.app.hideLoading();
        }
    }

    updateStats(stats) {
        // Update stat cards
        const statElements = {
            'total-accounts': stats.total_accounts || 0,
            'total-posts': stats.total_posts || 0,
            'success-rate': (stats.success_rate || 0) + '%',
            'pending-posts': stats.pending_posts || 0
        };

        Object.keys(statElements).forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = statElements[id];
                
                // Add animation
                element.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            }
        });

        // Update trend indicators
        this.updateTrendIndicators(stats.trends || {});
    }

    updateTrendIndicators(trends) {
        Object.keys(trends).forEach(key => {
            const trendElement = document.querySelector(`[data-trend="${key}"]`);
            if (trendElement) {
                const trend = trends[key];
                const isPositive = trend.direction === 'up';
                
                trendElement.className = `trend ${isPositive ? 'trend-up' : 'trend-down'}`;
                trendElement.innerHTML = `
                    <i class="fas fa-arrow-${isPositive ? 'up' : 'down'}"></i>
                    ${Math.abs(trend.percentage)}%
                `;
            }
        });
    }

    initCharts() {
        this.initPostsChart();
        this.initPlatformChart();
        this.initSuccessRateChart();
    }

    initPostsChart() {
        const ctx = document.getElementById('postsChart');
        if (!ctx) return;

        this.charts.posts = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Posts',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    initPlatformChart() {
        const ctx = document.getElementById('platformChart');
        if (!ctx) return;

        this.charts.platform = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#3B82F6', // Blue
                        '#EF4444', // Red
                        '#10B981', // Green
                        '#F59E0B', // Yellow
                        '#8B5CF6', // Purple
                        '#EC4899'  // Pink
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }

    initSuccessRateChart() {
        const ctx = document.getElementById('successRateChart');
        if (!ctx) return;

        this.charts.successRate = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Success Rate',
                    data: [],
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    updateCharts(chartData) {
        // Update posts chart
        if (this.charts.posts && chartData.posts) {
            this.charts.posts.data.labels = chartData.posts.labels;
            this.charts.posts.data.datasets[0].data = chartData.posts.data;
            this.charts.posts.update('none');
        }

        // Update platform chart
        if (this.charts.platform && chartData.platforms) {
            this.charts.platform.data.labels = chartData.platforms.labels;
            this.charts.platform.data.datasets[0].data = chartData.platforms.data;
            this.charts.platform.update('none');
        }

        // Update success rate chart
        if (this.charts.successRate && chartData.success_rate) {
            this.charts.successRate.data.labels = chartData.success_rate.labels;
            this.charts.successRate.data.datasets[0].data = chartData.success_rate.data;
            this.charts.successRate.update('none');
        }
    }

    updateRecentPosts(posts) {
        const container = document.getElementById('recentPostsList');
        if (!container) return;

        if (!posts || posts.length === 0) {
            container.innerHTML = this.getEmptyPostsHTML();
            return;
        }

        container.innerHTML = posts.map(post => this.createPostItemHTML(post)).join('');
    }

    getEmptyPostsHTML() {
        return `
            <div class="empty-state">
                <i class="fas fa-file-alt"></i>
                <p>No recent posts</p>
                <button class="btn btn-primary" onclick="window.location.href='/content'">
                    <i class="fas fa-plus"></i>
                    Create Your First Post
                </button>
            </div>
        `;
    }

    createPostItemHTML(post) {
        const statusClass = this.getPostStatusClass(post.status);
        const platformIcon = this.getPlatformIcon(post.platform);
        
        return `
            <div class="post-item" data-post-id="${post.id}">
                <div class="post-platform">
                    <i class="fab fa-${platformIcon}"></i>
                </div>
                <div class="post-content">
                    <h4>${this.truncateText(post.title || post.content, 50)}</h4>
                    <p>${this.truncateText(post.content, 100)}</p>
                    <div class="post-meta">
                        <span class="post-time">
                            <i class="fas fa-clock"></i>
                            ${this.formatTimeAgo(post.created_at)}
                        </span>
                        <span class="post-account">
                            <i class="fas fa-user"></i>
                            ${post.account_name}
                        </span>
                    </div>
                </div>
                <div class="post-status">
                    <span class="badge badge-${statusClass}">${this.capitalizeFirst(post.status)}</span>
                </div>
                <div class="post-actions">
                    <button class="btn btn-sm btn-outline" data-action="view-post" data-id="${post.id}">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline" data-action="edit-post" data-id="${post.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${post.status === 'failed' ? `
                        <button class="btn btn-sm btn-warning" data-action="retry-post" data-id="${post.id}">
                            <i class="fas fa-redo"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }

    updatePlatformStats(platformStats) {
        const container = document.getElementById('platformStats');
        if (!container || !platformStats) return;

        container.innerHTML = platformStats.map(stat => this.createPlatformStatHTML(stat)).join('');
    }

    createPlatformStatHTML(stat) {
        const iconClass = this.getPlatformIcon(stat.platform);
        const colorClass = this.getPlatformColor(stat.platform);
        
        return `
            <div class="platform-stat">
                <div class="platform-icon ${colorClass}">
                    <i class="fab fa-${iconClass}"></i>
                </div>
                <div class="platform-info">
                    <h4>${this.capitalizeFirst(stat.platform)}</h4>
                    <div class="platform-metrics">
                        <span class="metric">
                            <strong>${stat.posts}</strong> posts
                        </span>
                        <span class="metric">
                            <strong>${stat.success_rate}%</strong> success
                        </span>
                    </div>
                </div>
                <div class="platform-trend">
                    <span class="trend ${stat.trend > 0 ? 'trend-up' : 'trend-down'}">
                        <i class="fas fa-arrow-${stat.trend > 0 ? 'up' : 'down'}"></i>
                        ${Math.abs(stat.trend)}%
                    </span>
                </div>
            </div>
        `;
    }

    setupRefreshInterval() {
        // Refresh dashboard every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 30000);
    }

    setupEventListeners() {
        // Quick action buttons
        document.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]');
            if (!action) return;

            const actionType = action.dataset.action;
            const itemId = action.dataset.id;

            switch (actionType) {
                case 'refresh-dashboard':
                    this.loadDashboardData();
                    break;
                case 'scrape-wordpress':
                    this.scrapeWordPress();
                    break;
                case 'process-posts':
                    this.processPosts();
                    break;
                case 'view-post':
                    this.viewPost(itemId);
                    break;
                case 'edit-post':
                    this.editPost(itemId);
                    break;
                case 'retry-post':
                    this.retryPost(itemId);
                    break;
            }
        });

        // Handle page visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Pause refresh when tab is not visible
                if (this.refreshInterval) {
                    clearInterval(this.refreshInterval);
                    this.refreshInterval = null;
                }
            } else {
                // Resume refresh when tab becomes visible
                this.setupRefreshInterval();
                this.loadDashboardData();
            }
        });
    }

    async scrapeWordPress() {
        try {
            window.app.showLoading();
            window.app.showToast('Info', 'Starting WordPress scraping...', 'info');
            
            const response = await fetch('/api/wordpress/scrape', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', `Scraped ${result.count} articles successfully!`, 'success');
                this.loadDashboardData(); // Refresh dashboard
            } else {
                throw new Error(result.message || 'Failed to scrape WordPress');
            }
        } catch (error) {
            console.error('Error scraping WordPress:', error);
            window.app.showToast('Error', error.message || 'Failed to scrape WordPress', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async processPosts() {
        try {
            window.app.showLoading();
            window.app.showToast('Info', 'Processing posts...', 'info');
            
            const response = await fetch('/api/posts/process', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', `Processed ${result.count} posts successfully!`, 'success');
                this.loadDashboardData(); // Refresh dashboard
            } else {
                throw new Error(result.message || 'Failed to process posts');
            }
        } catch (error) {
            console.error('Error processing posts:', error);
            window.app.showToast('Error', error.message || 'Failed to process posts', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    viewPost(postId) {
        window.location.href = `/posts/${postId}`;
    }

    editPost(postId) {
        window.location.href = `/posts/${postId}/edit`;
    }

    async retryPost(postId) {
        try {
            window.app.showLoading();
            
            const response = await fetch(`/api/posts/${postId}/retry`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'Post retry initiated!', 'success');
                this.loadDashboardData(); // Refresh dashboard
            } else {
                throw new Error(result.message || 'Failed to retry post');
            }
        } catch (error) {
            console.error('Error retrying post:', error);
            window.app.showToast('Error', error.message || 'Failed to retry post', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    showErrorState() {
        const mainContent = document.querySelector('.dashboard-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="error-state">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Failed to Load Dashboard</h3>
                    <p>There was an error loading the dashboard data.</p>
                    <button class="btn btn-primary" data-action="refresh-dashboard">
                        <i class="fas fa-refresh"></i>
                        Try Again
                    </button>
                </div>
            `;
        }
    }

    // Utility methods
    getPostStatusClass(status) {
        const statusClasses = {
            'published': 'success',
            'scheduled': 'info',
            'draft': 'secondary',
            'failed': 'danger',
            'processing': 'warning'
        };
        return statusClasses[status] || 'secondary';
    }

    getPlatformIcon(platform) {
        const icons = {
            'facebook': 'facebook',
            'instagram': 'instagram',
            'twitter': 'twitter',
            'linkedin': 'linkedin',
            'wordpress': 'wordpress'
        };
        return icons[platform] || 'globe';
    }

    getPlatformColor(platform) {
        const colors = {
            'facebook': 'text-primary',
            'instagram': 'text-danger',
            'twitter': 'text-info',
            'linkedin': 'text-info',
            'wordpress': 'text-secondary'
        };
        return colors[platform] || 'text-secondary';
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    formatTimeAgo(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + 'm ago';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + 'h ago';
        if (diffInSeconds < 604800) return Math.floor(diffInSeconds / 86400) + 'd ago';
        return date.toLocaleDateString();
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Destroy charts
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on dashboard page
    if (document.querySelector('.dashboard-content')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Cleanup when leaving page
window.addEventListener('beforeunload', function() {
    if (window.dashboardManager) {
        window.dashboardManager.destroy();
    }
});

