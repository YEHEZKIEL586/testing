import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
import os

class DatabaseManager:
    def __init__(self, db_path='social_automation.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database with all required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Social media accounts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                platform TEXT NOT NULL,
                account_name TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                last_used TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Guest posting sites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guest_posting_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                login_url TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                cms_type TEXT DEFAULT 'wordpress',
                status TEXT DEFAULT 'pending',
                last_used TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                source_type TEXT DEFAULT 'manual',
                tags TEXT,
                category TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id INTEGER,
                account_id INTEGER,
                guest_site_id INTEGER,
                title TEXT,
                content TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                scheduled_at TIMESTAMP,
                published_at TIMESTAMP,
                post_url TEXT,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (content_id) REFERENCES content (id),
                FOREIGN KEY (account_id) REFERENCES accounts (id),
                FOREIGN KEY (guest_site_id) REFERENCES guest_posting_sites (id)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                setting_key TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                setting_type TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, setting_key)
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER,
                extra_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Automation schedules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_config TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_platform ON accounts(platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_scheduled_at ON posts(scheduled_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_status ON content(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_created_at ON logs(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(setting_key)')
        
        conn.commit()
        conn.close()
        
        # Insert default settings
        self.insert_default_settings()
    
    def insert_default_settings(self):
        """Insert default application settings"""
        default_settings = {
            'app_name': 'Social Media Automation V2',
            'language': 'en',
            'timezone': 'Asia/Jakarta',
            'date_format': 'DD/MM/YYYY',
            'theme': 'light',
            'default_tone': 'professional',
            'default_length': 'medium',
            'auto_hashtags': 'true',
            'auto_optimize': 'true',
            'save_drafts': 'true',
            'rate_limiting': 'moderate',
            'user_agent_rotation': 'enabled',
            'human_behavior': 'true',
            'headless_mode': 'true',
            'data_retention': '90',
            'encrypt_passwords': 'true',
            'concurrent_posts': '3',
            'request_timeout': '30',
            'retry_attempts': '3',
            'cache_duration': '60',
            'log_level': 'INFO',
            'debug_mode': 'false',
            'verbose_logging': 'false',
            'save_screenshots': 'true'
        }
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for key, value in default_settings.items():
            cursor.execute('''
                INSERT OR IGNORE INTO settings (user_id, setting_key, setting_value, setting_type)
                VALUES (?, ?, ?, ?)
            ''', (1, key, value, 'general'))
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # User management
    def create_user(self, username, email, password):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return user_id
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return dict(user) if user else None
    
    # Account management
    def add_account(self, user_id, platform, account_name, username, password, notes=''):
        """Add social media account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO accounts (user_id, platform, account_name, username, password_hash, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, platform, account_name, username, password_hash, notes))
        
        account_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return account_id
    
    def get_accounts(self, user_id=None):
        """Get all accounts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM accounts WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        else:
            cursor.execute('SELECT * FROM accounts ORDER BY created_at DESC')
        
        accounts = cursor.fetchall()
        conn.close()
        
        return [dict(account) for account in accounts]
    
    def get_account(self, account_id):
        """Get account by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        
        conn.close()
        return dict(account) if account else None
    
    def update_account_status(self, account_id, status):
        """Update account status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE accounts 
            SET status = ?, last_used = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, account_id))
        
        conn.commit()
        conn.close()
    
    def delete_account(self, account_id):
        """Delete account"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM accounts WHERE id = ?', (account_id,))
        
        conn.commit()
        conn.close()
    
    # Guest posting sites management
    def add_guest_posting_site(self, user_id, name, url, login_url, username, password, cms_type='wordpress', notes=''):
        """Add guest posting site"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            INSERT INTO guest_posting_sites (user_id, name, url, login_url, username, password_hash, cms_type, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, url, login_url, username, password_hash, cms_type, notes))
        
        site_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return site_id
    
    def get_guest_posting_sites(self, user_id=None):
        """Get all guest posting sites"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('SELECT * FROM guest_posting_sites WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        else:
            cursor.execute('SELECT * FROM guest_posting_sites ORDER BY created_at DESC')
        
        sites = cursor.fetchall()
        conn.close()
        
        return [dict(site) for site in sites]
    
    def get_guest_posting_site(self, site_id):
        """Get guest posting site by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM guest_posting_sites WHERE id = ?', (site_id,))
        site = cursor.fetchone()
        
        conn.close()
        return dict(site) if site else None
    
    # Content management
    def add_content(self, user_id, title, content, source_url='', source_type='manual', tags='', category=''):
        """Add content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content (user_id, title, content, source_url, source_type, tags, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, content, source_url, source_type, tags, category))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return content_id
    
    def get_content(self, user_id=None, status=None):
        """Get content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM content'
        params = []
        
        conditions = []
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        
        if status:
            conditions.append('status = ?')
            params.append(status)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        content = cursor.fetchall()
        
        conn.close()
        return [dict(item) for item in content]
    
    def get_content_by_id(self, content_id):
        """Get content by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        content = cursor.fetchone()
        
        conn.close()
        return dict(content) if content else None
    
    def update_content(self, content_id, title=None, content=None, status=None, tags=None, category=None):
        """Update content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        
        if status is not None:
            updates.append('status = ?')
            params.append(status)
        
        if tags is not None:
            updates.append('tags = ?')
            params.append(tags)
        
        if category is not None:
            updates.append('category = ?')
            params.append(category)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            params.append(content_id)
            
            query = f'UPDATE content SET {", ".join(updates)} WHERE id = ?'
            cursor.execute(query, params)
            
            conn.commit()
        
        conn.close()
    
    # Posts management
    def add_post(self, user_id, content_id, account_id, title, content, platform, status='draft', scheduled_at=None, guest_site_id=None):
        """Add post"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO posts (user_id, content_id, account_id, guest_site_id, title, content, platform, status, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, content_id, account_id, guest_site_id, title, content, platform, status, scheduled_at))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return post_id
    
    def get_posts(self, user_id=None, status=None, platform=None, limit=None):
        """Get posts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.*, a.account_name, a.platform as account_platform, c.title as content_title
            FROM posts p
            LEFT JOIN accounts a ON p.account_id = a.id
            LEFT JOIN content c ON p.content_id = c.id
        '''
        params = []
        
        conditions = []
        if user_id:
            conditions.append('p.user_id = ?')
            params.append(user_id)
        
        if status:
            conditions.append('p.status = ?')
            params.append(status)
        
        if platform:
            conditions.append('p.platform = ?')
            params.append(platform)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += ' ORDER BY p.created_at DESC'
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, params)
        posts = cursor.fetchall()
        
        conn.close()
        return [dict(post) for post in posts]
    
    def get_post(self, post_id):
        """Get post by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, a.account_name, a.platform as account_platform, c.title as content_title
            FROM posts p
            LEFT JOIN accounts a ON p.account_id = a.id
            LEFT JOIN content c ON p.content_id = c.id
            WHERE p.id = ?
        ''', (post_id,))
        
        post = cursor.fetchone()
        conn.close()
        
        return dict(post) if post else None
    
    def update_post_status(self, post_id, status, error_message=None, post_url=None):
        """Update post status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = ['status = ?', 'updated_at = CURRENT_TIMESTAMP']
        params = [status]
        
        if status == 'published':
            updates.append('published_at = CURRENT_TIMESTAMP')
        
        if error_message:
            updates.append('error_message = ?')
            params.append(error_message)
        
        if post_url:
            updates.append('post_url = ?')
            params.append(post_url)
        
        params.append(post_id)
        
        query = f'UPDATE posts SET {", ".join(updates)} WHERE id = ?'
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
    
    def increment_retry_count(self, post_id):
        """Increment post retry count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE posts 
            SET retry_count = retry_count + 1, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (post_id,))
        
        conn.commit()
        conn.close()
    
    # Settings management
    def get_settings(self, user_id=1):
        """Get all settings"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_key, setting_value FROM settings WHERE user_id = ?', (user_id,))
        settings = cursor.fetchall()
        
        conn.close()
        
        return {setting['setting_key']: setting['setting_value'] for setting in settings}
    
    def save_settings(self, setting_type, data, user_id=1):
        """Save settings by type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for key, value in data.items():
            cursor.execute('''
                INSERT OR REPLACE INTO settings (user_id, setting_key, setting_value, setting_type, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, key, str(value), setting_type))
        
        conn.commit()
        conn.close()
    
    def auto_save_settings(self, data, user_id=1):
        """Auto-save settings"""
        self.save_settings('auto_save', data, user_id)
    
    def reset_settings(self, user_id=1):
        """Reset settings to defaults"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM settings WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        self.insert_default_settings()
    
    # Dashboard stats
    def get_dashboard_stats(self, user_id=1):
        """Get dashboard statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total accounts
        cursor.execute('SELECT COUNT(*) as count FROM accounts WHERE user_id = ?', (user_id,))
        total_accounts = cursor.fetchone()['count']
        
        # Total posts
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE user_id = ?', (user_id,))
        total_posts = cursor.fetchone()['count']
        
        # Success rate
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published
            FROM posts WHERE user_id = ?
        ''', (user_id,))
        
        post_stats = cursor.fetchone()
        success_rate = (post_stats['published'] / post_stats['total'] * 100) if post_stats['total'] > 0 else 0
        
        # Pending posts
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE user_id = ? AND status = ?', (user_id, 'scheduled'))
        pending_posts = cursor.fetchone()['count']
        
        # Recent posts
        cursor.execute('''
            SELECT p.*, a.account_name, a.platform as account_platform
            FROM posts p
            LEFT JOIN accounts a ON p.account_id = a.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
            LIMIT 10
        ''', (user_id,))
        
        recent_posts = [dict(post) for post in cursor.fetchall()]
        
        # Platform stats
        cursor.execute('''
            SELECT 
                platform,
                COUNT(*) as posts,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published
            FROM posts 
            WHERE user_id = ?
            GROUP BY platform
        ''', (user_id,))
        
        platform_stats = []
        for stat in cursor.fetchall():
            platform_stats.append({
                'platform': stat['platform'],
                'posts': stat['posts'],
                'success_rate': (stat['published'] / stat['posts'] * 100) if stat['posts'] > 0 else 0,
                'trend': 0  # Would calculate based on historical data
            })
        
        conn.close()
        
        return {
            'total_accounts': total_accounts,
            'total_posts': total_posts,
            'success_rate': round(success_rate, 1),
            'pending_posts': pending_posts,
            'recent_posts': recent_posts,
            'platform_stats': platform_stats,
            'trends': {
                'accounts': {'direction': 'up', 'percentage': 5},
                'posts': {'direction': 'up', 'percentage': 12},
                'success_rate': {'direction': 'up', 'percentage': 3}
            }
        }
    
    def get_chart_data(self, user_id=1):
        """Get chart data for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Posts over time (last 7 days)
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM posts 
            WHERE user_id = ? AND created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (user_id,))
        
        posts_data = cursor.fetchall()
        
        # Platform distribution
        cursor.execute('''
            SELECT platform, COUNT(*) as count
            FROM posts 
            WHERE user_id = ?
            GROUP BY platform
        ''', (user_id,))
        
        platform_data = cursor.fetchall()
        
        # Success rate by day
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published
            FROM posts 
            WHERE user_id = ? AND created_at >= date('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (user_id,))
        
        success_data = cursor.fetchall()
        
        conn.close()
        
        return {
            'posts': {
                'labels': [row['date'] for row in posts_data],
                'data': [row['count'] for row in posts_data]
            },
            'platforms': {
                'labels': [row['platform'].title() for row in platform_data],
                'data': [row['count'] for row in platform_data]
            },
            'success_rate': {
                'labels': [row['date'] for row in success_data],
                'data': [(row['published'] / row['total'] * 100) if row['total'] > 0 else 0 for row in success_data]
            }
        }
    
    # Logging
    def add_log(self, user_id, level, message, module=None, function=None, line_number=None, extra_data=None):
        """Add log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (user_id, level, message, module, function, line_number, extra_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, level, message, module, function, line_number, json.dumps(extra_data) if extra_data else None))
        
        conn.commit()
        conn.close()
    
    def get_logs(self, user_id=None, level=None, limit=100):
        """Get logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM logs'
        params = []
        
        conditions = []
        if user_id:
            conditions.append('user_id = ?')
            params.append(user_id)
        
        if level:
            conditions.append('level = ?')
            params.append(level)
        
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        
        query += f' ORDER BY created_at DESC LIMIT {limit}'
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        conn.close()
        return [dict(log) for log in logs]
    
    def clear_old_logs(self, days=30):
        """Clear logs older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM logs 
            WHERE created_at < date('now', '-{} days')
        '''.format(days))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
    # Data export/import
    def export_all_data(self, user_id=1):
        """Export all user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data = {
            'export_date': datetime.now().isoformat(),
            'user_id': user_id,
            'accounts': [],
            'guest_posting_sites': [],
            'content': [],
            'posts': [],
            'settings': {},
            'logs': []
        }
        
        # Export accounts (without passwords)
        cursor.execute('SELECT id, platform, account_name, username, status, notes, created_at FROM accounts WHERE user_id = ?', (user_id,))
        data['accounts'] = [dict(row) for row in cursor.fetchall()]
        
        # Export guest posting sites (without passwords)
        cursor.execute('SELECT id, name, url, login_url, username, cms_type, status, notes, created_at FROM guest_posting_sites WHERE user_id = ?', (user_id,))
        data['guest_posting_sites'] = [dict(row) for row in cursor.fetchall()]
        
        # Export content
        cursor.execute('SELECT * FROM content WHERE user_id = ?', (user_id,))
        data['content'] = [dict(row) for row in cursor.fetchall()]
        
        # Export posts
        cursor.execute('SELECT * FROM posts WHERE user_id = ?', (user_id,))
        data['posts'] = [dict(row) for row in cursor.fetchall()]
        
        # Export settings
        cursor.execute('SELECT setting_key, setting_value FROM settings WHERE user_id = ?', (user_id,))
        data['settings'] = {row['setting_key']: row['setting_value'] for row in cursor.fetchall()}
        
        # Export recent logs
        cursor.execute('SELECT * FROM logs WHERE user_id = ? ORDER BY created_at DESC LIMIT 1000', (user_id,))
        data['logs'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return data
    
    def reset_database(self):
        """Reset entire database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Drop all tables
        for table in tables:
            cursor.execute(f'DROP TABLE IF EXISTS {table["name"]}')
        
        conn.commit()
        conn.close()
        
        # Reinitialize database
        self.init_database()

