import streamlit as st
import feedparser
from collections import Counter
import string
from duckduckgo_search import DDGS
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Trend Hunter Gap Finder", page_icon="🧿", layout="wide")

# --- ENGINE: DEMAND (REDDIT) ---
@st.cache_data(ttl=600)
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

# --- ENGINE: SUPPLY (DUCKDUCKGO VIDEO SEARCH) ---
def check_supply_gap(keyword, genre_suffix):
    # This uses DuckDuckGo to search for videos (Site: YouTube mostly)
    # It is far more robust than scraping YouTube directly from a cloud server.
    query = f"{keyword} {genre_suffix}"
    
    results = []
    try:
        with DDGS() as ddgs:
            # Search specifically for videos
            results = list(ddgs.videos(query, max_results=10))
    except Exception as e:
        st.error(f"Search failed: {e}")
        return 0, []
    
    recent_count = 0
    recent_markers = ['hour', 'day', 'week', 'month'] 
    
    processed_results = []
    
    for r in results:
        # DDGS returns 'published' like "2 days ago"
        published = r.get('published', '').lower()
        title = r.get('title', 'Unknown')
        link = r.get('content', '') # DDGS uses 'content' for the video link often
        
        if any(marker in published for marker in recent_markers):
            recent_count += 1
            
        processed_results.append({'title': title, 'link': link, 'published': published})
            
    return recent_count, processed_results

# --- THE UI ---
st.title("🧿 Market Gap Finder")
st.markdown("Find the **Blue Ocean**: High Demand (Reddit) + Low Supply (YouTube).")

if st.button("🔄 Refresh Market Data"):
    st.cache_data.clear()
    st.rerun()

col1, col2, col3 = st.columns(3)

# --- HELPER FUNCTION FOR UI ---
def render_column(title, emoji, subreddits, genre_suffix, col):
    with col:
        st.header(f"{emoji} {title}")
        
        trends, context, total = get_trends_for_genre(subreddits)
        
        for rank, (word, count) in enumerate(trends):
            sat = (count / total) * 100
            st.divider()
            st.write(f"**#{rank+1} {word.upper()}**")
            st.caption(f"Demand: {sat:.1f}%")
            
            btn_key = f"btn_{title}_{word}"
            
            if st.button(f"🔍 Check Supply", key=btn_key):
                with st.spinner("Scanning Video Market..."):
                    recent_videos, video_data = check_supply_gap(word, genre_suffix)
                
                # LOGIC: SCORING THE GAP
                if recent_videos >= 5:
                    st.error(f"🔴 SATURATED ({recent_videos}/10 recent)")
                elif recent_videos >= 2:
                    st.warning(f"🟡 MODERATE ({recent_videos}/10 recent)")
                else:
                    st.success(f"🟢 WIDE OPEN GAP ({recent_videos}/10 recent)")
                    
                with st.expander("Competitors"):
                    for v in video_data[:3]:
                        st.write(f"📺 [{v['title']}]({v['link']}) - *{v['published']}*")
            
            with st.expander("Context"):
                for t in context[word][:2]: st.write(f"• {t}")

# --- RENDER COLUMNS ---
render_column("Horror", "👻", ['nosleep', 'shortscarystories', 'ruleshorror'], "scary story", col1)
render_column("Romantasy", "🧚‍♀️", ['relationships', 'FantasyRomance', 'ParanormalRomance'], "romance audio visual novel", col2)
render_column("Mystery", "🕵️", ['Glitch_in_the_Matrix', 'InternetMysteries', 'HighStrangeness'], "mystery explained", col3)
