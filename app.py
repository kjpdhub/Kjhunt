import streamlit as st
import feedparser
from collections import Counter
import string

# --- PAGE CONFIG ---
st.set_page_config(page_title="Trend Hunter Trinity", page_icon="🔻", layout="wide")

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
    # Tuned Stop Words to filter noise from all 3 genres
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
    
    return Counter(words).most_common(10), word_to_titles, len(all_titles)

# --- THE UI ---
st.title("🔻 The Viral Trinity")
st.markdown("Combine elements from **Horror**, **Romance**, and **Mystery**.")

if st.button("🚀 RUN TRI-SCAN", type="primary", use_container_width=True):
    
    col1, col2, col3 = st.columns(3)
    
    # --- COL 1: HORROR ---
    with col1:
        st.header("👻 Horror")
        with st.spinner("Scanning..."):
            trends, context, total = get_trends_for_genre(['nosleep', 'shortscarystories', 'ruleshorror'])
            for rank, (word, count) in enumerate(trends[:5]):
                sat = (count / total) * 100
                st.success(f"{word.upper()}")
                st.caption(f"📊 {sat:.1f}%")
                with st.expander("Context"):
                    for t in context[word][:2]: st.write(f"• {t}")

    # --- COL 2: ROMANTASY ---
    with col2:
        st.header("🧚‍♀️ Romantasy")
        with st.spinner("Scanning..."):
            trends, context, total = get_trends_for_genre([
                'relationships', 'dating_advice', 
                'FantasyRomance', 'ParanormalRomance', 'OtomeIsekai'
            ])
            for rank, (word, count) in enumerate(trends[:5]):
                sat = (count / total) * 100
                st.error(f"{word.upper()}")
                st.caption(f"📊 {sat:.1f}%")
                with st.expander("Context"):
                    for t in context[word][:2]: st.write(f"• {t}")

    # --- COL 3: MYSTERY & CRIME ---
    with col3:
        st.header("🕵️ Mystery")
        with st.spinner("Scanning..."):
            # ADDED: True Crime, Unsolved Mysteries, RBI (Investigations)
            trends, context, total = get_trends_for_genre([
                'UnresolvedMysteries', 'TrueCrimeDiscussion', 
                'TrueCrime', 'RBI', 'ColdCases'
            ])
            for rank, (word, count) in enumerate(trends[:5]):
                sat = (count / total) * 100
                st.info(f"{word.upper()}")
                st.caption(f"📊 {sat:.1f}%")
                with st.expander("Context"):
                    for t in context[word][:2]: st.write(f"• {t}")

    st.divider()
    st.markdown("### 🧬 How to Mix:")
    st.markdown("*Take one keyword from each column to build your plot.*")
    st.markdown("**Example:** *[Horror: BASEMENT] + [Romance: HUSBAND] + [Mystery: DISAPPEARANCE]*")

else:
    st.write("Tap above to scan the markets.")
