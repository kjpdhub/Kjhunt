import streamlit as st
import feedparser
from collections import Counter
import string

# --- PAGE CONFIG ---
st.set_page_config(page_title="Trend Hunter Pro", page_icon="🧬", layout="wide")

# --- THE ENGINE ---
def get_trends_for_genre(subreddits):
    all_titles = set()
    
    # Scrape
    for sub in subreddits:
        try:
            # Check Hot + Top Weekly
            rss_urls = [f"https://www.reddit.com/r/{sub}/hot.rss", f"https://www.reddit.com/r/{sub}/top/.rss?t=week"]
            for url in rss_urls:
                feed = feedparser.parse(url)
                for entry in feed.entries:
                    clean = entry.title.replace("[Mod Post]", "").replace("[Announcement]", "")
                    all_titles.add(clean)
        except:
            pass

    # Analyze
    words = []
    stop_words = {
        'the', 'and', 'a', 'to', 'of', 'in', 'i', 'is', 'that', 'it', 'for', 'my', 'on', 'with', 
        'this', 'was', 'have', 'but', 'be', 'are', 'just', 'me', 'from', 'at', 'so', 'not', 
        'story', 'part', 'update', 'series', 'final', 'like', 'one', 'up', 'out', 'what', 'when', 
        'all', 'do', 'no', 'found', 'about', 'how', 'an', 'they', 'we', 'she', 'he', 'by',
        'looking', 'help', 'question', 'advice', 'anyone', 'else', 'has', 'scary', 'horror', 
        'dating', 'relationship', 'confession', 'reddit', 'people', 'know', 'want', 'time', 'would'
    }

    word_to_titles = {}
    for title in all_titles:
        clean = title.lower().translate(str.maketrans('', '', string.punctuation))
        for w in clean.split():
            if w not in stop_words and len(w) > 3:
                words.append(w)
                if w not in word_to_titles: word_to_titles[w] = []
                word_to_titles[w].append(title)
                
    return Counter(words).most_common(10), word_to_titles

# --- THE UI ---
st.title("🧬 Genre Fusion Engine")
st.markdown("Don't just copy trends. **Combine them.**")

if st.button("🚀 RUN DUAL SCAN", type="primary", use_container_width=True):
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("👻 Horror")
        with st.spinner("Scanning Nightmares..."):
            h_trends, h_context = get_trends_for_genre(['nosleep', 'shortscarystories', 'ruleshorror'])
            
            for rank, (word, count) in enumerate(h_trends[:5]):
                st.success(f"#{rank+1} {word.upper()}")
                with st.expander("See Titles"):
                    for t in h_context[word][:2]: st.caption(f"• {t}")

    with col2:
        st.header("💘 Drama")
        with st.spinner("Scanning Heartbreak..."):
            r_trends, r_context = get_trends_for_genre(['relationships', 'confessions', 'dating_advice'])
            
            for rank, (word, count) in enumerate(r_trends[:5]):
                st.error(f"#{rank+1} {word.upper()}")
                with st.expander("See Titles"):
                    for t in r_context[word][:2]: st.caption(f"• {t}")
                    
    st.divider()
    st.info("💡 **PRO TIP:** Take a word from the LEFT column and a word from the RIGHT column to make your title.")

else:
    st.write("Click above to start.")
