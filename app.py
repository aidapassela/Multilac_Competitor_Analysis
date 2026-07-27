import streamlit as st
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Multilac Competitor Analysis",
    page_icon="🎨",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    google = pd.read_csv("google_ratings.csv")
    keywords = pd.read_csv("keyword_ranking.csv")
    social = pd.read_csv("social_media.csv")
    backlinks = pd.read_csv("backlinks_seo.csv")
    return google, keywords, social, backlinks

google, keywords, social, backlinks = load_data()

# --- Title ---
st.title("🎨 Multilac Competitor Analysis Dashboard")
st.caption("Paint Industry — Sri Lanka")
st.divider()

# --- Show Tables ---
st.subheader("📋 Google Ratings Data")
st.dataframe(google, use_container_width=True)

st.subheader("📋 Keyword Rankings Data")
st.dataframe(keywords, use_container_width=True)

st.subheader("📋 SEO & Backlinks Data")
st.dataframe(backlinks, use_container_width=True)

st.subheader("📋 Social Media Data")
st.dataframe(social, use_container_width=True)