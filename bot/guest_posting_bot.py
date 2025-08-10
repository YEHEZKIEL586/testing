"""
Guest Posting Bot yang flexible untuk berbagai CMS
Mendukung WordPress, Blogger, Medium, dan custom sites
"""

import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

class GuestPostingBot:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
        # Common selectors untuk berbagai CMS
        self.cms_selectors = {
            'wordpress': {
                'login': {
                    'username': [
                        "//input[@id='user_login' or @name='log']",
                        "//input[@type='text' and contains(@class, 'user')]",
                        "//input[contains(@placeholder, 'Username') or contains(@placeholder, 'Email')]"
                    ],
                    'password': [
                        "//input[@id='user_pass' or @name='pwd']",
                        "//input[@type='password']"
                    ],
                    'submit': [
                        "//input[@id='wp-submit' or @type='submit']",
                        "//button[@type='submit']",
                        "//input[@value='Log In' or @value='Login']"
                    ]
                },
                'post_creation': {
                    'new_post': [
                        "//a[contains(@href, 'post-new.php') or contains(text(), 'Add New')]",
                        "//a[@class='page-title-action']",
                        "//button[contains(text(), 'Add New Post')]"
                    ],
                    'title': [
                        "//input[@id='title' or @name='post_title']",
                        "//h1[@contenteditable='true']",
                        "//input[contains(@placeholder, 'Add title')]"
                    ],
                    'content': [
                        "//textarea[@id='content']",
                        "//div[@id='wp-content-editor-container']//iframe",
                        "//div[contains(@class, 'editor-writing-flow')]",
                        "//div[@contenteditable='true' and contains(@class, 'editor')]"
                    ],
                    'publish': [
                        "//input[@id='publish' or @value='Publish']",
                        "//button[contains(text(), 'Publish')]",
                        "//button[@class='editor-post-publish-button']"
                    ],
                    'category': [
                        "//div[@id='categorydiv']//input[@type='checkbox']",
                        "//select[@name='post_category[]']"
                    ],
                    'tags': [
                        "//input[@id='new-tag-post_tag']",
                        "//textarea[@name='tax_input[post_tag]']"
                    ]
                }
            },
            'blogger': {
                'login': {
                    'email': [
                        "//input[@type='email' or @id='identifierId']"
                    ],
                    'password': [
                        "//input[@type='password' or @name='password']"
                    ],
                    'next': [
                        "//div[@id='identifierNext']//button",
                        "//button[contains(text(), 'Next')]"
                    ],
                    'submit': [
                        "//div[@id='passwordNext']//button",
                        "//button[@type='submit']"
                    ]
                },
                'post_creation': {
                    'new_post': [
                        "//span[contains(text(), 'New post')]",
                        "//a[@aria-label='New post']"
                    ],
                    'title': [
                        "//input[@aria-label='Title']",
                        "//input[contains(@class, 'title')]"
                    ],
                    'content': [
                        "//div[@role='textbox']",
                        "//div[contains(@class, 'editor')]//div[@contenteditable='true']"
                    ],
                    'publish': [
                        "//span[contains(text(), 'Publish')]",
                        "//button[@aria-label='Publish']"
                    ]
                }
            },
            'medium': {
                'login': {
                    'signin': [
                        "//a[contains(text(), 'Sign in')]",
                        "//button[contains(text(), 'Sign in')]"
                    ],
                    'email': [
                        "//input[@type='email' or @name='email']"
                    ],
                    'continue': [
                        "//button[contains(text(), 'Continue')]"
                    ],
                    'password': [
                        "//input[@type='password']"
                    ]
                },
                'post_creation': {
                    'write': [
                        "//a[contains(@href, '/new-story') or contains(text(), 'Write')]"
                    ],
                    'title': [
                        "//h3[@data-default-value='Title']",
                        "//div[contains(@class, 'title')]//p"
                    ],
                    'content': [
                        "//div[contains(@class, 'section-content')]//p",
                        "//div[@role='textbox']"
                    ],
                    'publish': [
                        "//button[contains(text(), 'Publish')]"
                    ]
                }
            },
            'generic': {
                'login': {
                    'username': [
                        "//input[@name='username' or @name='user' or @name='email']",
                        "//input[@type='email']",
                        "//input[@id='username' or @id='user' or @id='email']",
                        "//input[contains(@placeholder, 'username') or contains(@placeholder, 'email')]"
                    ],
                    'password': [
                        "//input[@name='password' or @name='pass']",
                        "//input[@type='password']",
                        "//input[@id='password' or @id='pass']"
                    ],
                    'submit': [
                        "//button[@type='submit']",
                        "//input[@type='submit']",
                        "//button[contains(text(), 'Login') or contains(text(), 'Sign in')]",
                        "//input[contains(@value, 'Login') or contains(@value, 'Sign in')]"
                    ]
                },
                'post_creation': {
                    'new_post': [
                        "//a[contains(text(), 'New Post') or contains(text(), 'Add Post')]",
                        "//button[contains(text(), 'Create') or contains(text(), 'New')]",
                        "//a[contains(@href, 'new') or contains(@href, 'create')]"
                    ],
                    'title': [
                        "//input[@name='title' or contains(@placeholder, 'title')]",
                        "//input[@id='title']",
                        "//h1[@contenteditable='true']"
                    ],
                    'content': [
                        "//textarea[@name='content' or @name='body']",
                        "//div[@contenteditable='true']",
                        "//iframe[contains(@id, 'editor')]"
                    ],
                    'publish': [
                        "//button[contains(text(), 'Publish') or contains(text(), 'Submit')]",
                        "//input[@type='submit' and contains(@value, 'Publish')]"
                    ]
                }
            }
        }
    
    def detect_cms(self, url: str) -> str:
        """Detect CMS type dari URL atau page source"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # WordPress detection
            if ('wp-content' in page_source or 'wp-admin' in current_url or 
                'wordpress' in page_source or 'wp-login' in current_url):
                return 'wordpress'
            
            # Blogger detection
            elif ('blogger.com' in current_url or 'blogspot.com' in current_url or
                  'blogger' in page_source):
                return 'blogger'
            
            # Medium detection
            elif 'medium.com' in current_url or 'medium' in page_source:
                return 'medium'
            
            # Default to generic
            else:
                return 'generic'
        
        except Exception as e:
            print(f"CMS detection error: {e}")
            return 'generic'
    
    def login_to_site(self, site_info: Dict) -> Dict:
        """Login ke guest posting site"""
        try:
            login_url = site_info['login_url']
            username = site_info['username']
            password = site_info['password']
            
            # Detect CMS type
            cms_type = self.detect_cms(login_url)
            print(f"Detected CMS: {cms_type}")
            
            # Navigate to login page
            self.driver.get(login_url)
            time.sleep(random.uniform(3, 5))
            
            # Handle different CMS login flows
            if cms_type == 'wordpress':
                return self._login_wordpress(username, password)
            elif cms_type == 'blogger':
                return self._login_blogger(username, password)
            elif cms_type == 'medium':
                return self._login_medium(username, password)
            else:
                return self._login_generic(username, password)
        
        except Exception as e:
            return {'success': False, 'message': f'Login error: {str(e)}'}
    
    def _login_wordpress(self, username: str, password: str) -> Dict:
        """Login ke WordPress site"""
        try:
            selectors = self.cms_selectors['wordpress']['login']
            
            # Find username field
            username_field = self._find_element_flexible(selectors['username'])
            self._human_type(username_field, username)
            time.sleep(random.uniform(1, 2))
            
            # Find password field
            password_field = self._find_element_flexible(selectors['password'])
            self._human_type(password_field, password)
            time.sleep(random.uniform(1, 2))
            
            # Find and click submit button
            submit_button = self._find_element_flexible(selectors['submit'])
            submit_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Check if login successful
            current_url = self.driver.current_url
            if 'wp-admin' in current_url or 'dashboard' in current_url:
                return {'success': True, 'message': 'WordPress login successful'}
            else:
                return {'success': False, 'message': 'WordPress login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'WordPress login error: {str(e)}'}
    
    def _login_blogger(self, username: str, password: str) -> Dict:
        """Login ke Blogger"""
        try:
            selectors = self.cms_selectors['blogger']['login']
            
            # Enter email
            email_field = self._find_element_flexible(selectors['email'])
            self._human_type(email_field, username)
            time.sleep(1)
            
            # Click Next
            next_button = self._find_element_flexible(selectors['next'])
            next_button.click()
            time.sleep(3)
            
            # Enter password
            password_field = self._find_element_flexible(selectors['password'])
            self._human_type(password_field, password)
            time.sleep(1)
            
            # Click Next/Submit
            submit_button = self._find_element_flexible(selectors['submit'])
            submit_button.click()
            time.sleep(5)
            
            return {'success': True, 'message': 'Blogger login successful'}
        
        except Exception as e:
            return {'success': False, 'message': f'Blogger login error: {str(e)}'}
    
    def _login_medium(self, username: str, password: str) -> Dict:
        """Login ke Medium"""
        try:
            selectors = self.cms_selectors['medium']['login']
            
            # Click Sign in
            signin_button = self._find_element_flexible(selectors['signin'])
            signin_button.click()
            time.sleep(2)
            
            # Enter email
            email_field = self._find_element_flexible(selectors['email'])
            self._human_type(email_field, username)
            time.sleep(1)
            
            # Click Continue
            continue_button = self._find_element_flexible(selectors['continue'])
            continue_button.click()
            time.sleep(2)
            
            # Enter password
            password_field = self._find_element_flexible(selectors['password'])
            self._human_type(password_field, password)
            password_field.send_keys(Keys.RETURN)
            time.sleep(5)
            
            return {'success': True, 'message': 'Medium login successful'}
        
        except Exception as e:
            return {'success': False, 'message': f'Medium login error: {str(e)}'}
    
    def _login_generic(self, username: str, password: str) -> Dict:
        """Generic login untuk custom sites"""
        try:
            selectors = self.cms_selectors['generic']['login']
            
            # Find username field
            username_field = self._find_element_flexible(selectors['username'])
            self._human_type(username_field, username)
            time.sleep(random.uniform(1, 2))
            
            # Find password field
            password_field = self._find_element_flexible(selectors['password'])
            self._human_type(password_field, password)
            time.sleep(random.uniform(1, 2))
            
            # Find and click submit button
            submit_button = self._find_element_flexible(selectors['submit'])
            submit_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Basic success check
            current_url = self.driver.current_url
            if 'login' not in current_url.lower():
                return {'success': True, 'message': 'Generic login successful'}
            else:
                return {'success': False, 'message': 'Generic login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'Generic login error: {str(e)}'}
    
    def create_guest_post(self, site_info: Dict, post_data: Dict) -> Dict:
        """Create guest post di site"""
        try:
            # Login first
            login_result = self.login_to_site(site_info)
            if not login_result['success']:
                return login_result
            
            # Detect CMS and create post
            cms_type = self.detect_cms(site_info['url'])
            
            if cms_type == 'wordpress':
                return self._create_wordpress_post(post_data)
            elif cms_type == 'blogger':
                return self._create_blogger_post(post_data)
            elif cms_type == 'medium':
                return self._create_medium_post(post_data)
            else:
                return self._create_generic_post(post_data, site_info)
        
        except Exception as e:
            return {'success': False, 'message': f'Post creation error: {str(e)}'}
    
    def _create_wordpress_post(self, post_data: Dict) -> Dict:
        """Create post di WordPress"""
        try:
            selectors = self.cms_selectors['wordpress']['post_creation']
            
            # Navigate to new post page
            try:
                new_post_button = self._find_element_flexible(selectors['new_post'])
                new_post_button.click()
            except:
                # Try direct URL
                current_url = self.driver.current_url
                base_url = current_url.split('/wp-admin')[0]
                self.driver.get(f"{base_url}/wp-admin/post-new.php")
            
            time.sleep(random.uniform(3, 5))
            
            # Add title
            title_field = self._find_element_flexible(selectors['title'])
            self._human_type(title_field, post_data['title'])
            time.sleep(1)
            
            # Add content
            content_field = self._find_element_flexible(selectors['content'])
            
            # Handle different editor types
            if content_field.tag_name == 'iframe':
                # Classic editor
                self.driver.switch_to.frame(content_field)
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.clear()
                body.send_keys(post_data['content'])
                self.driver.switch_to.default_content()
            else:
                # Block editor or other
                self._human_type(content_field, post_data['content'])
            
            time.sleep(2)
            
            # Add categories if provided
            if post_data.get('categories'):
                try:
                    for category in post_data['categories']:
                        category_checkbox = self.driver.find_element(
                            By.XPATH, f"//label[contains(text(), '{category}')]//input[@type='checkbox']"
                        )
                        if not category_checkbox.is_selected():
                            category_checkbox.click()
                except:
                    pass
            
            # Add tags if provided
            if post_data.get('tags'):
                try:
                    tags_field = self._find_element_flexible(selectors['tags'])
                    tags_text = ', '.join(post_data['tags'])
                    self._human_type(tags_field, tags_text)
                    tags_field.send_keys(Keys.RETURN)
                except:
                    pass
            
            time.sleep(2)
            
            # Publish post
            publish_button = self._find_element_flexible(selectors['publish'])
            publish_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Check if published successfully
            try:
                success_message = self.driver.find_element(
                    By.XPATH, "//div[contains(text(), 'Post published') or contains(text(), 'published successfully')]"
                )
                return {'success': True, 'message': 'WordPress post published successfully'}
            except:
                return {'success': True, 'message': 'WordPress post created (verification timeout)'}
        
        except Exception as e:
            return {'success': False, 'message': f'WordPress post creation error: {str(e)}'}
    
    def _create_blogger_post(self, post_data: Dict) -> Dict:
        """Create post di Blogger"""
        try:
            selectors = self.cms_selectors['blogger']['post_creation']
            
            # Click New Post
            new_post_button = self._find_element_flexible(selectors['new_post'])
            new_post_button.click()
            time.sleep(3)
            
            # Add title
            title_field = self._find_element_flexible(selectors['title'])
            self._human_type(title_field, post_data['title'])
            time.sleep(1)
            
            # Add content
            content_field = self._find_element_flexible(selectors['content'])
            self._human_type(content_field, post_data['content'])
            time.sleep(2)
            
            # Publish
            publish_button = self._find_element_flexible(selectors['publish'])
            publish_button.click()
            time.sleep(5)
            
            return {'success': True, 'message': 'Blogger post published successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Blogger post creation error: {str(e)}'}
    
    def _create_medium_post(self, post_data: Dict) -> Dict:
        """Create post di Medium"""
        try:
            selectors = self.cms_selectors['medium']['post_creation']
            
            # Click Write
            write_button = self._find_element_flexible(selectors['write'])
            write_button.click()
            time.sleep(3)
            
            # Add title
            title_field = self._find_element_flexible(selectors['title'])
            title_field.click()
            title_field.clear()
            self._human_type(title_field, post_data['title'])
            time.sleep(1)
            
            # Add content
            content_field = self._find_element_flexible(selectors['content'])
            content_field.click()
            self._human_type(content_field, post_data['content'])
            time.sleep(2)
            
            # Publish
            publish_button = self._find_element_flexible(selectors['publish'])
            publish_button.click()
            time.sleep(3)
            
            # Confirm publish
            try:
                confirm_publish = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Publish now')]"))
                )
                confirm_publish.click()
                time.sleep(3)
            except:
                pass
            
            return {'success': True, 'message': 'Medium post published successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Medium post creation error: {str(e)}'}
    
    def _create_generic_post(self, post_data: Dict, site_info: Dict) -> Dict:
        """Create post di generic/custom site"""
        try:
            selectors = self.cms_selectors['generic']['post_creation']
            
            # Try to find new post button
            try:
                new_post_button = self._find_element_flexible(selectors['new_post'])
                new_post_button.click()
                time.sleep(3)
            except:
                # Try using post_url if provided
                if site_info.get('post_url'):
                    self.driver.get(site_info['post_url'])
                    time.sleep(3)
                else:
                    return {'success': False, 'message': 'Could not find new post button'}
            
            # Add title
            title_field = self._find_element_flexible(selectors['title'])
            self._human_type(title_field, post_data['title'])
            time.sleep(1)
            
            # Add content
            content_field = self._find_element_flexible(selectors['content'])
            
            # Handle iframe editor
            if content_field.tag_name == 'iframe':
                self.driver.switch_to.frame(content_field)
                body = self.driver.find_element(By.TAG_NAME, 'body')
                body.clear()
                body.send_keys(post_data['content'])
                self.driver.switch_to.default_content()
            else:
                self._human_type(content_field, post_data['content'])
            
            time.sleep(2)
            
            # Publish
            publish_button = self._find_element_flexible(selectors['publish'])
            publish_button.click()
            time.sleep(5)
            
            return {'success': True, 'message': 'Generic post published successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Generic post creation error: {str(e)}'}
    
    def _find_element_flexible(self, xpath_list: List[str], timeout: int = 10):
        """Find element dengan multiple XPath fallbacks"""
        for xpath in xpath_list:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                return element
            except TimeoutException:
                continue
        
        raise TimeoutException(f"Could not find element with any of the XPaths: {xpath_list}")
    
    def _human_type(self, element, text: str, delay_range: Tuple[float, float] = (0.05, 0.15)):
        """Type text seperti manusia"""
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def get_site_info(self, url: str) -> Dict:
        """Get information about the site"""
        try:
            self.driver.get(url)
            time.sleep(3)
            
            # Get basic site info
            title = self.driver.title
            cms_type = self.detect_cms(url)
            
            # Try to detect login URL
            login_urls = []
            login_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'login') or contains(text(), 'Login') or contains(text(), 'Sign in')]")
            for link in login_links:
                href = link.get_attribute('href')
                if href:
                    login_urls.append(href)
            
            return {
                'success': True,
                'title': title,
                'cms_type': cms_type,
                'login_urls': login_urls,
                'current_url': self.driver.current_url
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Site info error: {str(e)}'}
    
    def test_post_creation_access(self, site_info: Dict) -> Dict:
        """Test if we can access post creation after login"""
        try:
            # Login first
            login_result = self.login_to_site(site_info)
            if not login_result['success']:
                return login_result
            
            # Try to access post creation
            cms_type = self.detect_cms(site_info['url'])
            selectors = self.cms_selectors.get(cms_type, self.cms_selectors['generic'])
            
            try:
                new_post_button = self._find_element_flexible(selectors['post_creation']['new_post'], timeout=5)
                return {'success': True, 'message': 'Post creation access confirmed'}
            except:
                return {'success': False, 'message': 'Cannot access post creation'}
        
        except Exception as e:
            return {'success': False, 'message': f'Post creation access test error: {str(e)}'}

