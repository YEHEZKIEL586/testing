"""
Social Media Automation V2 - Modern Web Application
Fitur: Instagram, Guest Posting, Edit Posts, XPath Bot Login
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

# Import custom modules
from bot.social_bot import SocialMediaBot
from services.openai_service import OpenAIService
from database.db_manager import DatabaseManager

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Initialize services
db_manager = DatabaseManager()
openai_service = OpenAIService()
social_bot = SocialMediaBot()

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard with statistics"""
    stats = db_manager.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/accounts')
def accounts():
    """Social media accounts management"""
    accounts = db_manager.get_all_accounts()
    return render_template('accounts.html', accounts=accounts)

@app.route('/guest-posting')
def guest_posting():
    """Guest posting management"""
    guest_sites = db_manager.get_guest_sites()
    return render_template('guest_posting.html', sites=guest_sites)

@app.route('/posts')
def posts():
    """Posts management and editing"""
    posts = db_manager.get_all_posts()
    return render_template('posts.html', posts=posts)

@app.route('/content')
def content():
    """Content management"""
    content_list = db_manager.get_content()
    return render_template('content.html', content=content_list)

@app.route('/automation')
def automation():
    """Automation control panel"""
    return render_template('automation.html')

@app.route('/settings')
def settings():
    """Application settings"""
    return render_template('settings.html')

# API Routes
@app.route('/api/accounts', methods=['GET', 'POST'])
def api_accounts():
    """API for account management"""
    if request.method == 'POST':
        data = request.json
        result = db_manager.add_account(
            platform=data['platform'],
            username=data['username'],
            email=data.get('email', ''),
            password=data['password'],
            proxy=data.get('proxy', ''),
            notes=data.get('notes', '')
        )
        return jsonify(result)
    
    accounts = db_manager.get_all_accounts()
    return jsonify({'accounts': accounts})

@app.route('/api/accounts/<int:account_id>', methods=['PUT', 'DELETE'])
def api_account_detail(account_id):
    """API for specific account operations"""
    if request.method == 'PUT':
        data = request.json
        result = db_manager.update_account(account_id, data)
        return jsonify(result)
    
    elif request.method == 'DELETE':
        result = db_manager.delete_account(account_id)
        return jsonify(result)

@app.route('/api/accounts/<int:account_id>/test', methods=['POST'])
def api_test_account(account_id):
    """Test account login"""
    account = db_manager.get_account(account_id)
    if not account:
        return jsonify({'success': False, 'message': 'Account not found'})
    
    result = social_bot.test_login(account)
    return jsonify(result)

@app.route('/api/guest-sites', methods=['GET', 'POST'])
def api_guest_sites():
    """API for guest posting sites"""
    if request.method == 'POST':
        data = request.json
        result = db_manager.add_guest_site(
            name=data['name'],
            url=data['url'],
            login_url=data['login_url'],
            username=data['username'],
            password=data['password'],
            post_url=data.get('post_url', ''),
            notes=data.get('notes', '')
        )
        return jsonify(result)
    
    sites = db_manager.get_guest_sites()
    return jsonify({'sites': sites})

@app.route('/api/guest-sites/<int:site_id>/test', methods=['POST'])
def api_test_guest_site(site_id):
    """Test guest site login"""
    site = db_manager.get_guest_site(site_id)
    if not site:
        return jsonify({'success': False, 'message': 'Site not found'})
    
    result = social_bot.test_guest_login(site)
    return jsonify(result)

@app.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    """API for posts management"""
    if request.method == 'POST':
        data = request.json
        
        # Generate content using OpenAI if needed
        if data.get('generate_content'):
            content = openai_service.generate_post_content(
                topic=data.get('topic', ''),
                platform=data.get('platform', ''),
                tone=data.get('tone', 'professional')
            )
            data['content'] = content
        
        result = db_manager.add_post(
            platform=data['platform'],
            content=data['content'],
            account_id=data.get('account_id'),
            guest_site_id=data.get('guest_site_id'),
            scheduled_time=data.get('scheduled_time'),
            image_path=data.get('image_path', ''),
            hashtags=data.get('hashtags', ''),
            status='draft'
        )
        return jsonify(result)
    
    posts = db_manager.get_all_posts()
    return jsonify({'posts': posts})

@app.route('/api/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def api_post_detail(post_id):
    """API for specific post operations"""
    if request.method == 'GET':
        post = db_manager.get_post(post_id)
        return jsonify({'post': post})
    
    elif request.method == 'PUT':
        data = request.json
        result = db_manager.update_post(post_id, data)
        return jsonify(result)
    
    elif request.method == 'DELETE':
        result = db_manager.delete_post(post_id)
        return jsonify(result)

@app.route('/api/posts/<int:post_id>/publish', methods=['POST'])
def api_publish_post(post_id):
    """Publish specific post"""
    post = db_manager.get_post(post_id)
    if not post:
        return jsonify({'success': False, 'message': 'Post not found'})
    
    result = social_bot.publish_post(post)
    
    # Update post status
    db_manager.update_post(post_id, {
        'status': 'published' if result['success'] else 'failed',
        'published_at': datetime.now().isoformat() if result['success'] else None,
        'error_message': result.get('message', '') if not result['success'] else ''
    })
    
    return jsonify(result)

@app.route('/api/content/generate', methods=['POST'])
def api_generate_content():
    """Generate content using OpenAI"""
    data = request.json
    
    content = openai_service.generate_post_content(
        topic=data.get('topic', ''),
        platform=data.get('platform', ''),
        tone=data.get('tone', 'professional'),
        length=data.get('length', 'medium')
    )
    
    return jsonify({'content': content})

@app.route('/api/content/scrape', methods=['POST'])
def api_scrape_content():
    """Scrape content from WordPress or other sources"""
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'})
    
    result = social_bot.scrape_content(url)
    
    if result['success']:
        # Save scraped content to database
        db_manager.add_content(
            title=result['title'],
            content=result['content'],
            source_url=url,
            scraped_at=datetime.now().isoformat()
        )
    
    return jsonify(result)

@app.route('/api/automation/start', methods=['POST'])
def api_start_automation():
    """Start automation process"""
    data = request.json
    
    # Get pending posts
    pending_posts = db_manager.get_posts_by_status('pending')
    
    results = []
    for post in pending_posts:
        result = social_bot.publish_post(post)
        results.append({
            'post_id': post['id'],
            'success': result['success'],
            'message': result['message']
        })
        
        # Update post status
        db_manager.update_post(post['id'], {
            'status': 'published' if result['success'] else 'failed',
            'published_at': datetime.now().isoformat() if result['success'] else None,
            'error_message': result.get('message', '') if not result['success'] else ''
        })
    
    return jsonify({
        'success': True,
        'processed': len(results),
        'results': results
    })

@app.route('/api/dashboard/stats')
def api_dashboard_stats():
    """Get dashboard statistics"""
    stats = db_manager.get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    db_manager.init_database()
    
    # Run application
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🚀 Social Media Automation V2 Starting...")
    print(f"📱 Dashboard: http://{host}:{port}")
    print(f"🏥 Health Check: http://{host}:{port}/api/health")
    print("=" * 50)
    
    app.run(host=host, port=port, debug=debug)

