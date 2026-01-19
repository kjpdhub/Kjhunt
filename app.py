import streamlit as st
import feedparser
from collections import Counter
import string
from youtubesearchpython import VideosSearch

# --- PAGE CONFIG ---
st.set_page_config(page_title="Trend Hunter Gap Finder", page_icon="🧿", layout="wide")

# --- ENGINE: DEMAND (REDDIT) ---
def get_trends_for_genre(subreddits):
    all_titles = set()
    for sub in subreddits:
        try:
            rss_urls = [f"https://www.reddit.com/r/{sub}/hot.rss", f"https://www.reddit.com/r/{sub}/top/.rss?t=week"]
            for url in rss_urls:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    clean = entry.title.replace("[Mod Post]", "").replace("[Announcement]", "")
                    all_titles.add(clean)
        except: pass

    words = []
    stop_words = {
        'the', 'and', 'a', 'to', 'of', 'in', 'i', 'is', 'that', 'it', 'for', 'my', 'on', 'with', 
        'this', 'was', 'have', 'but', 'be', 'are', 'just', 'me', 'from', 'at', 'so', 'not', 
        'story', 'part', 'update', 'series', 'final', 'like', 'one', 'up', 'out', 'what', 'when', 
        'all', 'do', 'no', 'found', 'about', 'how', 'an', 'they', 'we', 'she', 'he', 'by',
        'looking', 'help', 'question', 'advice', 'anyone', 'else', 'has', 'scary', 'horror', 
        'dating', 'relationship', 'confession', 'reddit', 'people', 'know', 'want', 'time', 'would',
        'really', 'because', 'friend', 'friends', 'girl', 'boy', 'year', 'years', 'been',
        'book', 'books', 'read', 'reading', 'series', 'recommendation', 'author', 'case', 'discussion'
    }

    word_to_titles = {}
    for title in all_titles:
        clean = title.lower().translate(str.maketrans('', '', string.punctuation))
        for w in clean.split():
            if w not in stop_words and len(w) > 3:
                words.append(w)
                if w not in word_to_titles: word_to_titles[w] = []
                word_to_titles[w].append(title)
    
    return Counter(words).most_common(5), word_to_titles, len(all_titles)

# --- ENGINE: SUPPLY (YOUTUBE) ---
def check_supply_gap(keyword, genre_suffix):
    # Search for the keyword + genre (e.g., "Basement Horror Story")
    query = f"{keyword} {genre_suffix}"
    videos_search = VideosSearch(query, limit=10)
    results = videos_search.result()['result']
    
    recent_count = 0
    recent_markers = ['hour', 'day', 'week', 'month'] # Markers for "Fresh" content
    
    for video in results:
        published = video.get('publishedTime', '')
        # Check if video was uploaded recently (contains '2 days ago', '1 week ago' etc)
        if any(marker in published for marker in recent_markers):
            recent_count += 1
            
    return recent_count, results

# --- THE UI ---
st.title("🧿 Market Gap Finder")
st.markdown("Find the **Blue Ocean**: High Demand (Reddit) + Low Supply (YouTube).")

if st.button("🚀 SCAN ALL MARKETS", type="primary", use_container_width=True):
    
    col1, col2, col3 = st.columns(3)
    
    # --- HELPER FUNCTION FOR UI ---
    def render_column(title, emoji, subreddits, genre_suffix, col):
        with col:
            st.header(f"{emoji} {title}")
            with st.spinner("Analyzing..."):
                trends, context, total = get_trends_for_genre(subreddits)
                
                for rank, (word, count) in enumerate(trends):
                    sat = (count / total) * 100
                    st.divider()
                    st.write(f"**#{rank+1} {word.upper()}** (Demand: {sat:.1f}%)")
                    
                    # --- THE GAP CHECKER ---
                    # We use a unique key for each button so they don't conflict
                    btn_key = f"btn_{title}_{word}"
                    if st.button(f"🔍 Check Supply", key=btn_key):
                        recent_videos, video_data = check_supply_gap(word, genre_suffix)
                        
                        # LOGIC: SCORING THE GAP
                        if recent_videos >= 5:
                            st.error(f"🔴 SATURATED ({recent_videos}/10 recent)")
                            st.caption("Too many videos this month. Hard to compete.")
                        elif recent_videos >= 2:
                            st.warning(f"🟡 MODERATE ({recent_videos}/10 recent)")
                            st.caption("Some competition. Needs a twist.")
                        else:
                            st.success(f"🟢 WIDE OPEN GAP ({recent_videos}/10 recent)")
                            st.caption("Go viral now! Nobody is covering this.")
                            
                        with st.expander("See Competitors"):
                            for v in video_data[:3]:
                                st.write(f"📺 [{v['title']}]({v['link']}) - *{v['publishedTime']}*")
                    
                    with st.expander("See Demand Context"):
                        for t in context[word][:2]: st.write(f"• {t}")

    # --- RENDER COLUMNS ---
    render_column("Horror", "👻", ['nosleep', 'shortscarystories', 'ruleshorror'], "scary story", col1)
    render_column("Romantasy", "🧚‍♀️", ['relationships', 'FantasyRomance', 'ParanormalRomance'], "romance audio visual novel", col2)
    render_column("Mystery", "🕵️", ['Glitch_in_the_Matrix', 'InternetMysteries', 'HighStrangeness'], "mystery explained", col3)

else:
    st.info("Tap 'SCAN' to load the market data.")
