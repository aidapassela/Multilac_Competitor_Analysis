import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Config ---
st.set_page_config(
    page_title="Multilac Competitor Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    [data-testid="stSidebar"] * { color: white !important; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { background-color: #2d2d44 !important; }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * { color: white !important; }
    [data-testid="stSidebar"] input { color: white !important; background-color: #2d2d44 !important; }
    [data-testid="stSidebar"] .stRadio * { color: white !important; }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.07);
    }
    h1 { color: #c0392b; }
    h2, h3 { color: #1a1a2e; }
    .insight-box {
        background-color: #fff8e1;
        border-left: 4px solid #FFC107;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #333333;
    }
    .multilac-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4CAF50;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #333333;
    }
    .warning-box {
        background-color: #fdecea;
        border-left: 4px solid #e74c3c;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #333333;
    }
    </style>
""", unsafe_allow_html=True)

# --- Load Data ---
@st.cache_data
def load_data():
    google = pd.read_csv("google_ratings.csv")
    keywords = pd.read_csv("keyword_ranking.csv")
    social = pd.read_csv("social_media.csv")
    backlinks = pd.read_csv("backlinks_seo.csv")

    keywords["Brand"] = keywords["Brand"].str.replace("Asian paints", "Asian Paints", case=True)
    keywords["Brand"] = keywords["Brand"].str.strip()
    google["Brand"] = google["Brand"].str.strip()
    social["Brand"] = social["Brand"].str.strip()
    backlinks["Brand"] = backlinks["Brand"].str.strip()

    social["Followers"] = social["Followers"].astype(str).str.replace(",", "").str.strip()
    social["Followers"] = pd.to_numeric(social["Followers"], errors="coerce")

    social["No_of_Posts"] = social["No_of_Posts"].astype(str).str.replace(",", "").str.strip()
    social["No_of_Posts"] = pd.to_numeric(social["No_of_Posts"], errors="coerce")

    social["July_Posts"] = pd.to_numeric(social["July_Posts"], errors="coerce")
    social["Avg_Likes"] = pd.to_numeric(social["Avg_Likes"], errors="coerce")

    backlinks["SEO_Performance"] = backlinks["SEO_Performance"].astype(str).str.replace("%", "").str.strip()
    backlinks["SEO_Performance"] = pd.to_numeric(backlinks["SEO_Performance"], errors="coerce")

    return google, keywords, social, backlinks

google, keywords, social, backlinks = load_data()

# --- Logo Map ---
logo_map = {
    "Multilac": r"G:\My Drive\Multilac\competitor_analysis\logos\multilac_logo.jpg",
    "Nippon Paints": r"G:\My Drive\Multilac\competitor_analysis\logos\nipponpaints_logo.jpg",
    "DULUX": r"G:\My Drive\Multilac\competitor_analysis\logos\dulux_logo.png",
    "Asian Paints": r"G:\My Drive\Multilac\competitor_analysis\logos\asianpaints_causeway_logo.jpg",
    "JAT": r"G:\My Drive\Multilac\competitor_analysis\logos\jatpaints_logo.png"
}

multilac_logo_path = r"G:\My Drive\Multilac\competitor_analysis\logos\multilac_logo.jpg"

# --- Sidebar ---
if os.path.exists(multilac_logo_path):
    st.sidebar.image(multilac_logo_path, width=150)

st.sidebar.title("Multilac Dashboard")
st.sidebar.markdown("Competitor Analysis — Paint Industry Sri Lanka")
st.sidebar.divider()

page = st.sidebar.selectbox("Navigate", [
    "Home", "Keyword Rankings", "SEO & Backlinks", "Social Media", "Google Ratings"
])

brands = ["All"] + sorted(google["Brand"].unique().tolist())
selected_brand = st.sidebar.selectbox("Filter by Brand", brands)

if selected_brand != "All":
    logo_path = logo_map.get(selected_brand, "")
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=120)

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
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if os.path.exists(multilac_logo_path):
            st.image(multilac_logo_path, width=120)
    with col_title:
        st.title("Multilac Competitor Analysis Dashboard")
        st.caption("Paint Industry — Sri Lanka | Digital Presence & SEO Analysis")
    st.divider()

    st.subheader("📊 Multilac at a Glance")
    multilac_seo = backlinks[backlinks["Brand"] == "Multilac"]
    multilac_google = google[google["Brand"] == "Multilac"]
    multilac_kw = keywords[keywords["Brand"] == "Multilac"]
    multilac_ig = social[(social["Brand"] == "Multilac") & (social["Platform"] == "Instagram")]

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("SEO Score", f"{multilac_seo['SEO_Performance'].values[0]}%", "🏆 Highest")
    col2.metric("Backlinks", f"{multilac_seo['Backlinks'].values[0]}", "2nd highest")
    col3.metric("Keywords Ranked", f"{len(multilac_kw)}", "keywords")
    col4.metric("Google Rating", f"⭐ {multilac_google['Star_Rating'].values[0]}", f"{multilac_google['Total_Reviews'].values[0]} reviews")
    col5.metric("Instagram Followers", f"{multilac_ig['Followers'].values[0]:,.0f}")

    st.divider()

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strengths:</b> Multilac leads all competitors in SEO performance (73%)
    and has a strong backlink count (189). Multilac uniquely ranks #1 for
    "lead safe paint Sri Lanka" — a key differentiator in the market.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
    ⚠️ <b>Areas to Improve:</b> Multilac only ranks for 4 keywords compared to Nippon Paints
    and DULUX who dominate most search terms. Social media following is also lower than
    key competitors on Facebook.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📋 SEO & Backlinks Overview")
        st.dataframe(backlinks_filtered, use_container_width=True)
        st.subheader("📋 Google Ratings Overview")
        st.dataframe(google_filtered, use_container_width=True)
    with col_right:
        st.subheader("📋 Social Media Overview")
        st.dataframe(social_filtered, use_container_width=True)
        st.subheader("📋 Keyword Rankings Overview")
        st.dataframe(keywords_filtered, use_container_width=True)

# =====================
# KEYWORD RANKINGS PAGE
# =====================
elif page == "Keyword Rankings":
    st.title("🔍 Keyword Rankings")
    st.caption("Google search keyword ranking positions by brand")
    st.divider()

    st.subheader("🏆 Number of Keywords Each Brand Ranks For")
    kw_count = keywords.groupby("Brand").size().reset_index(name="Keywords Ranked")
    fig1 = px.bar(
        kw_count.sort_values("Keywords Ranked", ascending=False),
        x="Brand", y="Keywords Ranked",
        color="Brand",
        title="Total Keywords Ranked per Brand",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> Nippon Paints and DULUX dominate keyword rankings.
    Multilac ranks for 4 keywords including the unique "lead safe paint Sri Lanka"
    at position #1 — a strong niche advantage worth promoting further.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("📊 Keyword Ranking Heatmap")
    st.caption("Lower number = better ranking position. Grey = not ranked.")
    pivot = keywords.pivot_table(
        index="Key word", columns="Brand", values="Rank", aggfunc="first"
    )
    fig2 = px.imshow(
        pivot, text_auto=True,
        color_continuous_scale="RdYlGn_r",
        title="Keyword Ranking Heatmap (1 = Top Position)",
        aspect="auto"
    )
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> Green cells indicate top positions. Multilac appears in green
    for "lead safe paint Sri Lanka" and ranks in several other key terms.
    White/grey cells mean the brand does not appear for that keyword.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Keyword Rankings Data")
    st.dataframe(keywords_filtered, use_container_width=True)

# =====================
# SEO & BACKLINKS PAGE
# =====================
elif page == "SEO & Backlinks":
    st.title("🔗 SEO & Backlinks Analysis")
    st.caption("Backlink count and SEO performance scores by brand")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🔗 Backlinks by Brand")
        fig1 = px.bar(
            backlinks.sort_values("Backlinks", ascending=False),
            x="Brand", y="Backlinks", color="Brand",
            title="Number of Backlinks per Brand",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("📈 SEO Performance Score")
        fig2 = px.bar(
            backlinks.sort_values("SEO_Performance", ascending=False),
            x="Brand", y="SEO_Performance", color="Brand",
            title="SEO Performance Score (%) by Brand",
            labels={"SEO_Performance": "SEO Score (%)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strength:</b> Multilac leads in SEO performance with 73% —
    the highest among all competitors. This means Multilac's website is
    well optimised for search engines despite having fewer keywords ranked.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("🔵 Backlinks vs SEO Performance")
    fig3 = px.scatter(
        backlinks, x="Backlinks", y="SEO_Performance",
        color="Brand", size="Backlinks", hover_name="Brand",
        title="Backlinks vs SEO Performance Score",
        labels={"SEO_Performance": "SEO Score (%)"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> JAT has the most backlinks (276) but a lower SEO score (53%)
    compared to Multilac. This suggests Multilac has better quality backlinks
    and stronger on-page SEO optimisation.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 SEO & Backlinks Data")
    st.dataframe(backlinks_filtered, use_container_width=True)

# =====================
# SOCIAL MEDIA PAGE
# =====================
elif page == "Social Media":
    st.title("📱 Social Media Analysis")
    st.caption("Instagram and Facebook performance comparison")
    st.divider()

    platform = st.radio("Select Platform", ["Instagram", "Facebook"], horizontal=True)
    platform_data = social[social["Platform"] == platform]
    platform_filtered = social_filtered[social_filtered["Platform"] == platform]

    # Time period note
    if platform == "Instagram":
        st.caption("📅 Average Likes based on last 20 posts | July 2026 Posts based on July 2026 data")
    else:
        st.caption("📅 Average Likes based on last 30 days | July 2026 Posts based on July 2026 data")

    st.divider()

    # Row 1 — Followers and Average Likes
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader(f"👥 {platform} Followers")
        fig1 = px.bar(
            platform_data.sort_values("Followers", ascending=False),
            x="Brand", y="Followers", color="Brand",
            title=f"{platform} Followers by Brand",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader(f"❤️ {platform} Average Likes")
        fig2 = px.bar(
            platform_data.sort_values("Avg_Likes", ascending=False),
            x="Brand", y="Avg_Likes", color="Brand",
            title=f"{platform} Average Likes per Post",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Row 2 — Posting Frequency and July Posts
    col_left2, col_right2 = st.columns(2)
    with col_left2:
        st.subheader(f"📅 {platform} July 2026 Posts")
        fig3 = px.bar(
            platform_data.sort_values("July_Posts", ascending=False),
            x="Brand", y="July_Posts", color="Brand",
            title=f"{platform} Number of Posts in July 2026",
            labels={"July_Posts": "Posts in July 2026"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_right2:
        st.subheader(f"📊 {platform} Total Posts")
        fig4 = px.bar(
            platform_data.sort_values("No_of_Posts", ascending=False),
            x="Brand", y="No_of_Posts", color="Brand",
            title=f"{platform} Total Number of Posts (All Time)",
            labels={"No_of_Posts": "Total Posts"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # Posting Frequency plain English
    st.subheader(f"🗓️ {platform} Posting Frequency")
    freq_data = platform_data[["Brand", "Post_Frequency", "Posting_Frequency"]].copy()
    freq_data.columns = ["Brand", "Posts per Day", "Frequency Description"]
    st.dataframe(freq_data, use_container_width=True)

    st.divider()

    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> JAT posts most frequently on Instagram (every day).
    DULUX dominates Facebook with 6.7M followers and posts daily.
    Multilac posts every 2 days on Instagram — increasing to daily posting
    could significantly improve reach and engagement.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Full Social Media Data")
    st.dataframe(platform_filtered, use_container_width=True)

# =====================
# GOOGLE RATINGS PAGE
# =====================
elif page == "Google Ratings":
    st.title("⭐ Google Map Ratings")
    st.caption("Star ratings and total review counts by brand")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("⭐ Star Ratings by Brand")
        fig1 = px.bar(
            google.sort_values("Star_Rating", ascending=False),
            x="Brand", y="Star_Rating", color="Brand",
            title="Google Star Rating by Brand",
            labels={"Star_Rating": "Star Rating"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_layout(yaxis=dict(range=[3.5, 5]))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("📝 Total Reviews by Brand")
        fig2 = px.bar(
            google.sort_values("Total_Reviews", ascending=False),
            x="Brand", y="Total_Reviews", color="Brand",
            title="Total Google Reviews by Brand",
            labels={"Total_Reviews": "Total Reviews"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.subheader("🔵 Star Rating vs Total Reviews")
    fig3 = px.scatter(
        google, x="Total_Reviews", y="Star_Rating",
        color="Brand", size="Total_Reviews", hover_name="Brand",
        title="Star Rating vs Total Reviews",
        labels={"Star_Rating": "Star Rating", "Total_Reviews": "Total Reviews"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strength:</b> Multilac has the second highest number of
    Google reviews (174) showing strong customer engagement.
    Encouraging more customers to leave reviews could further
    strengthen Multilac's online reputation.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 Google Ratings Data")
    st.dataframe(google_filtered, use_container_width=True)