/**
 * Social Media Automation V2 - Main JavaScript
 * Handles UI interactions, navigation, and core functionality
 */

class SocialMediaApp {
    constructor() {
        this.init();
        this.bindEvents();
        this.loadInitialData();
    }

    init() {
        // Initialize app state
        this.sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        this.currentPage = window.location.pathname;
        
        // Apply saved sidebar state
        if (this.sidebarCollapsed) {
            document.getElementById('sidebar').classList.add('collapsed');
        }
        
        // Initialize components
        this.initTooltips();
        this.initModals();
        this.initDropdowns();
    }

    bindEvents() {
        // Sidebar toggle
        const sidebarToggle = document.getElementById('sidebarToggle');
        const mobileMenuToggle = document.getElementById('mobileMenuToggle');
        
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }
        
        if (mobileMenuToggle) {
            mobileMenuToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }

        // Notification dropdown
        const notificationBtn = document.getElementById('notificationBtn');
        const notificationDropdown = document.getElementById('notificationDropdown');
        
        if (notificationBtn && notificationDropdown) {
            notificationBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown(notificationDropdown);
            });
        }

        // User menu dropdown
        const userMenuBtn = document.getElementById('userMenuBtn');
        const userMenuDropdown = document.getElementById('userMenuDropdown');
        
        if (userMenuBtn && userMenuDropdown) {
            userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown(userMenuDropdown);
            });
        }

        // Global search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => this.handleGlobalSearch(e.target.value));
        }

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });

        // Handle form submissions
        document.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // Handle dynamic content loading
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action]')) {
                this.handleAction(e.target.dataset.action, e.target);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('collapsed');
        this.sidebarCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
    }

    toggleMobileSidebar() {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('show');
    }

    toggleDropdown(dropdown) {
        // Close other dropdowns first
        this.closeAllDropdowns();
        dropdown.classList.toggle('show');
    }

    closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.notification-dropdown, .user-menu-dropdown');
        dropdowns.forEach(dropdown => dropdown.classList.remove('show'));
    }

    handleGlobalSearch(query) {
        if (query.length < 2) return;
        
        // Implement global search functionality
        console.log('Searching for:', query);
        // This would typically make an API call to search across all content
    }

    handleFormSubmit(e) {
        const form = e.target;
        if (!form.matches('form[data-ajax]')) return;
        
        e.preventDefault();
        this.submitFormAjax(form);
    }

    async submitFormAjax(form) {
        const formData = new FormData(form);
        const url = form.action || window.location.href;
        const method = form.method || 'POST';

        try {
            this.showLoading();
            
            const response = await fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Success', result.message, 'success');
                if (result.redirect) {
                    window.location.href = result.redirect;
                } else if (result.reload) {
                    window.location.reload();
                }
            } else {
                this.showToast('Error', result.message, 'error');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showToast('Error', 'An error occurred while submitting the form', 'error');
        } finally {
            this.hideLoading();
        }
    }

    handleAction(action, element) {
        switch (action) {
            case 'delete':
                this.handleDelete(element);
                break;
            case 'edit':
                this.handleEdit(element);
                break;
            case 'test':
                this.handleTest(element);
                break;
            case 'publish':
                this.handlePublish(element);
                break;
            case 'generate':
                this.handleGenerate(element);
                break;
            default:
                console.log('Unknown action:', action);
        }
    }

    async handleDelete(element) {
        const id = element.dataset.id;
        const type = element.dataset.type;
        const name = element.dataset.name || 'item';

        if (!confirm(`Are you sure you want to delete this ${type}? This action cannot be undone.`)) {
            return;
        }

        try {
            this.showLoading();
            
            const response = await fetch(`/api/${type}s/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Success', `${type} deleted successfully`, 'success');
                // Remove the element from DOM
                const row = element.closest('tr') || element.closest('.card') || element.closest('.item');
                if (row) {
                    row.remove();
                }
            } else {
                this.showToast('Error', result.message, 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            this.showToast('Error', 'An error occurred while deleting', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async handleTest(element) {
        const id = element.dataset.id;
        const type = element.dataset.type;

        try {
            this.showLoading();
            element.disabled = true;
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
            
            const response = await fetch(`/api/${type}s/${id}/test`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Success', result.message, 'success');
                element.innerHTML = '<i class="fas fa-check"></i> Test Passed';
                element.classList.remove('btn-primary');
                element.classList.add('btn-success');
            } else {
                this.showToast('Error', result.message, 'error');
                element.innerHTML = '<i class="fas fa-times"></i> Test Failed';
                element.classList.remove('btn-primary');
                element.classList.add('btn-danger');
            }
        } catch (error) {
            console.error('Test error:', error);
            this.showToast('Error', 'An error occurred during testing', 'error');
            element.innerHTML = '<i class="fas fa-times"></i> Test Failed';
            element.classList.remove('btn-primary');
            element.classList.add('btn-danger');
        } finally {
            this.hideLoading();
            setTimeout(() => {
                element.disabled = false;
                element.innerHTML = '<i class="fas fa-vial"></i> Test';
                element.className = 'btn btn-primary btn-sm';
            }, 3000);
        }
    }

    async handlePublish(element) {
        const id = element.dataset.id;
        const type = element.dataset.type || 'post';

        if (!confirm('Are you sure you want to publish this post?')) {
            return;
        }

        try {
            this.showLoading();
            element.disabled = true;
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Publishing...';
            
            const response = await fetch(`/api/${type}s/${id}/publish`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();
            
            if (result.success) {
                this.showToast('Success', result.message, 'success');
                element.innerHTML = '<i class="fas fa-check"></i> Published';
                element.classList.remove('btn-primary');
                element.classList.add('btn-success');
                
                // Update status in the UI
                const statusCell = element.closest('tr')?.querySelector('.status');
                if (statusCell) {
                    statusCell.innerHTML = '<span class="badge badge-success">Published</span>';
                }
            } else {
                this.showToast('Error', result.message, 'error');
                element.innerHTML = '<i class="fas fa-times"></i> Failed';
                element.classList.remove('btn-primary');
                element.classList.add('btn-danger');
            }
        } catch (error) {
            console.error('Publish error:', error);
            this.showToast('Error', 'An error occurred while publishing', 'error');
            element.innerHTML = '<i class="fas fa-times"></i> Failed';
            element.classList.remove('btn-primary');
            element.classList.add('btn-danger');
        } finally {
            this.hideLoading();
            setTimeout(() => {
                element.disabled = false;
                if (!element.classList.contains('btn-success')) {
                    element.innerHTML = '<i class="fas fa-paper-plane"></i> Publish';
                    element.className = 'btn btn-primary btn-sm';
                }
            }, 3000);
        }
    }

    async handleGenerate(element) {
        const type = element.dataset.generateType || 'content';
        const target = element.dataset.target;

        try {
            this.showLoading();
            element.disabled = true;
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            const response = await fetch('/api/content/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    type: type,
                    topic: document.getElementById('topic')?.value || '',
                    platform: document.getElementById('platform')?.value || '',
                    tone: document.getElementById('tone')?.value || 'professional'
                })
            });

            const result = await response.json();
            
            if (result.success || result.content) {
                this.showToast('Success', 'Content generated successfully', 'success');
                
                // Fill the target field with generated content
                if (target) {
                    const targetElement = document.getElementById(target);
                    if (targetElement) {
                        targetElement.value = result.content;
                        // Trigger input event for any listeners
                        targetElement.dispatchEvent(new Event('input'));
                    }
                }
            } else {
                this.showToast('Error', result.message || 'Failed to generate content', 'error');
            }
        } catch (error) {
            console.error('Generate error:', error);
            this.showToast('Error', 'An error occurred while generating content', 'error');
        } finally {
            this.hideLoading();
            element.disabled = false;
            element.innerHTML = '<i class="fas fa-magic"></i> Generate';
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for global search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('globalSearch');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Escape to close modals and dropdowns
        if (e.key === 'Escape') {
            this.closeAllDropdowns();
            this.closeAllModals();
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('show');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    }

    showToast(title, message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

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

        container.appendChild(toast);

        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    initTooltips() {
        // Initialize tooltips for elements with data-tooltip attribute
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', this.showTooltip.bind(this));
            element.addEventListener('mouseleave', this.hideTooltip.bind(this));
        });
    }

    showTooltip(e) {
        const element = e.target;
        const text = element.dataset.tooltip;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        element._tooltip = tooltip;
    }

    hideTooltip(e) {
        const element = e.target;
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    }

    initModals() {
        // Initialize modal functionality
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.openModal(modalId);
            });
        });

        // Close modal when clicking backdrop
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-backdrop')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });

        // Close modal with close button
        document.addEventListener('click', (e) => {
            if (e.target.matches('.modal-close, .modal-close *')) {
                this.closeModal(e.target.closest('.modal'));
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    closeAllModals() {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => this.closeModal(modal));
    }

    initDropdowns() {
        // Initialize custom dropdown functionality
        const dropdownTriggers = document.querySelectorAll('[data-dropdown]');
        dropdownTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const dropdownId = trigger.dataset.dropdown;
                const dropdown = document.getElementById(dropdownId);
                if (dropdown) {
                    this.toggleDropdown(dropdown);
                }
            });
        });
    }

    async loadInitialData() {
        // Load dashboard stats if on dashboard page
        if (this.currentPage === '/' || this.currentPage === '/dashboard') {
            await this.loadDashboardStats();
        }
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/dashboard/stats');
            const stats = await response.json();
            
            if (stats) {
                this.updateDashboardStats(stats);
            }
        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    updateDashboardStats(stats) {
        // Update stat cards
        const statElements = {
            'totalAccounts': stats.total_accounts,
            'totalPosts': stats.total_posts,
            'publishedPosts': stats.published_posts,
            'pendingPosts': stats.pending_posts,
            'successRate': stats.success_rate + '%'
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    // Utility methods
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    formatNumber(number) {
        return new Intl.NumberFormat().format(number);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SocialMediaApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocialMediaApp;
}

