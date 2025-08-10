"""
Database Manager untuk Social Media Automation V2
Menggunakan SQLite untuk kemudahan deployment di Windows
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = 'database/social_automation.db'):
        self.db_path = db_path
        self.ensure_db_directory()
    
    def ensure_db_directory(self):
        """Pastikan direktori database ada"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Dapatkan koneksi database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Untuk akses kolom by name
        return conn
    
    def init_database(self):
        """Inisialisasi database dengan tabel-tabel yang diperlukan"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabel untuk akun social media
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                email TEXT,
                password TEXT NOT NULL,
                proxy TEXT,
                notes TEXT,
                status TEXT DEFAULT 'active',
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk guest posting sites
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guest_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                login_url TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                post_url TEXT,
                notes TEXT,
                status TEXT DEFAULT 'active',
                last_used TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                account_id INTEGER,
                guest_site_id INTEGER,
                title TEXT,
                image_path TEXT,
                hashtags TEXT,
                status TEXT DEFAULT 'draft',
                scheduled_time TIMESTAMP,
                published_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES social_accounts (id),
                FOREIGN KEY (guest_site_id) REFERENCES guest_sites (id)
            )
        ''')
        
        # Tabel untuk content yang di-scrape
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraped_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source_url TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_count INTEGER DEFAULT 0,
                tags TEXT
            )
        ''')
        
        # Tabel untuk automation logs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                target_id INTEGER,
                target_type TEXT,
                status TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk settings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    # Social Accounts Methods
    def add_account(self, platform: str, username: str, email: str, password: str, 
                   proxy: str = '', notes: str = '') -> Dict:
        """Tambah akun social media baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO social_accounts (platform, username, email, password, proxy, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (platform, username, email, password, proxy, notes))
            
            account_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Account added successfully',
                'account_id': account_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding account: {str(e)}'
            }
    
    def get_all_accounts(self) -> List[Dict]:
        """Dapatkan semua akun social media"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM social_accounts ORDER BY created_at DESC')
        accounts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return accounts
    
    def get_account(self, account_id: int) -> Optional[Dict]:
        """Dapatkan akun berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM social_accounts WHERE id = ?', (account_id,))
        account = cursor.fetchone()
        
        conn.close()
        return dict(account) if account else None
    
    def update_account(self, account_id: int, data: Dict) -> Dict:
        """Update akun social media"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id':
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            values.append(datetime.now().isoformat())
            values.append(account_id)
            
            query = f"UPDATE social_accounts SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Account updated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error updating account: {str(e)}'}
    
    def delete_account(self, account_id: int) -> Dict:
        """Hapus akun social media"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM social_accounts WHERE id = ?', (account_id,))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Account deleted successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error deleting account: {str(e)}'}
    
    # Guest Sites Methods
    def add_guest_site(self, name: str, url: str, login_url: str, username: str, 
                      password: str, post_url: str = '', notes: str = '') -> Dict:
        """Tambah guest posting site baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO guest_sites (name, url, login_url, username, password, post_url, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, url, login_url, username, password, post_url, notes))
            
            site_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Guest site added successfully',
                'site_id': site_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding guest site: {str(e)}'
            }
    
    def get_guest_sites(self) -> List[Dict]:
        """Dapatkan semua guest posting sites"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM guest_sites ORDER BY created_at DESC')
        sites = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return sites
    
    def get_guest_site(self, site_id: int) -> Optional[Dict]:
        """Dapatkan guest site berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM guest_sites WHERE id = ?', (site_id,))
        site = cursor.fetchone()
        
        conn.close()
        return dict(site) if site else None
    
    # Posts Methods
    def add_post(self, platform: str, content: str, account_id: int = None, 
                guest_site_id: int = None, scheduled_time: str = None, 
                image_path: str = '', hashtags: str = '', status: str = 'draft',
                title: str = '') -> Dict:
        """Tambah post baru"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO posts (platform, content, account_id, guest_site_id, 
                                 scheduled_time, image_path, hashtags, status, title)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (platform, content, account_id, guest_site_id, scheduled_time, 
                  image_path, hashtags, status, title))
            
            post_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Post added successfully',
                'post_id': post_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding post: {str(e)}'
            }
    
    def get_all_posts(self) -> List[Dict]:
        """Dapatkan semua posts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, sa.username as account_username, gs.name as guest_site_name
            FROM posts p
            LEFT JOIN social_accounts sa ON p.account_id = sa.id
            LEFT JOIN guest_sites gs ON p.guest_site_id = gs.id
            ORDER BY p.created_at DESC
        ''')
        posts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return posts
    
    def get_post(self, post_id: int) -> Optional[Dict]:
        """Dapatkan post berdasarkan ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, sa.username as account_username, gs.name as guest_site_name
            FROM posts p
            LEFT JOIN social_accounts sa ON p.account_id = sa.id
            LEFT JOIN guest_sites gs ON p.guest_site_id = gs.id
            WHERE p.id = ?
        ''', (post_id,))
        post = cursor.fetchone()
        
        conn.close()
        return dict(post) if post else None
    
    def get_posts_by_status(self, status: str) -> List[Dict]:
        """Dapatkan posts berdasarkan status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, sa.username as account_username, gs.name as guest_site_name
            FROM posts p
            LEFT JOIN social_accounts sa ON p.account_id = sa.id
            LEFT JOIN guest_sites gs ON p.guest_site_id = gs.id
            WHERE p.status = ?
            ORDER BY p.created_at DESC
        ''', (status,))
        posts = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return posts
    
    def update_post(self, post_id: int, data: Dict) -> Dict:
        """Update post"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build dynamic update query
            fields = []
            values = []
            for key, value in data.items():
                if key != 'id':
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            values.append(datetime.now().isoformat())
            values.append(post_id)
            
            query = f"UPDATE posts SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Post updated successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error updating post: {str(e)}'}
    
    def delete_post(self, post_id: int) -> Dict:
        """Hapus post"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Post deleted successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Error deleting post: {str(e)}'}
    
    # Content Methods
    def add_content(self, title: str, content: str, source_url: str = '', 
                   scraped_at: str = None, tags: str = '') -> Dict:
        """Tambah scraped content"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if not scraped_at:
                scraped_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO scraped_content (title, content, source_url, scraped_at, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, source_url, scraped_at, tags))
            
            content_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Content added successfully',
                'content_id': content_id
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding content: {str(e)}'
            }
    
    def get_content(self) -> List[Dict]:
        """Dapatkan semua scraped content"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scraped_content ORDER BY scraped_at DESC')
        content = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return content
    
    # Dashboard Stats
    def get_dashboard_stats(self) -> Dict:
        """Dapatkan statistik untuk dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total accounts
        cursor.execute('SELECT COUNT(*) as count FROM social_accounts WHERE status = "active"')
        total_accounts = cursor.fetchone()['count']
        
        # Total guest sites
        cursor.execute('SELECT COUNT(*) as count FROM guest_sites WHERE status = "active"')
        total_guest_sites = cursor.fetchone()['count']
        
        # Total posts
        cursor.execute('SELECT COUNT(*) as count FROM posts')
        total_posts = cursor.fetchone()['count']
        
        # Published posts
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE status = "published"')
        published_posts = cursor.fetchone()['count']
        
        # Pending posts
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE status = "pending"')
        pending_posts = cursor.fetchone()['count']
        
        # Failed posts
        cursor.execute('SELECT COUNT(*) as count FROM posts WHERE status = "failed"')
        failed_posts = cursor.fetchone()['count']
        
        # Posts by platform
        cursor.execute('''
            SELECT platform, COUNT(*) as count 
            FROM posts 
            GROUP BY platform
        ''')
        platform_stats = {row['platform']: row['count'] for row in cursor.fetchall()}
        
        # Recent activity
        cursor.execute('''
            SELECT * FROM automation_logs 
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        recent_activity = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            'total_accounts': total_accounts,
            'total_guest_sites': total_guest_sites,
            'total_posts': total_posts,
            'published_posts': published_posts,
            'pending_posts': pending_posts,
            'failed_posts': failed_posts,
            'platform_stats': platform_stats,
            'recent_activity': recent_activity,
            'success_rate': round((published_posts / total_posts * 100) if total_posts > 0 else 0, 1)
        }
    
    # Logging
    def log_action(self, action: str, target_id: int = None, target_type: str = None, 
                  status: str = 'success', message: str = '') -> None:
        """Log automation action"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO automation_logs (action, target_id, target_type, status, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (action, target_id, target_type, status, message))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error logging action: {e}")
    
    # Settings
    def get_setting(self, key: str, default_value: str = None) -> str:
        """Dapatkan setting berdasarkan key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        return result['value'] if result else default_value
    
    def set_setting(self, key: str, value: str, description: str = '') -> None:
        """Set setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, description, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (key, value, description, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()

