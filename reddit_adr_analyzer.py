import requests
import requests.auth
from rich import print
import argparse
import json
from pathlib import Path
import time
import re
import csv
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Set

CLIENT_ID = 'C_-eUtUmYyIzctlGgN-JAQ'
CLIENT_SECRET = 'd_fP7GSUzB9GxrPhItfRBGXpuV6Ndg'
USERNAME = 'HolidayAd7928'
PASSWORD = '8w6Ha-FZS2b5yX:'

client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
post_data = {'grant_type': 'password', 'username': USERNAME, 'password': PASSWORD}
headers = {'User-Agent': 'RedditADRAnalyzer/2.0 by HolidayAd7928'}

TOKEN_ACCESS_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
response = requests.post(TOKEN_ACCESS_ENDPOINT, data=post_data, headers=headers, auth=client_auth)

token_id = None
try:
    token_json = response.json()
    if response.status_code == 200 and isinstance(token_json, dict):
        token_id = token_json.get('access_token')
        if not token_id:
            print('Warning: authentication returned 200 but no access_token found')
    else:
        print(f'Warning: token request returned status {response.status_code}')
except Exception as e:
    print(f'Authentication error: {e}')

# ========== CONFIGURATION ==========
SUBREDDITS = [
    'ADHD', 'ADHDmemes', 'adhdwomen', 'adhd_anxiety',
    'ADHD_partners', 'ADHDUK', 'VyvanseADHD', 'AdhdRelationships',
]

# Enhanced medication list with common names and brand names
MEDICATIONS = {
    # Stimulants
    'adderall', 'vyvanse', 'ritalin', 'concerta', 'focalin', 'dexedrine', 
    'methylphenidate', 'lisdexamfetamine', 'dextroamphetamine', 'amphetamine',
    'mydayis', 'quillivant', 'daytrana', 'evekeo', 'zenzedi', 'dyanavel',
    # Non-stimulants
    'strattera', 'atomoxetine', 'intuniv', 'guanfacine', 'kapvay', 'clonidine',
    'wellbutrin', 'bupropion', 'qelbree', 'viloxazine', 'wellbutrin xl',
    # Antidepressants commonly used with ADHD
    'prozac', 'fluoxetine', 'zoloft', 'sertraline', 'lexapro', 'escitalopram',
    'celexa', 'citalopram', 'effexor', 'venlafaxine', 'cymbalta', 'duloxetine',
    'paxil', 'paroxetine', 'pristiq', 'desvenlafaxine', 'remeron', 'mirtazapine',
    'trazodone', 'trintellix', 'vortioxetine', 'celex', 'effexor xr', 'paxil cr',
    'viibryd', 'vilazodone', 'amitriptyline', 'tramadol', 'nefazodone', 'nortriptyline',
    'desipramine', 'doxepin', 'amoxapine', 'fluvoxamine', 'imipramine', 'ketamine',
    'nardil', 'norpramin', 'parnate', 'phenelzine', 'symbyax', 'tranylcypromine',
    'clomipramine', 'emsam', 'pamelor', 'selegiline', 'esketamine', 'isocarboxazid',
    'levomilnacipran', 'marplan', 'protriptyline', 'spravato', 'trimipramine',
    # Anxiety medications
    'xanax', 'alprazolam', 'ativan', 'lorazepam', 'klonopin', 'clonazepam',
    'valium', 'diazepam', 'buspar', 'buspirone', 'hydroxyzine', 'vistaril',
    'propranolol', 'gabapentin', 'neurontin', 'lyrica', 'pregabalin', 'atenolol', 'nadolol',
    'alprazolam intensol', 'tranxene', 'lorazepam intensol', 'clorazepate', 'diazepam intensol',
    'loreev xr', 'oxazepam', 'cannabidiol', 'chlordiazepoxide', 'meprobamate',
    'tranxene t-tab', 'trifluoperazine', 'oxcarbazepine', 'phenytoin',
    # Mood stabilizers / Antipsychotics
    'abilify', 'aripiprazole', 'risperdal', 'risperidone', 'seroquel', 'quetiapine',
    'zyprexa', 'olanzapine', 'latuda', 'lurasidone', 'rexulti', 'brexpiprazole',
    'lamictal', 'lamotrigine', 'lithium', 'depakote', 'valproate', 'paliperidone',
    # Supplements/Other
    'modafinil', 'provigil', 'armodafinil', 'nuvigil', 'amantadine', 'deplin',
    'l-methylfolate', 'methylin', 'niacin', 'methyl folate forte',
    'forfivo', 'budeprion', 'raldesy', 'aplenzin', 'fetzima', 'irenka', 'xaquil',
    # Slang terms for medications
    'addy', 'addies', 'study meds', 'focus pills', 'concentration vitamins',
    'executive function pills', 'brain fuel', 'productivity pills', 'smarties',
    'attention juice', 'zoomies in a pill', 'brain batteries',
    'antideps', 'happy pills', 'miracle drugs', 'brain meds', 'mood meds',
    'serotonin pills', 'stability pills', 'emotional support meds', 'chemical helpers',
    'daily dose', 'brain candy', 'psych meds', 'anti-depressy', 'depression pills',
    'my silly little meds', 'my scripts',
    # Psilocybin
    'boom', 'boomers', 'magic mushrooms', 'simple simon', 'caps', 'shrooms',
    'buttons', 'mushies', 'psilocybin',
    # LSD
    'lsd', 'haze', 'california sunshine', 'white lightning', 'mellow yellow',
    'tabs', 'trips', 'microdots', 'microdose', 'dots', 'blotter', 'cubes',
    # Cannabis
    'weed', 'za', 'sticky', 'grass', 'exotic', 'flower', 'gas', 'wax pen',
    'oil', 'dab', 'amnesia', 'bizarro', 'blaze', 'bliss', 'brain freeze',
    'buzz haze', 'cloud 10', 'dr. feel good', 'green peace', 'geeked',
    'geeked up', 'sky high', 'snake bite', 'potpourri', 'herbal incense',
    'blunt', 'bowl', 'bong', 'bubbler', 'doobie', 'fatty', 'gravity bong',
    'j', 'jay', 'joint', 'left-handed cigarette', 'one-hitter', 'percolator',
    'piece', 'pipe', 'rig', 'roach', 'spliff', 'vape', 'water pipe', 'cannabis',
    'marijuana', 'thc', 'cbd', 'edibles',
}

# ADR-specific keywords organized by category
ADR_KEYWORDS = {
    'side_effect_indicators': [
        'side effect', 'side-effect', 'adverse', 'reaction', 'bad reaction',
        'caused', 'making me', 'made me', 'giving me', 'experiencing',
        'suffering from', 'dealing with', 'struggling with', 'issues with',
        'problems with', 'concern', 'worried about', 'scared of',
        'negative effect', 'downsides', 'drawbacks', 'complications',
        'affecting me', 'messing me up', 'screwing with', 'not right',
        'feeling off', 'something wrong', 'not myself', 'weird symptoms',
    ],
    'withdrawal_tolerance': [
        'withdrawal', 'withdrawing', 'coming off', 'stopping', 'quit',
        'discontinuation', 'tolerance', 'not working anymore', 'stopped working',
        'losing effect', 'building tolerance', 'wears off', 'crash', 'rebound',
        'tapering', 'weaning off', 'cold turkey', 'detox', 'dependency',
        'addicted', 'addiction', 'dependence', 'need more', 'need higher dose',
        'doesnt work', "doesn't work", 'lost effectiveness', 'reduced effect',
    ],
    'physical_symptoms': [
        'headache', 'migraine', 'nausea', 'vomiting', 'diarrhea', 'constipation',
        'stomach pain', 'appetite loss', 'weight loss', 'weight gain',
        'dry mouth', 'sweating', 'tremor', 'shaking', 'dizziness', 'dizzy',
        'fatigue', 'tired', 'exhausted', 'insomnia', 'cant sleep', "can't sleep",
        'sleep issues', 'racing heart', 'palpitations', 'chest pain', 'shortness of breath',
        'tics', 'twitching', 'muscle pain', 'joint pain', 'rash', 'itching',
        'blurred vision', 'tinnitus', 'ringing ears', 'numbness',
        'abdominal pain', 'bloating', 'gas', 'indigestion', 'acid reflux',
        'hot flashes', 'cold sweats', 'night sweats', 'chills', 'fever',
        'weakness', 'lethargy', 'sluggish', 'heavy limbs', 'body aches',
        'restless legs', 'jaw clenching', 'teeth grinding', 'bruxism',
        'hair loss', 'skin problems', 'acne', 'hives', 'swelling',
        'back pain', 'stiff neck', 'sore muscles', 'cramping', 'spasms',
        'vertigo', 'lightheaded', 'unsteady', 'balance issues',
    ],
    'psychological_symptoms': [
        'anxiety', 'anxious', 'panic', 'depression', 'depressed', 'sad',
        'irritable', 'irritability', 'angry', 'rage', 'mood swings', 'emotional',
        'crying', 'suicidal', 'suicide', 'self harm', 'intrusive thoughts',
        'paranoid', 'paranoia', 'hallucination', 'zombie', 'flat', 'numb',
        'brain fog', 'foggy', 'confused', 'memory loss', 'forgetful',
        'dissociation', 'derealisation', 'depersonalization',
        'panic attacks', 'anxiety attacks', 'agitation', 'restless', 'on edge',
        'nightmares', 'vivid dreams', 'sleep paralysis', 'night terrors',
        'hopeless', 'worthless', 'guilt', 'shame', 'emptiness',
        'anhedonia', 'no motivation', 'apathy', 'emotionally blunted',
        'manic', 'hypomania', 'racing thoughts', 'impulsive', 'reckless',
        'obsessive', 'compulsive', 'rumination', 'overthinking',
        'derealization', 'detached', 'unreal', 'spacey', 'out of it',
    ],
    'cardiovascular': [
        'heart rate', 'blood pressure', 'hypertension', 'tachycardia',
        'arrhythmia', 'chest tightness', 'fainting', 'syncope',
        'elevated heart rate', 'high blood pressure', 'low blood pressure',
        'irregular heartbeat', 'skipped beats', 'heart pounding',
    ],
    'cognitive': [
        'brain zaps', 'zaps', 'focus worse', 'cant focus', "can't focus",
        'concentration', 'attention span', 'memory', 'cognitive',
        'mental fog', 'thinking slower', 'processing slow', 'word finding',
        'cant think', "can't think", 'confusion', 'disoriented',
        'short term memory', 'forgetting things', 'lost my train of thought',
    ],
    'gastrointestinal': [
        'stomach issues', 'digestive problems', 'upset stomach', 'queasy',
        'gi issues', 'bowel problems', 'ibs symptoms',
    ],
    'neurological': [
        'seizures', 'convulsions', 'nerve pain', 'neuropathy', 'pins and needles',
        'tingling', 'burning sensation', 'electric shocks',
    ],
}

# Severity indicators
SEVERITY_INDICATORS = {
    'severe': [
        'severe', 'extreme', 'unbearable', 'terrible', 'awful', 'horrible',
        'emergency', 'hospitalized', 'er visit', 'urgent care', 'doctor immediately',
        'cant function', "can't function", 'unable to', 'debilitating',
        'excruciating', 'intolerable', 'life threatening', 'life-threatening',
        'crisis', 'critical', 'dangerous', 'scary', 'terrifying',
        'worst ever', 'worst pain', 'never felt this bad', 'thought i was dying',
        'called 911', 'ambulance', 'suicide watch', 'psychiatric hold',
        'cant work', "can't work", 'cant leave bed', "can't leave bed",
        'bedridden', 'incapacitated', 'completely non-functional',
    ],
    'moderate': [
        'bad', 'worse', 'concerning', 'worrying', 'uncomfortable', 'difficult',
        'hard to', 'struggling', 'noticeable', 'significant',
        'pretty bad', 'rough', 'tough', 'challenging', 'problematic',
        'interfering', 'affecting daily life', 'impacting work',
        'cant ignore', "can't ignore", 'distracting', 'bothersome',
        'unpleasant', 'miserable', 'suffering', 'hard to deal with',
    ],
    'mild': [
        'mild', 'slight', 'minor', 'a little', 'somewhat', 'manageable',
        'tolerable', 'annoying', 'inconvenient',
        'barely noticeable', 'hardly', 'not too bad', 'livable',
        'can deal with', 'can handle', 'bearable', 'acceptable',
        'minor nuisance', 'small issue', 'tiny bit', 'occasionally',
    ],
}

# Positive sentiment (to filter out positive mentions)
POSITIVE_INDICATORS = [
    'helped', 'helping', 'better', 'improved', 'improvement', 'great', 'amazing',
    'wonderful', 'working well', 'life changing', 'life-changing', 'best decision',
    'no side effects', 'no issues', 'minimal side effects', 'worth it',
    'game changer', 'miracle', 'blessed', 'grateful', 'thankful',
    'finally working', 'doing great', 'feel good', 'feel better', 'feeling better',
    'highly recommend', 'recommend', 'love it', 'love this', 'works great',
    'works well', 'effective', 'positive effects', 'positive experience',
    'no complaints', 'happy with', 'satisfied', 'perfect', 'excellent',
    'outstanding', 'fantastic', 'incredible', 'best thing', 'saved my life',
    'totally fine', 'all good', 'going well', 'success', 'successful',
    'beneficial', 'advantageous', 'helpful', 'productive', 'focus improved',
    'mood improved', 'anxiety reduced', 'depression lifted', 'symptom free',
]

MAX_ITERATIONS_SAFETY = 800
POSTS_PER_PAGE = 100

# ========== DATA STRUCTURES ==========
all_posts = []
all_comments = []
adr_mentions = []  # Will store detailed ADR information


# ========== HELPER FUNCTIONS ==========

def normalize_medication_name(text: str) -> Set[str]:
    """Extract and normalize medication names from text."""
    text_lower = text.lower()
    found_meds = set()
    
    for med in MEDICATIONS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(med) + r'\b'
        if re.search(pattern, text_lower):
            found_meds.add(med)
    
    return found_meds


def extract_adr_context(text: str, med_name: str, context_window: int = 200) -> List[Dict]:
    """
    Extract context around medication mentions that include ADR indicators.
    Returns list of ADR mentions with context.
    """
    text_lower = text.lower()
    adr_contexts = []
    
    # Find all medication mentions
    pattern = r'\b' + re.escape(med_name) + r'\b'
    for match in re.finditer(pattern, text_lower):
        med_pos = match.start()
        
        # Extract context window
        start = max(0, med_pos - context_window)
        end = min(len(text), med_pos + len(med_name) + context_window)
        context = text[start:end]
        context_lower = context.lower()
        
        # Check for ADR indicators in context
        adr_types = []
        symptoms = []
        severity = None
        is_positive = False
        
        # Check each ADR category
        for category, keywords in ADR_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context_lower:
                    adr_types.append(category)
                    symptoms.append(keyword)
        
        # Check severity
        for sev_level, keywords in SEVERITY_INDICATORS.items():
            for keyword in keywords:
                if keyword in context_lower:
                    severity = sev_level
                    break
            if severity:
                break
        
        # Check if positive mention
        for pos_ind in POSITIVE_INDICATORS:
            if pos_ind in context_lower:
                is_positive = True
                break
        
        # Only record if ADR indicators found and not purely positive
        if adr_types and not is_positive:
            adr_contexts.append({
                'medication': med_name,
                'context': context.strip(),
                'adr_types': list(set(adr_types)),
                'symptoms': list(set(symptoms)),
                'severity': severity,
                'position': med_pos,
            })
    
    return adr_contexts


def calculate_sentiment_score(context: str) -> float:
    """
    Simple sentiment calculation: -1 (very negative) to 1 (very positive)
    """
    context_lower = context.lower()
    
    # Count negative indicators
    negative_count = sum(1 for kw_list in ADR_KEYWORDS.values() for kw in kw_list if kw in context_lower)
    negative_count += sum(1 for kw_list in SEVERITY_INDICATORS.values() for kw in kw_list if kw in context_lower)
    
    # Count positive indicators
    positive_count = sum(1 for kw in POSITIVE_INDICATORS if kw in context_lower)
    
    # Simple scoring
    if negative_count == 0 and positive_count == 0:
        return 0
    
    total = negative_count + positive_count
    return (positive_count - negative_count) / total


# ========== MAIN SCRAPING LOGIC ==========

def fetch_subreddit_data(subreddit: str, use_oauth: bool, base_endpoint: str, 
                         headers_get: dict) -> Tuple[List, List]:
    """Fetch posts and comments from a subreddit."""
    print(f"\n Fetching from r/{subreddit} ...")
    
    posts_collected = []
    comments_collected = []
    after_key = None
    iterations = 0
    
    while iterations < MAX_ITERATIONS_SAFETY:
        iterations += 1
        
        params_get = {'limit': POSTS_PER_PAGE, 'after': after_key}
        url = f"{base_endpoint}/r/{subreddit}/new"
        if not use_oauth:
            url += '.json'
        
        time.sleep(2)  # Rate limiting
        
        try:
            resp = requests.get(url, headers=headers_get, params=params_get)
            if resp.status_code != 200:
                print(f"Failed to fetch r/{subreddit} (status={resp.status_code})")
                break
            
            data = resp.json()
            posts = data['data']['children']
            
            if not posts:
                print(f"No more posts for r/{subreddit}")
                break
            
            for post in posts:
                post_data = post['data']
                
                # Extract post information
                post_record = {
                    'subreddit': subreddit,
                    'id': post_data.get('id'),
                    'title': post_data.get('title', ''),
                    'selftext': post_data.get('selftext', ''),
                    'author': post_data.get('author', '[deleted]'),
                    'created_utc': post_data.get('created_utc'),
                    'score': post_data.get('score', 0),
                    'num_comments': post_data.get('num_comments', 0),
                    'url': post_data.get('url', ''),
                }
                
                posts_collected.append(post_record)
                
                # Fetch comments for this post
                if post_data.get('num_comments', 0) > 0:
                    time.sleep(1)
                    comments = fetch_post_comments(
                        subreddit, post_data.get('id'), 
                        use_oauth, base_endpoint, headers_get
                    )
                    comments_collected.extend(comments)
            
            # Get next page
            after_key = data['data'].get('after')
            if not after_key:
                break
            
            print(f"  Iteration {iterations}: fetched {len(posts)} posts")
            
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            break
    
    print(f"  Total: {len(posts_collected)} posts, {len(comments_collected)} comments")
    return posts_collected, comments_collected


def fetch_post_comments(subreddit: str, post_id: str, use_oauth: bool, 
                        base_endpoint: str, headers_get: dict) -> List:
    """Fetch all comments for a specific post."""
    comments = []
    
    try:
        url = f"{base_endpoint}/r/{subreddit}/comments/{post_id}"
        if not use_oauth:
            url += '.json'
        
        resp = requests.get(url, headers=headers_get)
        if resp.status_code != 200:
            return comments
        
        data = resp.json()
        
        # Reddit returns [post, comments] structure
        if len(data) < 2:
            return comments
        
        comment_listing = data[1]['data']['children']
        
        def extract_comments(comment_list, depth=0):
            for item in comment_list:
                if item['kind'] == 't1':  # Comment
                    comment_data = item['data']
                    comments.append({
                        'post_id': post_id,
                        'comment_id': comment_data.get('id'),
                        'body': comment_data.get('body', ''),
                        'author': comment_data.get('author', '[deleted]'),
                        'created_utc': comment_data.get('created_utc'),
                        'score': comment_data.get('score', 0),
                        'depth': depth,
                    })
                    
                    # Process replies recursively
                    replies = comment_data.get('replies')
                    if replies and isinstance(replies, dict):
                        reply_children = replies.get('data', {}).get('children', [])
                        extract_comments(reply_children, depth + 1)
        
        extract_comments(comment_listing)
        
    except Exception as e:
        print(f"Error fetching comments for post {post_id}: {e}")
    
    return comments


def analyze_adr_mentions(posts: List, comments: List) -> List:
    """Analyze posts and comments for ADR mentions."""
    adr_data = []
    
    print("\n Analyzing posts for ADRs...")
    for post in posts:
        combined_text = f"{post['title']} {post['selftext']}"
        medications = normalize_medication_name(combined_text)
        
        for med in medications:
            adr_contexts = extract_adr_context(combined_text, med)
            
            for adr in adr_contexts:
                adr_data.append({
                    'source': 'post',
                    'source_id': post['id'],
                    'subreddit': post['subreddit'],
                    'medication': med,
                    'author': post['author'],
                    'timestamp': datetime.fromtimestamp(post['created_utc']) if post['created_utc'] else None,
                    'score': post['score'],
                    'adr_types': adr['adr_types'],
                    'symptoms': adr['symptoms'],
                    'severity': adr['severity'],
                    'context': adr['context'],
                    'sentiment': calculate_sentiment_score(adr['context']),
                    'full_text': combined_text,
                })
    
    print("\n Analyzing comments for ADRs...")
    for comment in comments:
        medications = normalize_medication_name(comment['body'])
        
        for med in medications:
            adr_contexts = extract_adr_context(comment['body'], med)
            
            for adr in adr_contexts:
                adr_data.append({
                    'source': 'comment',
                    'source_id': comment['comment_id'],
                    'post_id': comment['post_id'],
                    'medication': med,
                    'author': comment['author'],
                    'timestamp': datetime.fromtimestamp(comment['created_utc']) if comment['created_utc'] else None,
                    'score': comment['score'],
                    'adr_types': adr['adr_types'],
                    'symptoms': adr['symptoms'],
                    'severity': adr['severity'],
                    'context': adr['context'],
                    'sentiment': calculate_sentiment_score(adr['context']),
                    'full_text': comment['body'],
                })
    
    return adr_data


# ========== TREND ANALYSIS & VISUALIZATION ==========

def create_trend_visualizations(adr_data: List, output_dir: Path):
    """Create comprehensive trend visualizations."""
    output_dir.mkdir(exist_ok=True)
    
    if not adr_data:
        print("No ADR data to visualize")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(adr_data)
    df['date'] = pd.to_datetime(df['timestamp'])
    df['year_month'] = df['date'].dt.to_period('M')
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (14, 8)
    
    # 1. ADR mentions over time by medication
    print("\n Creating timeline visualization...")
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Get top 10 medications by ADR count
    top_meds = df['medication'].value_counts().head(10).index
    df_top = df[df['medication'].isin(top_meds)]
    
    for med in top_meds:
        med_data = df_top[df_top['medication'] == med]
        timeline = med_data.groupby('year_month').size()
        timeline.index = timeline.index.to_timestamp()
        ax.plot(timeline.index, timeline.values, marker='o', label=med, linewidth=2)
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Number of ADR Mentions', fontsize=12)
    ax.set_title('ADR Mentions Over Time by Medication (Top 10)', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / 'adr_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. ADR types distribution
    print(" Creating ADR types distribution...")
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Flatten ADR types
    all_adr_types = []
    for types in df['adr_types']:
        all_adr_types.extend(types)
    
    adr_type_counts = Counter(all_adr_types)
    types, counts = zip(*adr_type_counts.most_common(15))
    
    bars = ax.barh(range(len(types)), counts, color=sns.color_palette("viridis", len(types)))
    ax.set_yticks(range(len(types)))
    ax.set_yticklabels(types)
    ax.set_xlabel('Number of Mentions', fontsize=12)
    ax.set_title('Most Common ADR Categories', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(count, i, f' {count}', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'adr_categories.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Top symptoms by medication
    print(" Creating symptom heatmap...")
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Get top medications and symptoms
    top_meds_list = df['medication'].value_counts().head(15).index.tolist()
    
    all_symptoms = []
    for symptoms in df['symptoms']:
        all_symptoms.extend(symptoms)
    top_symptoms = [s for s, _ in Counter(all_symptoms).most_common(20)]
    
    # Create matrix
    heatmap_data = []
    for med in top_meds_list:
        med_df = df[df['medication'] == med]
        row = []
        for symptom in top_symptoms:
            count = sum(1 for symptoms in med_df['symptoms'] if symptom in symptoms)
            row.append(count)
        heatmap_data.append(row)
    
    sns.heatmap(heatmap_data, xticklabels=top_symptoms, yticklabels=top_meds_list,
                cmap='YlOrRd', annot=True, fmt='d', cbar_kws={'label': 'Mention Count'}, ax=ax)
    ax.set_title('ADR Symptoms by Medication (Heatmap)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(output_dir / 'symptom_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Severity distribution
    print(" Creating severity distribution...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    severity_counts = df['severity'].value_counts()
    colors = {'severe': '#d62728', 'moderate': '#ff7f0e', 'mild': '#2ca02c'}
    
    bars = ax.bar(severity_counts.index, severity_counts.values, 
                  color=[colors.get(s, '#7f7f7f') for s in severity_counts.index])
    ax.set_xlabel('Severity Level', fontsize=12)
    ax.set_ylabel('Number of ADR Mentions', fontsize=12)
    ax.set_title('ADR Severity Distribution', fontsize=14, fontweight='bold')
    
    for bar, count in zip(bars, severity_counts.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}', ha='center', va='bottom', fontsize=11)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'severity_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 5. Sentiment analysis
    print(" Creating sentiment analysis...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    top_10_meds = df['medication'].value_counts().head(10).index
    sentiment_by_med = []
    
    for med in top_10_meds:
        med_sentiments = df[df['medication'] == med]['sentiment'].dropna()
        sentiment_by_med.append(med_sentiments.values)
    
    bp = ax.boxplot(sentiment_by_med, labels=top_10_meds, patch_artist=True)
    
    for patch in bp['boxes']:
        patch.set_facecolor('#3498db')
        patch.set_alpha(0.7)
    
    ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, label='Neutral')
    ax.set_xlabel('Medication', fontsize=12)
    ax.set_ylabel('Sentiment Score (-1 to 1)', fontsize=12)
    ax.set_title('Sentiment Distribution by Medication', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    ax.legend()
    plt.tight_layout()
    plt.savefig(output_dir / 'sentiment_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 6. Monthly trend for all ADRs
    print(" Creating monthly trend...")
    fig, ax = plt.subplots(figsize=(14, 6))
    
    monthly_counts = df.groupby('year_month').size()
    monthly_counts.index = monthly_counts.index.to_timestamp()
    
    ax.plot(monthly_counts.index, monthly_counts.values, marker='o', 
            linewidth=2, markersize=8, color='#e74c3c')
    ax.fill_between(monthly_counts.index, monthly_counts.values, alpha=0.3, color='#e74c3c')
    
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Total ADR Mentions', fontsize=12)
    ax.set_title('Overall ADR Mentions Trend', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / 'monthly_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n All visualizations saved to {output_dir}/")


def generate_summary_statistics(adr_data: List, output_path: Path):
    """Generate comprehensive summary statistics."""
    if not adr_data:
        return
    
    df = pd.DataFrame(adr_data)
    
    summary = {
        'total_adr_mentions': len(df),
        'unique_medications': df['medication'].nunique(),
        'date_range': {
            'start': df['timestamp'].min().isoformat() if not df.empty else None,
            'end': df['timestamp'].max().isoformat() if not df.empty else None,
        },
        'top_medications': df['medication'].value_counts().head(20).to_dict(),
        'sources': df['source'].value_counts().to_dict(),
        'severity_distribution': df['severity'].value_counts().to_dict(),
        'average_sentiment': float(df['sentiment'].mean()) if 'sentiment' in df else None,
        'most_common_symptoms': {},
        'most_common_adr_types': {},
    }
    
    # Flatten and count symptoms
    all_symptoms = []
    for symptoms in df['symptoms']:
        all_symptoms.extend(symptoms)
    summary['most_common_symptoms'] = dict(Counter(all_symptoms).most_common(30))
    
    # Flatten and count ADR types
    all_types = []
    for types in df['adr_types']:
        all_types.extend(types)
    summary['most_common_adr_types'] = dict(Counter(all_types).most_common(10))
    
    # Save summary
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n Summary statistics saved to {output_path}")


# ========== MAIN EXECUTION ==========

def main():
    parser = argparse.ArgumentParser(description='Analyze ADRs from ADHD-related subreddits')
    parser.add_argument('--subreddits', '-s', help='Comma-separated subreddit list')
    parser.add_argument('--output-dir', '-o', help='Output directory', default='adr_analysis_output')
    parser.add_argument('--no-visualizations', action='store_true', help='Skip creating visualizations')
    args = parser.parse_args()
    
    if args.subreddits:
        global SUBREDDITS
        SUBREDDITS = [s.strip() for s in args.subreddits.split(',') if s.strip()]
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Setup OAuth
    USE_OAUTH = token_id is not None
    if USE_OAUTH:
        headers_get = {
            'User-Agent': 'RedditADRAnalyzer/2.0 by HolidayAd7928',
            'Authorization': f'bearer {token_id}'
        }
        base_endpoint = 'https://oauth.reddit.com'
    else:
        print('Using public endpoints (rate-limited)')
        headers_get = {'User-Agent': 'RedditADRAnalyzer/2.0 by HolidayAd7928'}
        base_endpoint = 'https://www.reddit.com'
    
    # Fetch data from all subreddits
    print("=" * 60)
    print("Starting Reddit ADR Analysis")
    print("=" * 60)
    
    for subreddit in SUBREDDITS:
        posts, comments = fetch_subreddit_data(
            subreddit, USE_OAUTH, base_endpoint, headers_get
        )
        all_posts.extend(posts)
        all_comments.extend(comments)
    
    print(f"\n Total collected: {len(all_posts)} posts, {len(all_comments)} comments")
    
    # Save raw data
    print("\n Saving raw data...")
    with open(output_dir / 'raw_posts.json', 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    
    with open(output_dir / 'raw_comments.json', 'w', encoding='utf-8') as f:
        json.dump(all_comments, f, indent=2, ensure_ascii=False)
    
    # Analyze ADRs
    print("\n Analyzing ADR mentions...")
    adr_data = analyze_adr_mentions(all_posts, all_comments)
    
    print(f"\n Found {len(adr_data)} ADR mentions")
    
    # Save ADR data
    with open(output_dir / 'adr_mentions.json', 'w', encoding='utf-8') as f:
        json.dump(adr_data, f, indent=2, ensure_ascii=False, default=str)
    
    # Save as CSV for easier analysis
    if adr_data:
        df = pd.DataFrame(adr_data)
        df['adr_types'] = df['adr_types'].apply(lambda x: '; '.join(x))
        df['symptoms'] = df['symptoms'].apply(lambda x: '; '.join(x))
        df.to_csv(output_dir / 'adr_mentions.csv', index=False, encoding='utf-8')
        print(f" ADR data saved to {output_dir / 'adr_mentions.csv'}")
    
    # Generate summary statistics
    generate_summary_statistics(adr_data, output_dir / 'summary_statistics.json')
    
    # Create visualizations
    if not args.no_visualizations and adr_data:
        print("\n Creating visualizations...")
        viz_dir = output_dir / 'visualizations'
        create_trend_visualizations(adr_data, viz_dir)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)
    print(f"\n Results saved in: {output_dir}/")
    print(f"  - Raw data: raw_posts.json, raw_comments.json")
    print(f"  - ADR mentions: adr_mentions.json, adr_mentions.csv")
    print(f"  - Summary: summary_statistics.json")
    if not args.no_visualizations:
        print(f"  - Visualizations: visualizations/")


if __name__ == '__main__':
    main()
