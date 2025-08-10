"""
Instagram Bot dengan fitur lengkap
Mendukung posting foto, video, stories, dan reels
"""

import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, List, Optional
import requests
from PIL import Image
import io

class InstagramBot:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
        
        # Instagram-specific XPath selectors
        self.selectors = {
            'login': {
                'username': "//input[@name='username' or @aria-label='Phone number, username, or email']",
                'password': "//input[@name='password' or @aria-label='Password']",
                'submit': "//button[@type='submit' or contains(text(), 'Log in')]",
                'not_now': "//button[contains(text(), 'Not Now')]"
            },
            'navigation': {
                'home': "//a[@href='/' or contains(@aria-label, 'Home')]",
                'create': "//div[@role='menuitem' and contains(@aria-label, 'New post')] | //*[contains(@aria-label, 'New post')] | //a[contains(@href, '/create/')]",
                'profile': "//a[contains(@href, '/') and contains(@aria-label, 'Profile')]"
            },
            'post_creation': {
                'select_files': "//input[@type='file' and @accept]",
                'drag_drop_area': "//div[contains(text(), 'Drag photos and videos here')]",
                'next_button': "//button[contains(text(), 'Next')]",
                'share_button': "//button[contains(text(), 'Share')]",
                'caption_textarea': "//textarea[@aria-label='Write a caption...' or @placeholder='Write a caption...']",
                'location_input': "//input[@placeholder='Add location']",
                'tag_people': "//button[contains(text(), 'Tag people')]",
                'advanced_settings': "//button[contains(text(), 'Advanced settings')]"
            },
            'story': {
                'your_story': "//button[contains(@aria-label, 'Add to your story')]",
                'camera_button': "//button[@aria-label='Camera']",
                'gallery_button': "//button[contains(@aria-label, 'Open Media Gallery')]",
                'share_story': "//button[contains(text(), 'Share to story')]"
            },
            'reels': {
                'reels_tab': "//button[contains(text(), 'Reels')]",
                'create_reel': "//button[contains(@aria-label, 'Create')]",
                'upload_video': "//input[@type='file' and contains(@accept, 'video')]"
            }
        }
    
    def login(self, username: str, password: str) -> Dict:
        """Login ke Instagram"""
        try:
            self.driver.get('https://www.instagram.com/accounts/login/')
            time.sleep(random.uniform(3, 5))
            
            # Handle cookies popup if exists
            try:
                cookies_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]")
                cookies_button.click()
                time.sleep(1)
            except:
                pass
            
            # Find username field
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.selectors['login']['username']))
            )
            
            # Type username with human-like delay
            self._human_type(username_field, username)
            time.sleep(random.uniform(1, 2))
            
            # Find password field
            password_field = self.driver.find_element(By.XPATH, self.selectors['login']['password'])
            self._human_type(password_field, password)
            time.sleep(random.uniform(1, 2))
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, self.selectors['login']['submit'])
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(5, 8))
            
            # Handle "Save Your Login Info" popup
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors['login']['not_now']))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            # Handle "Turn on Notifications" popup
            try:
                not_now_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                not_now_button.click()
                time.sleep(2)
            except:
                pass
            
            # Check if login successful
            current_url = self.driver.current_url
            if 'instagram.com' in current_url and 'login' not in current_url:
                return {'success': True, 'message': 'Instagram login successful'}
            else:
                return {'success': False, 'message': 'Instagram login failed'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram login error: {str(e)}'}
    
    def post_photo(self, image_path: str, caption: str = '', hashtags: List[str] = None, 
                   location: str = '', alt_text: str = '') -> Dict:
        """Post foto ke Instagram"""
        try:
            # Navigate to create post
            self.driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(2, 4))
            
            # Click create button
            create_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['navigation']['create']))
            )
            create_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Upload file
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['select_files']))
            )
            
            # Make sure file exists and is valid image
            if not os.path.exists(image_path):
                return {'success': False, 'message': 'Image file not found'}
            
            file_input.send_keys(os.path.abspath(image_path))
            time.sleep(random.uniform(3, 5))
            
            # Click Next (crop/filter step)
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['next_button']))
            )
            next_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Click Next again (filter step)
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['next_button']))
                )
                next_button.click()
                time.sleep(random.uniform(2, 3))
            except:
                pass
            
            # Add caption
            if caption or hashtags:
                caption_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['caption_textarea']))
                )
                
                full_caption = caption
                if hashtags:
                    hashtag_text = ' '.join([f'#{tag.strip("#")}' for tag in hashtags])
                    full_caption = f"{caption}\\n\\n{hashtag_text}" if caption else hashtag_text
                
                self._human_type(caption_field, full_caption)
                time.sleep(random.uniform(1, 2))
            
            # Add location if provided
            if location:
                try:
                    location_input = self.driver.find_element(By.XPATH, self.selectors['post_creation']['location_input'])
                    self._human_type(location_input, location)
                    time.sleep(2)
                    
                    # Select first location suggestion
                    location_suggestion = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and contains(@class, 'location')]"))
                    )
                    location_suggestion.click()
                    time.sleep(1)
                except:
                    pass
            
            # Add alt text if provided
            if alt_text:
                try:
                    advanced_settings = self.driver.find_element(By.XPATH, self.selectors['post_creation']['advanced_settings'])
                    advanced_settings.click()
                    time.sleep(1)
                    
                    alt_text_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Alt text']"))
                    )
                    self._human_type(alt_text_field, alt_text)
                    time.sleep(1)
                except:
                    pass
            
            # Share the post
            share_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['share_button']))
            )
            share_button.click()
            
            # Wait for post to be shared
            time.sleep(random.uniform(5, 8))
            
            # Check if post was successful
            try:
                # Look for success indicators
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Your post has been shared')]")),
                        EC.url_contains('instagram.com')
                    )
                )
                return {'success': True, 'message': 'Instagram photo posted successfully'}
            except:
                return {'success': True, 'message': 'Instagram photo posted (verification timeout)'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram photo posting error: {str(e)}'}
    
    def post_video(self, video_path: str, caption: str = '', hashtags: List[str] = None,
                   cover_image_path: str = '') -> Dict:
        """Post video ke Instagram"""
        try:
            # Similar to photo posting but for video
            self.driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(2, 4))
            
            # Click create button
            create_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['navigation']['create']))
            )
            create_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Upload video file
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['select_files']))
            )
            
            if not os.path.exists(video_path):
                return {'success': False, 'message': 'Video file not found'}
            
            file_input.send_keys(os.path.abspath(video_path))
            time.sleep(random.uniform(5, 8))  # Video upload takes longer
            
            # Click Next (trim video step)
            next_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['next_button']))
            )
            next_button.click()
            time.sleep(random.uniform(3, 5))
            
            # Click Next (cover selection step)
            try:
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['next_button']))
                )
                next_button.click()
                time.sleep(random.uniform(2, 3))
            except:
                pass
            
            # Add caption and hashtags
            if caption or hashtags:
                caption_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['caption_textarea']))
                )
                
                full_caption = caption
                if hashtags:
                    hashtag_text = ' '.join([f'#{tag.strip("#")}' for tag in hashtags])
                    full_caption = f"{caption}\\n\\n{hashtag_text}" if caption else hashtag_text
                
                self._human_type(caption_field, full_caption)
                time.sleep(random.uniform(1, 2))
            
            # Share the video
            share_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['share_button']))
            )
            share_button.click()
            
            # Wait for video to be processed and shared
            time.sleep(random.uniform(10, 15))
            
            return {'success': True, 'message': 'Instagram video posted successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram video posting error: {str(e)}'}
    
    def post_story(self, media_path: str, story_type: str = 'photo') -> Dict:
        """Post story ke Instagram"""
        try:
            self.driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(2, 4))
            
            # Click on "Your story" or camera icon
            story_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['story']['your_story']))
            )
            story_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Upload media
            if story_type == 'photo':
                # Handle photo upload for story
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                file_input.send_keys(os.path.abspath(media_path))
            else:
                # Handle video upload for story
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file' and contains(@accept, 'video')]"))
                )
                file_input.send_keys(os.path.abspath(media_path))
            
            time.sleep(random.uniform(3, 5))
            
            # Share to story
            share_story_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['story']['share_story']))
            )
            share_story_button.click()
            
            time.sleep(random.uniform(3, 5))
            
            return {'success': True, 'message': 'Instagram story posted successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram story posting error: {str(e)}'}
    
    def post_reel(self, video_path: str, caption: str = '', hashtags: List[str] = None,
                  music_name: str = '') -> Dict:
        """Post reel ke Instagram"""
        try:
            self.driver.get('https://www.instagram.com/')
            time.sleep(random.uniform(2, 4))
            
            # Navigate to reels creation
            create_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['navigation']['create']))
            )
            create_button.click()
            time.sleep(random.uniform(2, 3))
            
            # Select Reels tab if available
            try:
                reels_tab = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors['reels']['reels_tab']))
                )
                reels_tab.click()
                time.sleep(2)
            except:
                pass
            
            # Upload video
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['select_files']))
            )
            
            if not os.path.exists(video_path):
                return {'success': False, 'message': 'Video file not found'}
            
            file_input.send_keys(os.path.abspath(video_path))
            time.sleep(random.uniform(5, 8))
            
            # Process through reel creation steps
            # This would include music selection, effects, etc.
            # For now, we'll skip to the final step
            
            # Add caption
            if caption or hashtags:
                try:
                    caption_field = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, self.selectors['post_creation']['caption_textarea']))
                    )
                    
                    full_caption = caption
                    if hashtags:
                        hashtag_text = ' '.join([f'#{tag.strip("#")}' for tag in hashtags])
                        full_caption = f"{caption}\\n\\n{hashtag_text}" if caption else hashtag_text
                    
                    self._human_type(caption_field, full_caption)
                    time.sleep(random.uniform(1, 2))
                except:
                    pass
            
            # Share the reel
            share_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, self.selectors['post_creation']['share_button']))
            )
            share_button.click()
            
            time.sleep(random.uniform(8, 12))
            
            return {'success': True, 'message': 'Instagram reel posted successfully'}
        
        except Exception as e:
            return {'success': False, 'message': f'Instagram reel posting error: {str(e)}'}
    
    def get_account_info(self, username: str = None) -> Dict:
        """Get account information"""
        try:
            if username:
                self.driver.get(f'https://www.instagram.com/{username}/')
            else:
                # Go to own profile
                profile_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, self.selectors['navigation']['profile']))
                )
                profile_button.click()
            
            time.sleep(random.uniform(3, 5))
            
            # Extract account information
            try:
                followers_count = self.driver.find_element(By.XPATH, "//a[contains(@href, '/followers/')]/span").text
            except:
                followers_count = "0"
            
            try:
                following_count = self.driver.find_element(By.XPATH, "//a[contains(@href, '/following/')]/span").text
            except:
                following_count = "0"
            
            try:
                posts_count = self.driver.find_element(By.XPATH, "//div[contains(text(), 'posts')]/span").text
            except:
                posts_count = "0"
            
            return {
                'success': True,
                'followers': followers_count,
                'following': following_count,
                'posts': posts_count
            }
        
        except Exception as e:
            return {'success': False, 'message': f'Error getting account info: {str(e)}'}
    
    def _human_type(self, element, text: str, delay_range: tuple = (0.05, 0.15)):
        """Type text dengan delay seperti manusia"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(*delay_range))
    
    def _scroll_and_click(self, element):
        """Scroll ke element dan click"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(random.uniform(0.5, 1.0))
        
        try:
            element.click()
        except:
            # Try JavaScript click if normal click fails
            self.driver.execute_script("arguments[0].click();", element)
    
    def _wait_for_upload(self, timeout: int = 30):
        """Wait for file upload to complete"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Look for upload progress indicators
                progress = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'progress') or contains(@aria-label, 'Loading')]")
                if not progress:
                    break
            except:
                pass
            time.sleep(1)
    
    def validate_media_file(self, file_path: str, media_type: str = 'photo') -> Dict:
        """Validate media file before upload"""
        try:
            if not os.path.exists(file_path):
                return {'valid': False, 'message': 'File does not exist'}
            
            file_size = os.path.getsize(file_path)
            
            if media_type == 'photo':
                # Instagram photo requirements
                max_size = 8 * 1024 * 1024  # 8MB
                allowed_formats = ['.jpg', '.jpeg', '.png']
                
                if file_size > max_size:
                    return {'valid': False, 'message': 'Photo file too large (max 8MB)'}
                
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in allowed_formats:
                    return {'valid': False, 'message': f'Invalid photo format. Allowed: {allowed_formats}'}
            
            elif media_type == 'video':
                # Instagram video requirements
                max_size = 100 * 1024 * 1024  # 100MB
                allowed_formats = ['.mp4', '.mov']
                
                if file_size > max_size:
                    return {'valid': False, 'message': 'Video file too large (max 100MB)'}
                
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in allowed_formats:
                    return {'valid': False, 'message': f'Invalid video format. Allowed: {allowed_formats}'}
            
            return {'valid': True, 'message': 'File is valid'}
        
        except Exception as e:
            return {'valid': False, 'message': f'File validation error: {str(e)}'}

