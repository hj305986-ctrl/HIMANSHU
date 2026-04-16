class ProfileScorer:
    
    def calculate_score(self, profile_data, analysis_results):
        
        score = 100
        reasons = []
        
        # CHECK 1: Profile Picture
        if not profile_data.get('profile_pic'):
            score -= 25
            reasons.append("❌ Profile picture nahi hai (-25 points)")
        else:
            reasons.append("✅ Profile picture hai")
        
        # CHECK 2: Bio
        bio_result = analysis_results.get('bio_analysis', {})
        
        if not profile_data.get('bio'):
            score -= 15
            reasons.append("❌ Bio nahi hai (-15 points)")
        elif bio_result.get('is_suspicious'):
            score -= 30
            reason_text = bio_result.get('reason', '')
            reasons.append(f"❌ Bio suspicious: {reason_text} (-30 points)")
        else:
            reasons.append("✅ Bio normal hai")
        
        # CHECK 3: Connections
        connections = profile_data.get('connections', 0)
        
        if connections == 0:
            score -= 20
            reasons.append("❌ Connections nahi hain (-20 points)")
        elif connections < 50:
            score -= 15
            reasons.append(f"❌ Sirf {connections} connections (-15 points)")
        elif connections > 200:
            score += 10
            reasons.append(f"✅ {connections} connections (Bonus +10)")
        else:
            reasons.append(f"✅ {connections} connections")
        
        # CHECK 4: Posts
        posts = profile_data.get('posts_count', 0)
        
        if posts == 0:
            score -= 10
            reasons.append("❌ Koi post nahi (-10 points)")
        else:
            reasons.append(f"✅ {posts} posts hain")
        
        # CHECK 5: Naam
        name_flags = analysis_results.get('name_flags', [])
        
        if name_flags:
            score -= 20
            reasons.append(f"❌ Naam suspicious: {name_flags} (-20 points)")
        else:
            reasons.append("✅ Naam normal lagta hai")
        
        score = max(0, min(100, score))
        
        if score >= 70:
            verdict = "✅ REAL PROFILE LAGTI HAI"
            risk = "LOW RISK"
            emoji = "🟢"
        elif score >= 40:
            verdict = "⚠️ SUSPICIOUS PROFILE HAI"
            risk = "MEDIUM RISK"
            emoji = "🟡"
        else:
            verdict = "❌ FAKE PROFILE HAI"
            risk = "HIGH RISK"
            emoji = "🔴"
        
        return {
            'score': score,
            'verdict': verdict,
            'risk_level': risk,
            'emoji': emoji,
            'reasons': reasons
        }