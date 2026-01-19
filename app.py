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
        'dating', 'relationship', 'confession', 'reddit', 'people', 'know', 'want', 'time', 'would',
        'really', 'because', 'friend', 'friends', 'girl', 'boy', 'year', 'years', 'been',
        'book', 'books', 'read', 'reading', 'series', 'recommendation', 'author' # Filter out book talk
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
st.title("🧬 Genre Fusion Engine")
st.markdown("Left: **Horror** | Right: **Romance + Fantasy**")

if st.button("🚀 RUN DUAL SCAN", type="primary", use_container_width=True):
    
    col1, col2 = st.columns(2)
    
    # --- LEFT COLUMN (HORROR) ---
    with col1:
        st.header("👻 Horror")
        with st.spinner("Scanning Nightmares..."):
            h_trends, h_context, h_total = get_trends_for_genre(['nosleep', 'shortscarystories', 'ruleshorror'])
            
            for rank, (word, count) in enumerate(h_trends[:5]):
                saturation = (count / h_total) * 100
                st.success(f"#{rank+1} {word.upper()}")
                st.caption(f"📊 **{saturation:.1f}%** ({count} Hits)")
                
                with st.expander("Examples"):
                    for t in h_context[word][:3]: st.write(f"• {t}")

    
    # --- RIGHT COLUMN (ROMANCE + FANTASY + WEB NOVEL) ---
    with col2:
        st.header("🧚‍♀️ Romantasy & Isekai")
        with st.spinner("Scanning for Alphas, Villainesses, and Magic..."):
            
            # UPDATED: Added specific 'Viral Fantasy' subreddits
            r_trends, r_context, r_total = get_trends_for_genre([
                'relationships', 'dating_advice', # Real Drama
                'FantasyRomance', 'ParanormalRomance', # Vampire/Wolf/Fae
                'OtomeIsekai', 'Isekai' # Villainess/Reborn/System trends
            ])
            
            for rank, (word, count) in enumerate(r_trends[:5]):
                saturation = (count / r_total) * 100
                st.error(f"#{rank+1} {word.upper()}")
                st.caption(f"📊 **{saturation:.1f}%** ({count} Hits)")
                
                with st.expander("Examples"):
                    for t in r_context[word][:3]: st.write(f"• {t}")

                    
    st.divider()
    st.info(f"💡 **DATA DEPTH:** Analyzed {h_total + r_total} stories.")

else:
    st.write("Click above to start.")
