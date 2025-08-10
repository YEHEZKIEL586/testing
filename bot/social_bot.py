"""
Social Media Bot dengan XPath dan Flexible Login
Mendukung Facebook, Twitter, LinkedIn, Instagram, dan Guest Posting
"""

import time
import random
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import json

class SocialMediaBot:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.current_platform = None
        
        # XPath selectors untuk berbagai platform
        self.selectors = {
            'facebook': {
                'login': {
                    'email': "//input[@id='email' or @name='email' or @type='email']",
                    'password': "//input[@id='pass' or @name='pass' or @type='password']",
                    'submit': "//button[@name='login' or @type='submit' or contains(@class, 'login')]"
                },
                'post': {
                    'composer': "//div[@role='textbox' or contains(@aria-label, 'What') or contains(@data-text, 'What')]",
                    'submit': "//div[@role='button' and contains(text(), 'Post')] | //button[contains(text(), 'Post')]",
                    'photo_button': "//div[@aria-label='Photo/video' or contains(@aria-label, 'Photo')]",
                    'file_input': "//input[@type='file' and @accept]"
                }
            },
            'twitter': {
                'login': {
                    'email': "//input[@name='text' or @autocomplete='username' or contains(@placeholder, 'email')]",
                    'password': "//input[@name='password' or @type='password']",
                    'submit': "//div[@role='button' and contains(text(), 'Log in')] | //button[@type='submit']",
                    'next': "//div[@role='button' and contains(text(), 'Next')] | //button[contains(text(), 'Next')]"
                },
                'post': {
                    'composer': "//div[@aria-label='Tweet text' or @contenteditable='true']",
                    'submit': "//div[@data-testid='tweetButtonInline'] | //button[@data-testid='tweetButton']",
                    'media_button': "//div[@aria-label='Add photos or video']",
                    'file_input': "//input[@type='file']"
                }
            },
            'linkedin': {
                'login': {
                    'email': "//input[@id='username' or @name='session_key']",
                    'password': "//input[@id='password' or @name='session_password']",
                    'submit': "//button[@type='submit' or contains(@class, 'sign-in')]"
                },
                'post': {
                    'start_post': "//button[contains(@aria-label, 'Start a post')]",
                    'composer': "//div[@contenteditable='true' or contains(@class, 'ql-editor')]",
                    'submit': "//button[contains(@aria-label, 'Post') or contains(text(), 'Post')]",
                    'media_button': "//button[@aria-label='Add media']"
                }
            },
            'instagram': {
                'login': {
                    'email': "//input[@name='username' or @aria-label='Phone number, username, or email']",
                    'password': "//input[@name='password' or @aria-label='Password']",
                    'submit': "//button[@type='submit' or contains(text(), 'Log in')]"
                },
                'post': {
                    'new_post': "//div[@role='menuitem' and contains(@aria-label, 'New post')] | //*[contains(@aria-label, 'New post')]",
                    'select_files': "//input[@type='file' and @accept]",
                    'next': "//button[contains(text(), 'Next')]",
                    'caption': "//textarea[@aria-label='Write a caption...']",
                    'share': "//button[contains(text(), 'Share')]"
                }
            }
        }
        
        # User agents untuk rotasi
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
    
    def setup_driver(self, headless: bool = False, proxy: str = None) -> bool:
        """Setup Chrome WebDriver dengan konfigurasi optimal"""
        try:
            options = Options()
            
            # Basic options
            if headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User agent rotation
            user_agent = random.choice(self.user_agents)
            options.add_argument(f'--user-agent={user_agent}')
            
            # Window size
            options.add_argument('--window-size=1366,768')
            
            # Proxy setup
            if proxy:
                options.add_argument(f'--proxy-server={proxy}')
            
            # Disable images untuk speed (optional)
            # options.add_argument('--disable-images')
            
            # Try to find Chrome driver
            chrome_paths = [
                'chromedriver.exe',  # Windows
                '/usr/local/bin/chromedriver',  # Linux/Mac
                '/usr/bin/chromedriver',
                'C:\\chromedriver\\chromedriver.exe'  # Windows alternative
            ]
            
            driver_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    driver_path = path
                    break
            
            if driver_path:
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                # Try without specifying path (system PATH)
                self.driver = webdriver.Chrome(options=options)
            
            # Anti-detection measures
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up WebDriver: {e}")
            return False
    
    def close_driver(self):
        """Close WebDriver dengan aman"""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ WebDriver closed successfully")
            except Exception as e:
                print(f"⚠️  Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None
    
    def human_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        """Delay seperti manusia"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def human_type(self, element, text: str, delay_range: Tuple[float, float] = (0.05, 0.15)):
        """Type text seperti manusia"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def find_element_flexible(self, xpath_list: List[str], timeout: int = 10):
        """Find element dengan multiple XPath fallbacks"""
        for xpath in xpath_list if isinstance(xpath_list, list) else [xpath_list]:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return element
            except TimeoutException:
                continue
        
        raise TimeoutException(f"Could not find element with any of the XPaths: {xpath_list}")
    
    def click_element_safe(self, element):
        """Click element dengan retry dan scroll"""
        try:
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.human_delay(0.5, 1.0)
            
            # Try normal click
            element.click()
            return True
        except Exception:
            try:
                # Try JavaScript click
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                try:
                    # Try ActionChains click
                    ActionChains(self.driver).move_to_element(element).click().perform()
                    return True
                except Exception as e:
                    print(f"Failed to click element: {e}")
                    return False
    
    def test_login(self, account: Dict) -> Dict:
        """Test login untuk akun social media"""
        platform = account['platform'].lower()
        
        if not self.setup_driver():
            return {'success': False, 'message': 'Failed to setup WebDriver'}
        
        try:
            if platform == 'facebook':
                return self._test_facebook_login(account)
            elif platform == 'twitter':
                return self._test_twitter_login(account)
            elif platform == 'linkedin':
                return self._test_linkedin_login(account)
            elif platform == 'instagram':
                return self._test_instagram_login(account)
            else:
                return {'success': False, 'message': f'Platform {platform} not supported'}
        
        except Exception as e:
            return {'success': False, 'message': f'Login test failed: {str(e)}'}
        
        finally:
            self.close_driver()
    
    def _test_facebook_login(self, account: Dict) -> Dict:
        """Test Facebook login"""
        try:
            self.driver.get('https://www.facebook.com/login')
            self.human_delay(2, 4)
            
            # Find email field
            email_field = self.find_element_flexible([
                self.selectors['facebook']['login']['email'],
                "//input[@type='email']",
                "//input[@placeholder='Email or phone number']"
            ])
            
            self.human_type(email_field, account['email'] or account['username'])
            self.human_delay(1, 2)
            
            # Find password field
            password_field = self.find_element_flexible([
                self.selectors['facebook']['login']['password'],
                "//input[@type='password']"
            ])
            
            self.human_type(password_field, account['password'])
            self.human_delay(1, 2)
            
            # Find and click login button
            login_button = self.find_element_flexible([
                self.selectors['facebook']['login']['submit'],
                "//button[@type='submit']",
                "//input[@type='submit']"
            ])
            
            self.click_element_safe(login_button)
            self.human_delay(5, 8)
            
            # Check if login successful
            current_url = self.driver.current_url
            if 'login' not in current_url and 'checkpoint' not in current_url:
                return {'success': True, 'message': 'Facebook login successful'}
            else:
                return {'success': False, 'message': 'Facebook login failed or requires verification'}
        
        except Exception as e:
            return {'success': False, 'message': f'Facebook login error: {str(e)}'}
    
    def _test_twitter_login(self, account: Dict) -> Dict:
        """Test Twitter login"""
        try:
            self.driver.get('https://twitter.com/i/flow/login')
            self.human_delay(3, 5)
            
            # Email/username field
            email_field = self.find_element_flexible([
                self.selectors['twitter']['login']['email'],
                "//input[@autocomplete='username']"
            ])
            
            self.human_type(email_field, account['email'] or account['username'])
            self.human_delay(1, 2)
            
            # Next button
            next_button = self.find_element_flexible([
                self.selectors['twitter']['login']['next'],
                "//div[@role='button' and contains(text(), 'Next')]"
            ])
            
            self.click_element_safe(next_button)
            self.human_delay(2, 4)
            
            # Password field
            password_field = self.find_element_flexible([
                self.selectors['twitter']['login']['password'],
                "//input[@type='password']"
            ])
            
            self.human_type(password_field, account['password'])
            self.human_delay(1, 2)
            
            # Login button
            login_button = self.find_element_flexible([
                self.selectors['twitter']['login']['submit'],
                "//div[@role='button' and contains(text(), 'Log in')]"
            ])
            
            self.click_element_safe(login_button)
            self.human_delay(5, 8)
            
            # Check success
            current_url = self.driver.current_url
            if 'home' in current_url or 'twitter.com' in current_url and 'login' not in current_url:
                return {'success': True, 'message': 'Twitter login successful'}
            else:
                return {'success': False, 'message': 'Twitter login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'Twitter login error: {str(e)}'}
    
    def _test_linkedin_login(self, account: Dict) -> Dict:
        """Test LinkedIn login"""
        try:
            self.driver.get('https://www.linkedin.com/login')
            self.human_delay(2, 4)
            
            # Email field
            email_field = self.find_element_flexible([
                self.selectors['linkedin']['login']['email'],
                "//input[@type='email']"
            ])
            
            self.human_type(email_field, account['email'] or account['username'])
            self.human_delay(1, 2)
            
            # Password field
            password_field = self.find_element_flexible([
                self.selectors['linkedin']['login']['password'],
                "//input[@type='password']"
            ])
            
            self.human_type(password_field, account['password'])
            self.human_delay(1, 2)
            
            # Login button
            login_button = self.find_element_flexible([
                self.selectors['linkedin']['login']['submit'],
                "//button[@type='submit']"
            ])
            
            self.click_element_safe(login_button)
            self.human_delay(5, 8)
            
            # Check success
            current_url = self.driver.current_url
            if 'feed' in current_url or ('linkedin.com' in current_url and 'login' not in current_url):
                return {'success': True, 'message': 'LinkedIn login successful'}
            else:
                return {'success': False, 'message': 'LinkedIn login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'LinkedIn login error: {str(e)}'}
    
    def _test_instagram_login(self, account: Dict) -> Dict:
        """Test Instagram login"""
        try:
            self.driver.get('https://www.instagram.com/accounts/login/')
            self.human_delay(3, 5)
            
            # Username field
            username_field = self.find_element_flexible([
                self.selectors['instagram']['login']['email'],
                "//input[@name='username']"
            ])
            
            self.human_type(username_field, account['username'])
            self.human_delay(1, 2)
            
            # Password field
            password_field = self.find_element_flexible([
                self.selectors['instagram']['login']['password'],
                "//input[@name='password']"
            ])
            
            self.human_type(password_field, account['password'])
            self.human_delay(1, 2)
            
            # Login button
            login_button = self.find_element_flexible([
                self.selectors['instagram']['login']['submit'],
                "//button[@type='submit']"
            ])
            
            self.click_element_safe(login_button)
            self.human_delay(5, 8)
            
            # Check success
            current_url = self.driver.current_url
            if 'instagram.com' in current_url and 'login' not in current_url:
                return {'success': True, 'message': 'Instagram login successful'}
            else:
                return {'success': False, 'message': 'Instagram login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram login error: {str(e)}'}
    
    def test_guest_login(self, site: Dict) -> Dict:
        """Test login untuk guest posting site"""
        if not self.setup_driver():
            return {'success': False, 'message': 'Failed to setup WebDriver'}
        
        try:
            self.driver.get(site['login_url'])
            self.human_delay(3, 5)
            
            # Try common login field selectors
            username_selectors = [
                "//input[@name='username' or @name='user' or @name='email']",
                "//input[@type='email']",
                "//input[@id='username' or @id='user' or @id='email']",
                "//input[contains(@placeholder, 'username') or contains(@placeholder, 'email')]"
            ]
            
            password_selectors = [
                "//input[@name='password' or @name='pass']",
                "//input[@type='password']",
                "//input[@id='password' or @id='pass']"
            ]
            
            submit_selectors = [
                "//button[@type='submit']",
                "//input[@type='submit']",
                "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]",
                "//input[contains(@value, 'Login') or contains(@value, 'Sign in')]"
            ]
            
            # Find and fill username
            username_field = self.find_element_flexible(username_selectors)
            self.human_type(username_field, site['username'])
            self.human_delay(1, 2)
            
            # Find and fill password
            password_field = self.find_element_flexible(password_selectors)
            self.human_type(password_field, site['password'])
            self.human_delay(1, 2)
            
            # Find and click submit
            submit_button = self.find_element_flexible(submit_selectors)
            self.click_element_safe(submit_button)
            self.human_delay(5, 8)
            
            # Check if login successful (basic check)
            current_url = self.driver.current_url
            if current_url != site['login_url'] and 'login' not in current_url.lower():
                return {'success': True, 'message': 'Guest site login successful'}
            else:
                return {'success': False, 'message': 'Guest site login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'Guest site login error: {str(e)}'}
        
        finally:
            self.close_driver()
    
    def publish_post(self, post: Dict) -> Dict:
        """Publish post ke platform yang ditentukan"""
        platform = post['platform'].lower()
        
        if not self.setup_driver():
            return {'success': False, 'message': 'Failed to setup WebDriver'}
        
        try:
            if platform == 'facebook':
                return self._publish_facebook_post(post)
            elif platform == 'twitter':
                return self._publish_twitter_post(post)
            elif platform == 'linkedin':
                return self._publish_linkedin_post(post)
            elif platform == 'instagram':
                return self._publish_instagram_post(post)
            elif platform == 'guest_post':
                return self._publish_guest_post(post)
            else:
                return {'success': False, 'message': f'Platform {platform} not supported'}
        
        except Exception as e:
            return {'success': False, 'message': f'Publishing failed: {str(e)}'}
        
        finally:
            self.close_driver()
    
    def _publish_facebook_post(self, post: Dict) -> Dict:
        """Publish post ke Facebook"""
        # Implementation akan ditambahkan di phase selanjutnya
        return {'success': False, 'message': 'Facebook posting implementation pending'}
    
    def _publish_twitter_post(self, post: Dict) -> Dict:
        """Publish post ke Twitter"""
        # Implementation akan ditambahkan di phase selanjutnya
        return {'success': False, 'message': 'Twitter posting implementation pending'}
    
    def _publish_linkedin_post(self, post: Dict) -> Dict:
        """Publish post ke LinkedIn"""
        # Implementation akan ditambahkan di phase selanjutnya
        return {'success': False, 'message': 'LinkedIn posting implementation pending'}
    
    def _publish_instagram_post(self, post: Dict) -> Dict:
        """Publish post ke Instagram"""
        # Implementation akan ditambahkan di phase selanjutnya
        return {'success': False, 'message': 'Instagram posting implementation pending'}
    
    def _publish_guest_post(self, post: Dict) -> Dict:
        """Publish post ke guest posting site"""
        # Implementation akan ditambahkan di phase selanjutnya
        return {'success': False, 'message': 'Guest posting implementation pending'}
    
    def scrape_content(self, url: str) -> Dict:
        """Scrape content dari URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = ''
            title_tags = soup.find_all(['h1', 'title'])
            if title_tags:
                title = title_tags[0].get_text().strip()
            
            # Extract content
            content = ''
            content_selectors = [
                'article', '.post-content', '.entry-content', 
                '.content', 'main', '.post', '.article-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove script and style elements
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    content = content_elem.get_text().strip()
                    break
            
            if not content:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])
            
            return {
                'success': True,
                'title': title,
                'content': content[:2000],  # Limit content length
                'url': url
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Content scraping failed: {str(e)}'
            }

