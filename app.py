import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Multilac Competitor Analysis",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data ---
@st.cache_data
def load_data():
    google = pd.read_csv("google_ratings.csv")
    keywords = pd.read_csv("keyword_ranking.csv")
    social = pd.read_csv("social_media.csv")
    backlinks = pd.read_csv("backlinks_seo.csv")

    # Clean followers column
    social["Followers"] = social["Followers"].astype(str).str.replace(",", "").str.strip()
    social["Followers"] = pd.to_numeric(social["Followers"], errors="coerce")

    # Clean SEO column
    backlinks["SEO_Performance"] = backlinks["SEO_Performance"].astype(str).str.replace("%", "").str.strip()
    backlinks["SEO_Performance"] = pd.to_numeric(backlinks["SEO_Performance"], errors="coerce")

    return google, keywords, social, backlinks

google, keywords, social, backlinks = load_data()

# --- Sidebar ---
st.sidebar.title("🎨 Multilac Dashboard")
st.sidebar.markdown("Competitor Analysis — Paint Industry Sri Lanka")
st.sidebar.divider()

# Page navigation
page = st.sidebar.selectbox("📄 Navigate", [
    "Home",
    "Keyword Rankings",
    "SEO & Backlinks",
    "Social Media",
    "Google Ratings"
])

# Brand filter
brands = ["All"] + sorted(google["Brand"].unique().tolist())
selected_brand = st.sidebar.selectbox("🏢 Filter by Brand", brands)

st.sidebar.divider()
st.sidebar.markdown("**Brands Analysed:**")
for b in google["Brand"].unique():
    if b == "Multilac":
        st.sidebar.markdown(f"🟢 **{b}** *(You)*")
    else:
        st.sidebar.markdown(f"🔵 {b}")

# --- Filter data based on brand ---
if selected_brand == "All":
    google_filtered = google.copy()
    keywords_filtered = keywords.copy()
    social_filtered = social.copy()
    backlinks_filtered = backlinks.copy()
else:
    google_filtered = google[google["Brand"] == selected_brand]
    keywords_filtered = keywords[keywords["Brand"] == selected_brand]
    social_filtered = social[social["Brand"] == selected_brand]
    backlinks_filtered = backlinks[backlinks["Brand"] == selected_brand]

# --- Pages ---
if page == "Home":
    st.title("🎨 Multilac Competitor Analysis Dashboard")
    st.caption("Paint Industry — Sri Lanka | Digital Presence & SEO Analysis")
    st.divider()

    st.subheader("📋 Google Ratings")
    st.dataframe(google_filtered, use_container_width=True)

    st.subheader("📋 Keyword Rankings")
    st.dataframe(keywords_filtered, use_container_width=True)

    st.subheader("📋 SEO & Backlinks")
    st.dataframe(backlinks_filtered, use_container_width=True)

    st.subheader("📋 Social Media")
    st.dataframe(social_filtered, use_container_width=True)

elif page == "Keyword Rankings":
    st.title("🔍 Keyword Rankings")
    st.caption("Google search keyword ranking positions by brand")
    st.divider()
    st.dataframe(keywords_filtered, use_container_width=True)

elif page == "SEO & Backlinks":
    st.title("🔗 SEO & Backlinks Analysis")
    st.caption("Backlink count and SEO performance scores by brand")
    st.divider()
    st.dataframe(backlinks_filtered, use_container_width=True)

elif page == "Social Media":
    st.title("📱 Social Media Analysis")
    st.caption("Instagram and Facebook performance comparison")
    st.divider()
    st.dataframe(social_filtered, use_container_width=True)

elif page == "Google Ratings":
    st.title("⭐ Google Map Ratings")
    st.caption("Star ratings and total review counts by brand")
    st.divider()
    st.dataframe(google_filtered, use_container_width=True)
    