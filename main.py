from flask import Flask, render_template_string, request, jsonify
from analyzer import ProfileAnalyzer
from scorer import ProfileScorer
import os
import csv
from datetime import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fake Profile Detector</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh;
            color: white;
            padding: 20px;
        }
        
        .container { max-width: 700px; margin: 0 auto; }
        
        h1 {
            text-align: center;
            font-size: 2.5em;
            color: #00d4ff;
            padding: 30px 0 10px 0;
        }
        
        p.subtitle {
            text-align: center;
            color: #aaa;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255,255,255,0.07);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
        }
        
        label {
            display: block;
            color: #00d4ff;
            margin-bottom: 6px;
            margin-top: 15px;
            font-weight: bold;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 1em;
        }
        
        input::placeholder, textarea::placeholder {
            color: #888;
        }
        
        textarea { height: 90px; resize: vertical; }
        
        select option { background: #302b63; }
        
        .btn {
            width: 100%;
            padding: 14px;
            margin-top: 20px;
            background: linear-gradient(135deg, #00d4ff, #a855f7);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
        }
        
        .btn:hover { opacity: 0.9; }
        
        /* Result */
        #result { display: none; }
        
        .score-box {
            text-align: center;
            padding: 20px;
        }
        
        .score-number {
            font-size: 5em;
            font-weight: bold;
        }
        
        .green { color: #00ff88; }
        .yellow { color: #ffdd00; }
        .red { color: #ff4444; }
        
        .verdict-text {
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            margin: 10px 0;
        }
        
        .risk-text {
            text-align: center;
            color: #aaa;
            margin-bottom: 20px;
        }
        
        .reason {
            background: rgba(255,255,255,0.05);
            border-left: 4px solid #00d4ff;
            padding: 10px 15px;
            margin: 8px 0;
            border-radius: 5px;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 30px;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid rgba(255,255,255,0.1);
            border-top: 4px solid #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 15px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
<div class="container">
    
    <h1>🔍 Fake Profile Detector</h1>
    <p class="subtitle">Profile details daalo aur pata karo - Real hai ya Fake!</p>
    
    <!-- Form -->
    <div class="card" id="form-section">
        
        <label>👤 Full Name *</label>
        <input 
            type="text" 
            id="name" 
            placeholder="Jaise: Rahul Sharma ya John123"
        >
        
        <label>📝 Bio / Headline</label>
        <textarea 
            id="bio" 
            placeholder="Profile ki bio yahan likho... 
Jaise: 'CEO at XYZ | Crypto Trader | DM for investment'"
        ></textarea>
        
        <label>🔗 Connections / Followers kitne hain?</label>
        <input 
            type="number" 
            id="connections" 
            placeholder="Jaise: 500"
            min="0"
        >
        
        <label>🖼️ Profile Picture hai?</label>
        <select id="pic">
            <option value="yes">✅ Haan, picture hai</option>
            <option value="no">❌ Nahi, picture nahi hai</option>
        </select>
        
        <label>📅 Account kitna purana hai?</label>
        <select id="age">
            <option value="new">🆕 1 hafte se kam (Bilkul naya)</option>
            <option value="month">📅 1 mahine se kam</option>
            <option value="old" selected>✅ 1 mahine se zyada</option>
            <option value="veteran">⭐ 1 saal se zyada (Purana)</option>
        </select>
        
        <label>📮 Posts / Activity kaisi hai?</label>
        <select id="posts">
            <option value="0">❌ Koi post nahi</option>
            <option value="few">⚠️ 1-5 posts hain</option>
            <option value="many" selected>✅ 5 se zyada posts hain</option>
        </select>
        
        <button class="btn" onclick="checkProfile()">
            🔍 CHECK KARO!
        </button>
        
    </div>
    
    <!-- Loading -->
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Profile check ho rahi hai...</p>
    </div>
    
    <!-- Result -->
    <div class="card" id="result">
        
        <div class="score-box">
            <div class="score-number" id="score-num">--</div>
            <div style="color:#aaa;">out of 100</div>
        </div>
        
        <div class="verdict-text" id="verdict">--</div>
        <div class="risk-text" id="risk">--</div>
        
        <hr style="border-color:rgba(255,255,255,0.1); margin:15px 0;">
        
        <h3 style="margin-bottom:10px;">📋 Detail Report:</h3>
        <div id="reasons"></div>
        
        <button class="btn" onclick="resetForm()">
            🔄 Dobara Check Karo
        </button>
        
    </div>

</div>

<script>
async function checkProfile() {
    
    const name = document.getElementById('name').value.trim();
    
    if (!name) {
        alert('❌ Naam daalna zaroori hai!');
        return;
    }
    
    // Data collect karo
    const formData = {
        name: name,
        bio: document.getElementById('bio').value.trim(),
        connections: parseInt(document.getElementById('connections').value) || 0,
        has_pic: document.getElementById('pic').value === 'yes',
        account_age: document.getElementById('age').value,
        posts: document.getElementById('posts').value
    };
    
    // Loading dikhao
    document.getElementById('form-section').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').style.display = 'none';
    
    try {
        // Server ko bhejo
        const response = await fetch('/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        // Result dikhao
        showResult(result);
        
    } catch(error) {
        alert('Error aaya: ' + error.message);
        document.getElementById('form-section').style.display = 'block';
        document.getElementById('loading').style.display = 'none';
    }
}

function showResult(result) {
    document.getElementById('loading').style.display = 'none';
    
    const scoreEl = document.getElementById('score-num');
    const verdictEl = document.getElementById('verdict');
    const riskEl = document.getElementById('risk');
    const reasonsEl = document.getElementById('reasons');
    
    // Score color
    scoreEl.textContent = result.score;
    scoreEl.className = 'score-number ';
    
    if (result.score >= 70) {
        scoreEl.className += 'green';
    } else if (result.score >= 40) {
        scoreEl.className += 'yellow';
    } else {
        scoreEl.className += 'red';
    }
    
    verdictEl.textContent = result.verdict;
    riskEl.textContent = '⚠️ Risk Level: ' + result.risk_level;
    
    // Reasons
    reasonsEl.innerHTML = '';
    result.reasons.forEach(function(reason) {
        const div = document.createElement('div');
        div.className = 'reason';
        div.textContent = reason;
        reasonsEl.appendChild(div);
    });
    
    document.getElementById('result').style.display = 'block';
}

function resetForm() {
    document.getElementById('result').style.display = 'none';
    document.getElementById('form-section').style.display = 'block';
    document.getElementById('name').value = '';
    document.getElementById('bio').value = '';
    document.getElementById('connections').value = '';
    window.scrollTo({top: 0, behavior: 'smooth'});
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)


@app.route('/check', methods=['POST'])
def check():
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data received'}), 400
    
    analyzer = ProfileAnalyzer()
    scorer = ProfileScorer()
    
    # Profile data banao
    profile_data = {
        'url': 'manual',
        'name': data.get('name', ''),
        'bio': data.get('bio', ''),
        'profile_pic': data.get('has_pic', False),
        'followers': data.get('connections', 0),
        'connections': data.get('connections', 0),
        'posts_count': (
            5 if data.get('posts') == 'many' else
            2 if data.get('posts') == 'few' else 0
        ),
        'join_date': 'Unknown'
    }
    
    # Age result
    age = data.get('account_age', 'old')
    age_map = {
        'new': {'suspicious': True, 'reason': 'Account sirf 1 hafte purana hai', 'age_days': 3},
        'month': {'suspicious': True, 'reason': 'Account 1 mahine se kam purana', 'age_days': 20},
        'old': {'suspicious': False, 'reason': 'Account theek purana hai', 'age_days': 180},
        'veteran': {'suspicious': False, 'reason': 'Account bahut purana hai', 'age_days': 500},
    }
    
    analysis_results = {
        'bio_analysis': analyzer.analyze_bio(profile_data['bio']),
        'name_flags': analyzer.check_name(profile_data['name']),
        'age_check': age_map.get(age, age_map['old']),
        'suspicious_links': analyzer.check_links_in_bio(profile_data['bio'])
    }
    
    result = scorer.calculate_score(profile_data, analysis_results)
    
    # CSV mein save karo
    try:
        os.makedirs('results', exist_ok=True)
        file_path = 'results/results.csv'
        write_header = not os.path.exists(file_path)
        
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(['Name', 'Score', 'Risk', 'Verdict', 'Time'])
            writer.writerow([
                data.get('name', 'Unknown'),
                result['score'],
                result['risk_level'],
                result['verdict'],
                datetime.now().strftime('%Y-%m-%d %H:%M')
            ])
    except:
        pass
    
    return jsonify(result)


if __name__ == '__main__':
    print("\n" + "="*40)
    print("✅ Server chal raha hai!")
    print("✅ Browser mein kholo:")
    print("   http://localhost:5000")
    print("="*40 + "\n")
app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))