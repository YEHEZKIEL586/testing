// Settings page specific JavaScript
class SettingsManager {
    constructor() {
        this.currentSettings = {};
        this.unsavedChanges = false;
        this.init();
    }

    init() {
        this.initTabs();
        this.initForms();
        this.initPasswordToggles();
        this.initRangeSliders();
        this.loadSettings();
        this.setupAutoSave();
        this.setupBeforeUnload();
    }

    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetTab = button.dataset.tab;
                
                // Update active states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                tabContents.forEach(content => content.classList.remove('active'));
                
                button.classList.add('active');
                const targetContent = document.getElementById(targetTab);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
                
                // Update URL hash
                window.location.hash = targetTab;
            });
        });

        // Handle initial tab from URL hash
        const hash = window.location.hash.substring(1);
        if (hash) {
            const targetButton = document.querySelector(`[data-tab="${hash}"]`);
            if (targetButton) {
                targetButton.click();
            }
        }
    }

    initForms() {
        const forms = document.querySelectorAll('form[data-ajax]');
        
        forms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleFormSubmit(form);
            });

            // Track changes
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('change', () => {
                    this.markUnsaved();
                });
            });
        });
    }

    initPasswordToggles() {
        const toggleButtons = document.querySelectorAll('[data-action="toggle-password"]');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const input = button.parentElement.querySelector('input');
                const icon = button.querySelector('i');
                
                if (input.type === 'password') {
                    input.type = 'text';
                    icon.className = 'fas fa-eye-slash';
                    button.setAttribute('title', 'Hide password');
                } else {
                    input.type = 'password';
                    icon.className = 'fas fa-eye';
                    button.setAttribute('title', 'Show password');
                }
            });
        });
    }

    initRangeSliders() {
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        
        rangeInputs.forEach(input => {
            const updateValue = () => {
                const value = input.value;
                const min = input.min || 0;
                const max = input.max || 100;
                const percentage = ((value - min) / (max - min)) * 100;
                
                // Update visual indicator
                input.style.background = `linear-gradient(to right, var(--primary-color) 0%, var(--primary-color) ${percentage}%, var(--gray-300) ${percentage}%, var(--gray-300) 100%)`;
                
                // Update value display
                const valueDisplay = input.parentElement.querySelector('.range-value');
                if (valueDisplay) {
                    valueDisplay.textContent = value;
                }
            };

            input.addEventListener('input', updateValue);
            updateValue(); // Initial update
        });
    }

    async loadSettings() {
        try {
            window.app.showLoading();
            
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.success) {
                this.currentSettings = data.settings;
                this.populateSettings(data.settings);
            } else {
                throw new Error(data.message || 'Failed to load settings');
            }
        } catch (error) {
            console.error('Error loading settings:', error);
            window.app.showToast('Error', 'Failed to load settings', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    populateSettings(settings) {
        Object.keys(settings).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                if (input.type === 'checkbox') {
                    input.checked = Boolean(settings[key]);
                } else if (input.type === 'radio') {
                    const radioInput = document.querySelector(`[name="${key}"][value="${settings[key]}"]`);
                    if (radioInput) {
                        radioInput.checked = true;
                    }
                } else {
                    input.value = settings[key] || '';
                }

                // Trigger change event for range sliders
                if (input.type === 'range') {
                    input.dispatchEvent(new Event('input'));
                }
            }
        });

        this.unsavedChanges = false;
        this.updateSaveButton();
    }

    async handleFormSubmit(form) {
        try {
            const formData = new FormData(form);
            const settingsType = this.getSettingsTypeFromForm(form);
            
            window.app.showLoading();
            
            const response = await fetch(`/api/settings/${settingsType}`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'Settings saved successfully!', 'success');
                this.unsavedChanges = false;
                this.updateSaveButton();
                
                // Update current settings
                const newSettings = Object.fromEntries(formData.entries());
                Object.assign(this.currentSettings, newSettings);
                
                // Handle special cases
                if (settingsType === 'account') {
                    window.app.closeModal('addAccountModal');
                    this.loadAccounts();
                }
            } else {
                throw new Error(result.message || 'Failed to save settings');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            window.app.showToast('Error', error.message || 'Failed to save settings', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    getSettingsTypeFromForm(form) {
        const formId = form.id;
        const mapping = {
            'generalSettingsForm': 'general',
            'contentSettingsForm': 'content',
            'openaiSettingsForm': 'openai',
            'otherApiSettingsForm': 'api',
            'emailNotificationForm': 'email',
            'browserNotificationForm': 'browser',
            'botSecurityForm': 'security',
            'dataSecurityForm': 'data',
            'performanceSettingsForm': 'performance',
            'debugSettingsForm': 'debug',
            'addAccountForm': 'account'
        };
        return mapping[formId] || 'general';
    }

    setupAutoSave() {
        // Auto-save every 30 seconds if there are unsaved changes
        setInterval(() => {
            if (this.unsavedChanges) {
                this.autoSave();
            }
        }, 30000);
    }

    async autoSave() {
        try {
            const forms = document.querySelectorAll('form[data-ajax]');
            const settingsData = {};
            
            forms.forEach(form => {
                const formData = new FormData(form);
                Object.assign(settingsData, Object.fromEntries(formData.entries()));
            });
            
            const response = await fetch('/api/settings/auto-save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settingsData)
            });
            
            if (response.ok) {
                console.log('Settings auto-saved');
                this.unsavedChanges = false;
                this.updateSaveButton();
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    setupBeforeUnload() {
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    markUnsaved() {
        this.unsavedChanges = true;
        this.updateSaveButton();
    }

    updateSaveButton() {
        const saveButton = document.querySelector('[data-action="save-all-settings"]');
        if (saveButton) {
            if (this.unsavedChanges) {
                saveButton.classList.add('btn-warning');
                saveButton.classList.remove('btn-success');
                saveButton.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Save Changes';
            } else {
                saveButton.classList.add('btn-success');
                saveButton.classList.remove('btn-warning');
                saveButton.innerHTML = '<i class="fas fa-check"></i> All Saved';
            }
        }
    }

    async saveAllSettings() {
        const forms = document.querySelectorAll('form[data-ajax]');
        let successCount = 0;
        let totalForms = forms.length;
        
        window.app.showLoading();
        
        for (const form of forms) {
            try {
                await this.handleFormSubmit(form);
                successCount++;
            } catch (error) {
                console.error('Error saving form:', form.id, error);
            }
        }
        
        window.app.hideLoading();
        
        if (successCount === totalForms) {
            window.app.showToast('Success', `All ${successCount} setting groups saved successfully!`, 'success');
        } else {
            window.app.showToast('Warning', `Saved ${successCount} of ${totalForms} setting groups`, 'warning');
        }
    }

    async resetSettings() {
        const confirmed = await window.app.showConfirm(
            'Reset Settings',
            'Are you sure you want to reset all settings to defaults? This cannot be undone.',
            'warning'
        );
        
        if (confirmed) {
            try {
                window.app.showLoading();
                
                const response = await fetch('/api/settings/reset', {
                    method: 'POST'
                });
                
                const result = await response.json();
                
                if (result.success) {
                    window.app.showToast('Success', 'Settings reset to defaults', 'success');
                    await this.loadSettings();
                } else {
                    throw new Error(result.message || 'Failed to reset settings');
                }
            } catch (error) {
                console.error('Error resetting settings:', error);
                window.app.showToast('Error', 'Failed to reset settings', 'error');
            } finally {
                window.app.hideLoading();
            }
        }
    }

    // Account management methods
    async loadAccounts() {
        try {
            const response = await fetch('/api/accounts');
            const data = await response.json();
            
            if (data.success) {
                this.updateAccountsList(data.accounts);
            }
        } catch (error) {
            console.error('Error loading accounts:', error);
        }
    }

    updateAccountsList(accounts) {
        const accountsList = document.getElementById('accountsList');
        if (!accountsList) return;
        
        if (accounts.length === 0) {
            accountsList.innerHTML = this.getEmptyAccountsHTML();
            return;
        }
        
        accountsList.innerHTML = accounts.map(account => this.createAccountItemHTML(account)).join('');
    }

    getEmptyAccountsHTML() {
        return `
            <div style="text-align: center; padding: 40px; color: var(--gray-500);">
                <i class="fas fa-users" style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;"></i>
                <p>No accounts connected</p>
                <button class="btn btn-primary" data-modal="addAccountModal">
                    <i class="fas fa-plus"></i>
                    Add Your First Account
                </button>
            </div>
        `;
    }

    createAccountItemHTML(account) {
        return `
            <div class="account-item" data-account-id="${account.id}">
                <div class="account-info">
                    <div class="account-icon">
                        <i class="fab fa-${account.platform} ${this.getPlatformColor(account.platform)}"></i>
                    </div>
                    <div class="account-details">
                        <h4>${account.account_name}</h4>
                        <p>@${account.username} • ${this.capitalizeFirst(account.status)}</p>
                        <small>Last used: ${this.formatTimeAgo(account.last_used)}</small>
                    </div>
                </div>
                <div class="account-status">
                    <span class="badge badge-${this.getAccountStatusColor(account.status)}">${this.capitalizeFirst(account.status)}</span>
                </div>
                <div class="account-actions">
                    ${this.getAccountActionsHTML(account)}
                </div>
            </div>
        `;
    }

    getPlatformColor(platform) {
        const colors = {
            'facebook': 'text-primary',
            'instagram': 'text-danger',
            'twitter': 'text-info',
            'linkedin': 'text-info'
        };
        return colors[platform] || 'text-secondary';
    }

    getAccountStatusColor(status) {
        const colors = {
            'active': 'success',
            'needs_attention': 'warning',
            'disconnected': 'danger',
            'pending': 'info'
        };
        return colors[status] || 'secondary';
    }

    getAccountActionsHTML(account) {
        let actions = '';
        
        if (account.status === 'active') {
            actions += `
                <button class="btn btn-sm btn-outline" data-action="test-account" data-id="${account.id}">
                    <i class="fas fa-check"></i>
                    Test
                </button>
            `;
        } else if (account.status === 'needs_attention') {
            actions += `
                <button class="btn btn-sm btn-warning" data-action="reconnect-account" data-id="${account.id}">
                    <i class="fas fa-sync"></i>
                    Reconnect
                </button>
            `;
        }
        
        actions += `
            <button class="btn btn-sm btn-outline" data-action="edit-account" data-id="${account.id}">
                <i class="fas fa-edit"></i>
                Edit
            </button>
            <button class="btn btn-sm btn-danger" data-action="disconnect-account" data-id="${account.id}">
                <i class="fas fa-unlink"></i>
                Disconnect
            </button>
        `;
        
        return actions;
    }

    // Test methods
    async testOpenAI() {
        try {
            window.app.showLoading();
            
            const response = await fetch('/api/test/openai', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'OpenAI connection successful!', 'success');
            } else {
                throw new Error(result.message || 'OpenAI connection failed');
            }
        } catch (error) {
            console.error('Error testing OpenAI:', error);
            window.app.showToast('Error', error.message || 'Failed to test OpenAI connection', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async testEmail() {
        try {
            window.app.showLoading();
            
            const response = await fetch('/api/test/email', { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'Test email sent successfully!', 'success');
            } else {
                throw new Error(result.message || 'Failed to send test email');
            }
        } catch (error) {
            console.error('Error testing email:', error);
            window.app.showToast('Error', error.message || 'Failed to send test email', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    testBrowserNotification() {
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                this.showTestNotification();
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        this.showTestNotification();
                    } else {
                        window.app.showToast('Error', 'Notification permission denied', 'error');
                    }
                });
            } else {
                window.app.showToast('Error', 'Browser notifications are blocked', 'error');
            }
        } else {
            window.app.showToast('Error', 'Browser notifications not supported', 'error');
        }
    }

    showTestNotification() {
        const notification = new Notification('Test Notification', {
            body: 'This is a test notification from Social Media Automation V2',
            icon: '/static/favicon.ico',
            badge: '/static/favicon.ico'
        });

        setTimeout(() => {
            notification.close();
        }, 5000);

        window.app.showToast('Success', 'Test notification sent!', 'success');
    }

    // Account actions
    async testAccount(accountId) {
        try {
            window.app.showLoading();
            
            const response = await fetch(`/api/accounts/${accountId}/test`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'Account connection successful!', 'success');
                this.loadAccounts();
            } else {
                throw new Error(result.message || 'Account connection failed');
            }
        } catch (error) {
            console.error('Error testing account:', error);
            window.app.showToast('Error', error.message || 'Failed to test account connection', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async reconnectAccount(accountId) {
        try {
            window.app.showLoading();
            
            const response = await fetch(`/api/accounts/${accountId}/reconnect`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                window.app.showToast('Success', 'Account reconnected successfully!', 'success');
                this.loadAccounts();
            } else {
                throw new Error(result.message || 'Failed to reconnect account');
            }
        } catch (error) {
            console.error('Error reconnecting account:', error);
            window.app.showToast('Error', error.message || 'Failed to reconnect account', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async editAccount(accountId) {
        // Implementation would load account data and open edit modal
        console.log('Edit account:', accountId);
        window.app.showToast('Info', 'Edit account feature coming soon!', 'info');
    }

    async disconnectAccount(accountId) {
        const confirmed = await window.app.showConfirm(
            'Disconnect Account',
            'Are you sure you want to disconnect this account?',
            'warning'
        );
        
        if (confirmed) {
            try {
                window.app.showLoading();
                
                const response = await fetch(`/api/accounts/${accountId}`, { method: 'DELETE' });
                const result = await response.json();
                
                if (result.success) {
                    window.app.showToast('Success', 'Account disconnected successfully!', 'success');
                    this.loadAccounts();
                } else {
                    throw new Error(result.message || 'Failed to disconnect account');
                }
            } catch (error) {
                console.error('Error disconnecting account:', error);
                window.app.showToast('Error', error.message || 'Failed to disconnect account', 'error');
            } finally {
                window.app.hideLoading();
            }
        }
    }

    // Data management
    async exportData() {
        try {
            window.app.showLoading();
            
            const response = await fetch('/api/export/data');
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `social_automation_data_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                window.app.showToast('Success', 'Data exported successfully!', 'success');
            } else {
                throw new Error('Failed to export data');
            }
        } catch (error) {
            console.error('Error exporting data:', error);
            window.app.showToast('Error', 'Failed to export data', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async clearLogs() {
        const confirmed = await window.app.showConfirm(
            'Clear Logs',
            'Are you sure you want to clear old logs? This cannot be undone.',
            'warning'
        );
        
        if (confirmed) {
            try {
                window.app.showLoading();
                
                const response = await fetch('/api/logs/clear', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    window.app.showToast('Success', `Cleared ${result.count || 0} log entries`, 'success');
                } else {
                    throw new Error(result.message || 'Failed to clear logs');
                }
            } catch (error) {
                console.error('Error clearing logs:', error);
                window.app.showToast('Error', error.message || 'Failed to clear logs', 'error');
            } finally {
                window.app.hideLoading();
            }
        }
    }

    async checkUpdates() {
        try {
            window.app.showLoading();
            window.app.showToast('Info', 'Checking for updates...', 'info');
            
            const response = await fetch('/api/updates/check');
            const result = await response.json();
            
            if (result.success) {
                if (result.hasUpdate) {
                    window.app.showToast('Info', `Update available: ${result.version}`, 'info');
                } else {
                    window.app.showToast('Success', 'You are running the latest version!', 'success');
                }
            } else {
                throw new Error(result.message || 'Failed to check for updates');
            }
        } catch (error) {
            console.error('Error checking updates:', error);
            window.app.showToast('Error', 'Failed to check for updates', 'error');
        } finally {
            window.app.hideLoading();
        }
    }

    async resetApp() {
        const confirmed1 = await window.app.showConfirm(
            'Reset Application',
            'Are you sure you want to reset the entire application? This will delete all data and cannot be undone.',
            'danger'
        );
        
        if (confirmed1) {
            const confirmed2 = await window.app.showConfirm(
                'Final Warning',
                'This is your final warning. All accounts, posts, and settings will be permanently deleted. Continue?',
                'danger'
            );
            
            if (confirmed2) {
                try {
                    window.app.showLoading();
                    
                    const response = await fetch('/api/reset', { method: 'POST' });
                    const result = await response.json();
                    
                    if (result.success) {
                        window.app.showToast('Success', 'Application reset successfully. Reloading...', 'success');
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    } else {
                        throw new Error(result.message || 'Failed to reset application');
                    }
                } catch (error) {
                    console.error('Error resetting application:', error);
                    window.app.showToast('Error', error.message || 'Failed to reset application', 'error');
                } finally {
                    window.app.hideLoading();
                }
            }
        }
    }

    // Utility methods
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    formatTimeAgo(dateString) {
        if (!dateString) return 'Never';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
        if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
        if (diffInSeconds < 604800) return Math.floor(diffInSeconds / 86400) + ' days ago';
        return date.toLocaleDateString();
    }
}

// Initialize settings manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.settingsManager = new SettingsManager();
    
    // Handle settings actions
    document.addEventListener('click', function(e) {
        const action = e.target.closest('[data-action]');
        if (!action) return;
        
        e.preventDefault();
        
        const actionType = action.dataset.action;
        const itemId = action.dataset.id;
        
        switch (actionType) {
            case 'save-all-settings':
                window.settingsManager.saveAllSettings();
                break;
            case 'reset-settings':
                window.settingsManager.resetSettings();
                break;
            case 'test-openai':
                window.settingsManager.testOpenAI();
                break;
            case 'test-email':
                window.settingsManager.testEmail();
                break;
            case 'test-browser-notification':
                window.settingsManager.testBrowserNotification();
                break;
            case 'test-account':
                window.settingsManager.testAccount(itemId);
                break;
            case 'reconnect-account':
                window.settingsManager.reconnectAccount(itemId);
                break;
            case 'edit-account':
                window.settingsManager.editAccount(itemId);
                break;
            case 'disconnect-account':
                window.settingsManager.disconnectAccount(itemId);
                break;
            case 'export-data':
                window.settingsManager.exportData();
                break;
            case 'clear-logs':
                window.settingsManager.clearLogs();
                break;
            case 'check-updates':
                window.settingsManager.checkUpdates();
                break;
            case 'reset-app':
                window.settingsManager.resetApp();
                break;
        }
    });
});

