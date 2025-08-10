/**
 * Notifications System
 * Handles toast notifications, real-time updates, and notification management
 */

class NotificationSystem {
    constructor() {
        this.notifications = [];
        this.container = null;
        this.init();
    }

    init() {
        this.createContainer();
        this.bindEvents();
        this.loadNotifications();
        
        // Start real-time updates
        this.startRealTimeUpdates();
    }

    createContainer() {
        // Create toast container if it doesn't exist
        let container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        this.container = container;
    }

    bindEvents() {
        // Handle notification dropdown
        const notificationBtn = document.getElementById('notificationBtn');
        const notificationDropdown = document.getElementById('notificationDropdown');
        
        if (notificationBtn && notificationDropdown) {
            notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleNotificationDropdown();
            });
        }

        // Handle mark all as read
        const markAllReadBtn = document.querySelector('.mark-all-read');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }

        // Handle individual notification clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.notification-item')) {
                const notificationItem = e.target.closest('.notification-item');
                const notificationId = notificationItem.dataset.id;
                if (notificationId) {
                    this.markAsRead(notificationId);
                }
            }
        });
    }

    toggleNotificationDropdown() {
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.classList.toggle('show');
            
            if (dropdown.classList.contains('show')) {
                this.loadNotifications();
            }
        }
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications');
            const data = await response.json();
            
            if (data.notifications) {
                this.notifications = data.notifications;
                this.updateNotificationDropdown();
                this.updateNotificationBadge();
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    updateNotificationDropdown() {
        const notificationList = document.querySelector('.notification-list');
        if (!notificationList) return;

        if (this.notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="notification-item" style="text-align: center; padding: 40px 20px;">
                    <div style="color: var(--gray-500);">
                        <i class="fas fa-bell-slash" style="font-size: 32px; margin-bottom: 12px; opacity: 0.5;"></i>
                        <p>No notifications</p>
                    </div>
                </div>
            `;
            return;
        }

        notificationList.innerHTML = this.notifications.map(notification => `
            <div class="notification-item ${notification.read ? '' : 'unread'}" data-id="${notification.id}">
                <i class="fas fa-${this.getNotificationIcon(notification.type)} ${this.getNotificationColor(notification.type)}"></i>
                <div class="notification-content">
                    <p>${notification.message}</p>
                    <span class="notification-time">${this.formatTimeAgo(notification.created_at)}</span>
                </div>
                ${!notification.read ? '<div class="notification-dot"></div>' : ''}
            </div>
        `).join('');
    }

    updateNotificationBadge() {
        const badge = document.querySelector('.notification-badge');
        if (!badge) return;

        const unreadCount = this.notifications.filter(n => !n.read).length;
        
        if (unreadCount > 0) {
            badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'error': 'exclamation-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'post_published': 'paper-plane',
            'account_added': 'user-plus',
            'automation_started': 'robot',
            'automation_stopped': 'stop-circle',
            'content_generated': 'magic',
            'site_connected': 'link',
            'login_required': 'key'
        };
        return icons[type] || 'bell';
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'text-success',
            'error': 'text-danger',
            'warning': 'text-warning',
            'info': 'text-info',
            'post_published': 'text-success',
            'account_added': 'text-info',
            'automation_started': 'text-success',
            'automation_stopped': 'text-warning',
            'content_generated': 'text-primary',
            'site_connected': 'text-success',
            'login_required': 'text-warning'
        };
        return colors[type] || 'text-info';
    }

    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Update local state
                const notification = this.notifications.find(n => n.id == notificationId);
                if (notification) {
                    notification.read = true;
                    this.updateNotificationDropdown();
                    this.updateNotificationBadge();
                }
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                // Update local state
                this.notifications.forEach(n => n.read = true);
                this.updateNotificationDropdown();
                this.updateNotificationBadge();
                
                this.showToast('Success', 'All notifications marked as read', 'success');
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }

    showToast(title, message, type = 'info', duration = 5000) {
        const toast = this.createToast(title, message, type);
        this.container.appendChild(toast);

        // Show toast with animation
        setTimeout(() => toast.classList.add('show'), 100);

        // Auto remove
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);

        return toast;
    }

    createToast(title, message, type) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="toast-icon ${icons[type] || icons.info}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add click to dismiss
        toast.addEventListener('click', (e) => {
            if (e.target.classList.contains('toast-close') || e.target.closest('.toast-close')) {
                this.removeToast(toast);
            }
        });

        return toast;
    }

    removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Real-time notification updates
    startRealTimeUpdates() {
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.checkForNewNotifications();
        }, 30000);

        // Also check when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkForNewNotifications();
            }
        });
    }

    async checkForNewNotifications() {
        try {
            const lastCheck = localStorage.getItem('lastNotificationCheck') || '0';
            const response = await fetch(`/api/notifications/new?since=${lastCheck}`);
            const data = await response.json();

            if (data.notifications && data.notifications.length > 0) {
                // Show toast for new notifications
                data.notifications.forEach(notification => {
                    this.showToast(
                        'New Notification',
                        notification.message,
                        this.mapNotificationTypeToToastType(notification.type),
                        7000
                    );
                });

                // Update local notifications
                this.notifications = [...data.notifications, ...this.notifications];
                this.updateNotificationDropdown();
                this.updateNotificationBadge();
            }

            // Update last check timestamp
            localStorage.setItem('lastNotificationCheck', Date.now().toString());
        } catch (error) {
            console.error('Error checking for new notifications:', error);
        }
    }

    mapNotificationTypeToToastType(notificationType) {
        const mapping = {
            'success': 'success',
            'error': 'error',
            'warning': 'warning',
            'info': 'info',
            'post_published': 'success',
            'account_added': 'success',
            'automation_started': 'info',
            'automation_stopped': 'warning',
            'content_generated': 'success',
            'site_connected': 'success',
            'login_required': 'warning'
        };
        return mapping[notificationType] || 'info';
    }

    // Programmatic notification creation
    async createNotification(type, message, data = {}) {
        try {
            const response = await fetch('/api/notifications', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    message: message,
                    data: data
                })
            });

            if (response.ok) {
                const notification = await response.json();
                
                // Add to local notifications
                this.notifications.unshift(notification);
                this.updateNotificationDropdown();
                this.updateNotificationBadge();
                
                // Show toast
                this.showToast(
                    'Notification',
                    message,
                    this.mapNotificationTypeToToastType(type)
                );
                
                return notification;
            }
        } catch (error) {
            console.error('Error creating notification:', error);
        }
    }

    // Utility methods
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
        if (diffInSeconds < 604800) return Math.floor(diffInSeconds / 86400) + ' days ago';
        return date.toLocaleDateString();
    }

    // Public API methods
    success(title, message) {
        return this.showToast(title, message, 'success');
    }

    error(title, message) {
        return this.showToast(title, message, 'error');
    }

    warning(title, message) {
        return this.showToast(title, message, 'warning');
    }

    info(title, message) {
        return this.showToast(title, message, 'info');
    }

    // Clear all notifications
    clearAll() {
        const toasts = this.container.querySelectorAll('.toast');
        toasts.forEach(toast => this.removeToast(toast));
    }

    // Get notification count
    getUnreadCount() {
        return this.notifications.filter(n => !n.read).length;
    }

    // Subscribe to notification events
    on(event, callback) {
        document.addEventListener(`notification:${event}`, callback);
    }

    // Emit notification events
    emit(event, data) {
        document.dispatchEvent(new CustomEvent(`notification:${event}`, { detail: data }));
    }
}

// Initialize notification system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notifications = new NotificationSystem();
    
    // Make it available globally for other scripts
    window.showToast = (title, message, type, duration) => {
        return window.notifications.showToast(title, message, type, duration);
    };
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationSystem;
}

