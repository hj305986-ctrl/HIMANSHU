import requests
from bs4 import BeautifulSoup

class ProfileScraper:
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
    
    def scrape_profile(self, url):
        try:
            print(f"   URL se data le raha hoon...")
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profile_data = {
                'url': url,
                'name': self.get_name(soup),
                'bio': self.get_bio(soup),
                'profile_pic': self.has_profile_pic(soup),
                'followers': self.get_followers(soup),
                'posts_count': self.get_posts_count(soup),
                'join_date': self.get_join_date(soup),
                'connections': self.get_connections(soup)
            }
            return profile_data
            
        except Exception as e:
            print(f"   Error aaya: {e}")
            return None
    
    def get_name(self, soup):
        try:
            name = soup.find('h1')
            return name.text.strip() if name else "Unknown"
        except:
            return "Unknown"
    
    def get_bio(self, soup):
        try:
            bio = soup.find('meta', {'name': 'description'})
            if bio:
                return bio.get('content', '')
            return ""
        except:
            return ""
    
    def has_profile_pic(self, soup):
        try:
            pic = soup.find('img')
            return True if pic else False
        except:
            return False
    
    def get_followers(self, soup):
        return 0
    
    def get_posts_count(self, soup):
        try:
            posts = soup.find_all('article')
            return len(posts)
        except:
            return 0
    
    def get_join_date(self, soup):
        return "Unknown"
    
    def get_connections(self, soup):
        return 0