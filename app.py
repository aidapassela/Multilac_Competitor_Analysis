import streamlit as st
import pandas as pd
import plotly.express as px

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

    # Fix brand name inconsistencies
    keywords["Brand"] = keywords["Brand"].str.replace("Asian paints", "Asian Paints", case=True)
    keywords["Brand"] = keywords["Brand"].str.strip()
    google["Brand"] = google["Brand"].str.strip()
    social["Brand"] = social["Brand"].str.strip()
    backlinks["Brand"] = backlinks["Brand"].str.strip()

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

page = st.sidebar.selectbox("📄 Navigate", [
    "Home", "Keyword Rankings", "SEO & Backlinks", "Social Media", "Google Ratings"
])

brands = ["All"] + sorted(google["Brand"].unique().tolist())
selected_brand = st.sidebar.selectbox("🏢 Filter by Brand", brands)

st.sidebar.divider()
st.sidebar.markdown("**Brands Analysed:**")
for b in google["Brand"].unique():
    if b == "Multilac":
        st.sidebar.markdown(f"🟢 **{b}** *(You)*")
    else:
        st.sidebar.markdown(f"🔵 {b}")

# --- Filter ---
if selected_brand == "All":
    google_filtered = google.copy()
    keywords_filtered = keywords.copy()
    social_filtered = social.copy()
    backlinks_filtered = backlinks.copy()
else:
    selected_brand_clean = selected_brand.strip()
    google_filtered = google[google["Brand"].str.strip() == selected_brand_clean]
    keywords_filtered = keywords[keywords["Brand"].str.strip() == selected_brand_clean]
    social_filtered = social[social["Brand"].str.strip() == selected_brand_clean]
    backlinks_filtered = backlinks[backlinks["Brand"].str.strip() == selected_brand_clean]

# =====================
# HOME PAGE
# =====================
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

# =====================
# KEYWORD RANKINGS PAGE
# =====================
elif page == "Keyword Rankings":
    st.title("🔍 Keyword Rankings")
    st.caption("Google search keyword ranking positions by brand")
    st.divider()

    # Chart 1 — Number of keywords each brand ranks for
    st.subheader("🏆 Number of Keywords Each Brand Ranks For")
    kw_count = keywords.groupby("Brand").size().reset_index(name="Keywords Ranked")
    fig1 = px.bar(
        kw_count.sort_values("Keywords Ranked", ascending=False),
        x="Brand",
        y="Keywords Ranked",
        color="Brand",
        title="Total Keywords Ranked per Brand",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # Chart 2 — Heatmap
    st.subheader("📊 Keyword Ranking Heatmap")
    st.caption("Lower number = better ranking position")
    pivot = keywords.pivot_table(
        index="Key word",
        columns="Brand",
        values="Rank",
        aggfunc="first"
    )
    fig2 = px.imshow(
        pivot,
        text_auto=True,
        color_continuous_scale="RdYlGn_r",
        title="Keyword Ranking Heatmap (1 = Top Position)",
        aspect="auto"
    )
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Raw table
    st.subheader("📋 Keyword Rankings Data")
    st.dataframe(keywords_filtered, use_container_width=True)

# =====================
# SEO & BACKLINKS PAGE
# =====================
elif page == "SEO & Backlinks":
    st.title("🔗 SEO & Backlinks Analysis")
    st.caption("Backlink count and SEO performance scores by brand")
    st.divider()
    st.dataframe(backlinks_filtered, use_container_width=True)

# =====================
# SOCIAL MEDIA PAGE
# =====================
elif page == "Social Media":
    st.title("📱 Social Media Analysis")
    st.caption("Instagram and Facebook performance comparison")
    st.divider()
    st.dataframe(social_filtered, use_container_width=True)

# =====================
# GOOGLE RATINGS PAGE
# =====================
elif page == "Google Ratings":
    st.title("⭐ Google Map Ratings")
    st.caption("Star ratings and total review counts by brand")
    st.divider()
    st.dataframe(google_filtered, use_container_width=True)
