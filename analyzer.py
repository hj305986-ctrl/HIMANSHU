import re

class ProfileAnalyzer:
    
    def __init__(self):
        self.spam_words = [
            'crypto', 'bitcoin', 'investment',
            'dm me', 'click link', 'earn money',
            'guaranteed profit', 'forex', 
            'make money', 'free money',
            'work from home', 'passive income',
            'whatsapp me', 'telegram me'
        ]
    
    def analyze_bio(self, bio_text):
        if not bio_text or len(bio_text) < 5:
            return {
                'is_suspicious': True,
                'reason': 'Bio bilkul khali hai',
                'confidence': 80
            }
        
        bio_lower = bio_text.lower()
        found_words = []
        
        for word in self.spam_words:
            if word in bio_lower:
                found_words.append(word)
        
        if found_words:
            return {
                'is_suspicious': True,
                'reason': f'Spam words mile: {found_words}',
                'confidence': 85
            }
        
        if len(bio_text) < 20:
            return {
                'is_suspicious': True,
                'reason': 'Bio bahut chhoti hai',
                'confidence': 60
            }
        
        return {
            'is_suspicious': False,
            'reason': 'Bio theek lagti hai',
            'confidence': 70
        }
    
    def check_name(self, name):
        problems = []
        
        if not name or name == "Unknown":
            problems.append("Naam nahi mila")
            return problems
        
        if any(char.isdigit() for char in name):
            problems.append("Naam mein numbers hain")
        
        if len(name) < 4:
            problems.append("Naam bahut chhota hai")
        
        if re.search(r'[^a-zA-Z\s\.\-]', name):
            problems.append("Naam mein special characters hain")
        
        return problems
    
    def check_account_age(self, join_date_str):
        if not join_date_str or join_date_str == "Unknown":
            return {
                'suspicious': True,
                'reason': 'Account ki date nahi mili',
                'age_days': 0
            }
        return {
            'suspicious': False,
            'reason': 'Account age theek hai',
            'age_days': 365
        }
    
    def check_links_in_bio(self, bio_text):
        if not bio_text:
            return []
        
        urls = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+])+', 
            bio_text
        )
        
        suspicious_links = []
        bad_domains = ['bit.ly', 'tinyurl', 't.me', 'wa.me']
        
        for url in urls:
            for domain in bad_domains:
                if domain in url:
                    suspicious_links.append(url)
        
        return suspicious_links