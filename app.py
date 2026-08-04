import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib

# --- Base directory (works locally AND on Streamlit Cloud) ---
BASE_DIR = pathlib.Path(__file__).parent

# --- Page Config ---
st.set_page_config(
    page_title="Multilac Competitor Analysis",
    page_icon="🎨",
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
    google    = pd.read_csv(BASE_DIR / "google_ratings.csv")
    keywords  = pd.read_csv(BASE_DIR / "keyword_ranking.csv")
    social    = pd.read_csv(BASE_DIR / "social_media.csv")
    backlinks = pd.read_csv(BASE_DIR / "backlinks_seo.csv")

    # Standardise brand names
    for df in [google, keywords, social, backlinks]:
        df["Brand"] = df["Brand"].str.strip()
        df["Brand"] = df["Brand"].replace({
            "Asian paints":  "Asian Paints",
            "Asian Paints ": "Asian Paints",
            "Multilac ":     "Multilac",
        })

    # Clean numeric columns
    for col in ["Followers", "No_of_Posts"]:
        social[col] = social[col].astype(str).str.replace(",", "").str.strip()
        social[col] = pd.to_numeric(social[col], errors="coerce")

    social["Avg_Likes"]   = pd.to_numeric(social["Avg_Likes"],   errors="coerce")
    social["July_Posts"]  = pd.to_numeric(social["July_Posts"],  errors="coerce")
    social["Post_Frequency"] = pd.to_numeric(social["Post_Frequency"], errors="coerce")

    backlinks["SEO_Performance"] = (
        backlinks["SEO_Performance"].astype(str).str.replace("%", "").str.strip()
    )
    backlinks["SEO_Performance"] = pd.to_numeric(backlinks["SEO_Performance"], errors="coerce")

    return google, keywords, social, backlinks

google, keywords, social, backlinks = load_data()

# --- Logo Map ---
LOGO_MAP = {
    "Multilac":      BASE_DIR / "logos/multilac_logo.jpg",
    "Nippon Paints": BASE_DIR / "logos/nipponpaints_logo.jpg",
    "DULUX":         BASE_DIR / "logos/dulux_logo.png",
    "Asian Paints":  BASE_DIR / "logos/asianpaints_causeway_logo.jpg",
    "JAT":           BASE_DIR / "logos/jatpaints_logo.png",
}

# --- Sidebar ---
ml_logo = LOGO_MAP["Multilac"]
if ml_logo.exists():
    st.sidebar.image(str(ml_logo), width=150)

st.sidebar.title("Multilac Dashboard")
st.sidebar.markdown("Competitor Analysis — Paint Industry Sri Lanka")
st.sidebar.divider()

page = st.sidebar.selectbox("Navigate", [
    "Home", "Keyword Rankings", "SEO & Backlinks", "Social Media", "Google Ratings"
])

brands = ["All"] + sorted(google["Brand"].unique().tolist())
selected_brand = st.sidebar.selectbox("Filter by Brand", brands)

if selected_brand != "All":
    lp = LOGO_MAP.get(selected_brand)
    if lp and lp.exists():
        st.sidebar.image(str(lp), width=120)

st.sidebar.divider()
st.sidebar.markdown("**Brands Analysed:**")
for b in ["Multilac", "Nippon Paints", "DULUX", "Asian Paints", "JAT"]:
    lp = LOGO_MAP.get(b)
    c1, c2 = st.sidebar.columns([1, 2])
    with c1:
        if lp and lp.exists():
            st.image(str(lp), width=35)
        else:
            st.markdown("🎨")
    with c2:
        st.markdown(f"**{b}** *(You)*" if b == "Multilac" else b)

# --- Filter helper ---
def filter_df(df):
    if selected_brand == "All":
        return df.copy()
    return df[df["Brand"] == selected_brand].copy()

google_filtered    = filter_df(google)
keywords_filtered  = filter_df(keywords)
social_filtered    = filter_df(social)
backlinks_filtered = filter_df(backlinks)

# =====================
# HOME PAGE
# =====================
if page == "Home":
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        if ml_logo.exists():
            st.image(str(ml_logo), width=120)
    with col_title:
        st.title("Multilac Competitor Analysis Dashboard")
        st.caption("Paint Industry — Sri Lanka | Digital Presence & SEO Analysis")
    st.divider()

    st.subheader("📊 Multilac at a Glance")
    ml_seo = backlinks[backlinks["Brand"] == "Multilac"].iloc[0]
    ml_g   = google[google["Brand"] == "Multilac"].iloc[0]
    ml_kw  = keywords[keywords["Brand"] == "Multilac"]
    ml_ig  = social[(social["Brand"] == "Multilac") & (social["Platform"] == "Instagram")].iloc[0]
    ml_fb  = social[(social["Brand"] == "Multilac") & (social["Platform"] == "Facebook")].iloc[0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SEO Score",           f"{int(ml_seo['SEO_Performance'])}%", "Highest among all")
    c2.metric("Backlinks",           f"{int(ml_seo['Backlinks'])}",        "2nd highest")
    c3.metric("Keywords Ranked",     f"{len(ml_kw)}",                      "incl. #1 lead safe")
    c4.metric("Google Rating",       f"⭐ {ml_g['Star_Rating']}",          f"{int(ml_g['Total_Reviews'])} reviews")
    c5.metric("Instagram Followers", f"{int(ml_ig['Followers']):,}")

    st.divider()

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strengths:</b> Multilac leads all competitors in SEO performance (73%)
    and has a strong backlink count (189). Multilac uniquely ranks #1 for
    "lead safe paint Sri Lanka" — a key differentiator no competitor holds.
    Instagram engagement (avg 20.94 likes/post) is the highest among comparable local brands.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="warning-box">
    ⚠️ <b>Areas to Improve:</b> Multilac is absent from 6 out of 10 category keywords.
    Nippon Paints ranks #1 on almost every major buying keyword.
    Facebook average likes (2.19) is significantly lower than competitors —
    content quality and boosting strategy on Facebook needs urgent attention.
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
# KEYWORD RANKINGS
# =====================
elif page == "Keyword Rankings":
    st.title("🔍 Keyword Rankings")
    st.caption("Google search keyword ranking positions by brand")
    st.divider()

    st.subheader("Number of Keywords Each Brand Ranks For")
    kw_count = keywords.groupby("Brand").size().reset_index(name="Keywords Ranked")
    fig1 = px.bar(
        kw_count.sort_values("Keywords Ranked", ascending=False),
        x="Brand", y="Keywords Ranked", color="Brand",
        title="Total Keywords Ranked per Brand",
        color_discrete_sequence=px.colors.qualitative.Set2,
        text="Keywords Ranked"
    )
    fig1.update_traces(textposition="outside")
    fig1.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> Nippon Paints and DULUX dominate keyword rankings.
    Multilac ranks for 4 keywords including the unique "lead safe paint Sri Lanka"
    at position #1 — a strong niche advantage worth promoting further.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Keyword Ranking Heatmap")
    st.caption("Lower number = better ranking position. Grey = not ranked.")
    pivot = keywords.pivot_table(index="Key word", columns="Brand", values="Rank", aggfunc="first")
    fig2 = px.imshow(
        pivot, text_auto=True,
        color_continuous_scale="RdYlGn_r",
        title="Keyword Ranking Heatmap (1 = Top Position)",
        aspect="auto"
    )
    fig2.update_layout(height=500, paper_bgcolor="white")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Insight:</b> Green cells = top positions. Multilac's green cell on
    "lead safe paint Sri Lanka" is its strongest digital asset with zero competition.
    White/grey = brand not ranked for that keyword.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Rankings by Keyword")
    selected_kw = st.selectbox("Select a keyword to inspect", sorted(keywords["Key word"].unique()))
    kw_data = keywords[keywords["Key word"] == selected_kw].sort_values("Rank")
    fig3 = px.bar(
        kw_data, x="Brand", y="Rank", color="Brand",
        title=f'Rankings for: "{selected_kw}"',
        text="Rank",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(autorange="reversed", title="Position (lower = better)")
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Full Keywords Data")
    st.dataframe(keywords_filtered, use_container_width=True)

# =====================
# SEO & BACKLINKS
# =====================
elif page == "SEO & Backlinks":
    st.title("🔗 SEO & Backlinks Analysis")
    st.caption("Backlink count and SEO performance scores by brand")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Backlinks by Brand")
        fig1 = px.bar(
            backlinks.sort_values("Backlinks", ascending=False),
            x="Brand", y="Backlinks", color="Brand",
            title="Number of Backlinks per Brand",
            text="Backlinks",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("SEO Performance Score")
        fig2 = px.bar(
            backlinks.sort_values("SEO_Performance", ascending=False),
            x="Brand", y="SEO_Performance", color="Brand",
            title="SEO Performance Score (%) by Brand",
            labels={"SEO_Performance": "SEO Score (%)"},
            text="SEO_Performance",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_traces(textposition="outside", texttemplate="%{text}%")
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strength:</b> Multilac leads in SEO performance with 73% —
    the highest among all competitors. JAT has the most backlinks (276) but
    a lower SEO score (53%), suggesting Multilac has better quality on-page optimisation.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Backlinks vs SEO Performance")
    fig3 = px.scatter(
        backlinks, x="Backlinks", y="SEO_Performance",
        color="Brand", size="Backlinks", hover_name="Brand",
        title="Backlinks vs SEO Performance Score",
        labels={"SEO_Performance": "SEO Score (%)"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=420)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Quadrant reading:</b> Ideal position is top-right (high backlinks + high SEO score).
    Multilac is top-left — strong SEO but fewer backlinks than JAT.
    Priority action: build more backlinks from local hardware, construction,
    and lifestyle sites to move toward the top-right quadrant.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("SEO & Backlinks Data")
    st.dataframe(backlinks_filtered, use_container_width=True)

# =====================
# SOCIAL MEDIA
# =====================
elif page == "Social Media":
    st.title("📱 Social Media Analysis")
    st.caption("Instagram and Facebook performance comparison")
    st.divider()

    platform = st.radio("Select Platform", ["Instagram", "Facebook"], horizontal=True)
    platform_data     = social[social["Platform"] == platform]
    platform_filtered = social_filtered[social_filtered["Platform"] == platform]

    if platform == "Instagram":
        st.caption("📅 Avg Likes based on last 20 posts | July Posts = posts published in July 2026")
    else:
        st.caption("📅 Avg Likes based on last 30 days | July Posts = posts published in July 2026")

    st.divider()

    # Row 1 — Followers and Avg Likes
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader(f"👥 {platform} Followers")
        fig1 = px.bar(
            platform_data.sort_values("Followers", ascending=False),
            x="Brand", y="Followers", color="Brand",
            title=f"{platform} Followers by Brand",
            text="Followers",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_traces(textposition="outside", texttemplate="%{text:,.0f}")
        fig1.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader(f"❤️{platform} Average Likes per Post")
        fig2 = px.bar(
            platform_data.sort_values("Avg_Likes", ascending=False),
            x="Brand", y="Avg_Likes", color="Brand",
            title=f"{platform} Average Likes per Post ({platform_data['Avg_Likes_Count'].iloc[0]})",
            text="Avg_Likes",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # Row 2 — July Posts and Total Posts
    col_left2, col_right2 = st.columns(2)
    with col_left2:
        st.subheader(f"📅 {platform} Posts in July 2026")
        fig3 = px.bar(
            platform_data.sort_values("July_Posts", ascending=False),
            x="Brand", y="July_Posts", color="Brand",
            title=f"{platform} Number of Posts — July 2026",
            labels={"July_Posts": "Posts in July 2026"},
            text="July_Posts",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig3.update_traces(textposition="outside")
        fig3.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    with col_right2:
        st.subheader(f"📊 {platform} Total Posts (All Time)")
        fig4 = px.bar(
            platform_data.sort_values("No_of_Posts", ascending=False),
            x="Brand", y="No_of_Posts", color="Brand",
            title=f"{platform} Total Posts Published",
            labels={"No_of_Posts": "Total Posts"},
            text="No_of_Posts",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig4.update_traces(textposition="outside", texttemplate="%{text:,.0f}")
        fig4.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # Row 3 — Posting Frequency
    st.subheader(f"🔄 {platform} Posting Frequency")
    fig5 = px.bar(
        platform_data.sort_values("Post_Frequency", ascending=False),
        x="Brand", y="Post_Frequency", color="Brand",
        title=f"{platform} Post Frequency (Posts per Day)",
        labels={"Post_Frequency": "Posts per Day"},
        text="Post_Frequency",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig5.update_traces(textposition="outside")
    fig5.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig5, use_container_width=True)

    # Posting frequency data table
    st.subheader("Posting Frequency")
    freq_data = platform_data[["Brand", "Post_Frequency", "Posting_Frequency"]].copy()
    freq_data.columns = ["Brand", "Posts per Day", "Description"]
    st.dataframe(freq_data, use_container_width=True, hide_index=True)

    st.divider()

    if platform == "Instagram":
        st.markdown("""
        <div class="insight-box">
        💡 <b>Instagram Insight:</b> JAT posts most frequently (every day) but has the lowest followers (133).
        Multilac posts every 2 days and has the highest average likes (20.94) among comparable local brands —
        strong content quality. Increasing to daily posting could significantly improve reach.
        Asian Paints only posted 2 times in July 2026 — a major drop in activity.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="insight-box">
        💡 <b>Facebook Insight:</b> DULUX's 6.7M followers is a global page — not directly comparable.
        Among local brands, Asian Paints (247K) leads followed by Nippon Paints (204K) and Multilac (127K).
        JAT has the highest average likes per post (450.6) on Facebook despite fewer followers —
        their content resonates strongly with their audience.
        Multilac's Facebook average likes (2.19) is critically low and needs immediate content improvement.
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Full Social Media Data")
    st.dataframe(platform_filtered, use_container_width=True)

# =====================
# GOOGLE RATINGS
# =====================
elif page == "Google Ratings":
    st.title("⭐ Google Map Ratings")
    st.caption("Star ratings and total review counts by brand")
    st.divider()

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Star Ratings by Brand")
        fig1 = px.bar(
            google.sort_values("Star_Rating", ascending=False),
            x="Brand", y="Star_Rating", color="Brand",
            title="Google Star Rating by Brand",
            labels={"Star_Rating": "Star Rating"},
            text="Star_Rating",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig1.update_traces(textposition="outside")
        fig1.update_layout(
            showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(range=[3.5, 5])
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Total Reviews by Brand")
        fig2 = px.bar(
            google.sort_values("Total_Reviews", ascending=False),
            x="Brand", y="Total_Reviews", color="Brand",
            title="Total Google Reviews by Brand",
            labels={"Total_Reviews": "Total Reviews"},
            text="Total_Reviews",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    st.subheader("Star Rating vs Total Reviews — Brand Trust Map")
    fig3 = px.scatter(
        google, x="Total_Reviews", y="Star_Rating",
        color="Brand", size="Total_Reviews", hover_name="Brand",
        title="Brand Trust Map — Rating vs Review Count",
        labels={"Star_Rating": "Star Rating", "Total_Reviews": "Total Reviews"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=420, yaxis=dict(range=[3.8, 4.7])
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""
    <div class="multilac-box">
    🟢 <b>Multilac Strength:</b> Multilac has the second highest review count (174)
    behind Nippon Paints (247) — showing strong customer engagement.
    Actively encouraging customers to leave Google reviews could push Multilac
    to #1 in review volume, strengthening trust signals for new buyers.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-box">
    💡 <b>Opportunity:</b> JAT leads in star rating (4.4) despite only 55 reviews.
    DULUX has a good rating (4.3) but only 39 reviews — very low visibility.
    Multilac's combination of solid rating (4.2) AND high review count (174)
    is a strong trust position that should be highlighted in all marketing materials.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Google Ratings Data")
    st.dataframe(google_filtered, use_container_width=True)