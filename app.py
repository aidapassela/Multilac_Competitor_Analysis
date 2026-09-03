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

    social["Avg_Likes"]     = pd.to_numeric(social["Avg_Likes"],     errors="coerce")
    social["August_Posts"]  = pd.to_numeric(social["August_Posts"],  errors="coerce")
    social["Post_Frequency"] = pd.to_numeric(social["Post_Frequency"], errors="coerce")

    backlinks["SEO_Performance"] = (
        backlinks["SEO_Performance"].astype(str).str.replace("%", "").str.strip()
    )
    backlinks["SEO_Performance"] = pd.to_numeric(backlinks["SEO_Performance"], errors="coerce")

    return google, keywords, social, backlinks

google, keywords, social, backlinks = load_data()

# --- Dynamic insight helpers ---------------------------------------------
# These replace hand-typed numbers in the insight boxes below, so the
# narrative text stays correct automatically whenever the CSVs are refreshed.

def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def rank_of(df: pd.DataFrame, col: str, brand: str, ascending: bool = False):
    """Returns (1-indexed rank of `brand` on `col`, the fully sorted df)."""
    sorted_df = df.sort_values(col, ascending=ascending).reset_index(drop=True)
    rank = int(sorted_df.index[sorted_df["Brand"] == brand][0]) + 1
    return rank, sorted_df

MULTILAC = "Multilac"
FOLLOWER_OUTLIER_THRESHOLD = 1_000_000  # e.g. DULUX's global FB page

def compute_insights(google, keywords, social, backlinks):
    ins = {}
    ins["n_brands"] = backlinks["Brand"].nunique()

    # --- SEO ---
    ins["seo_ml_rank"], seo_sorted = rank_of(backlinks, "SEO_Performance", MULTILAC)
    ins["seo_leader"] = seo_sorted.iloc[0]
    ins["seo_ml_value"] = backlinks.loc[backlinks["Brand"] == MULTILAC, "SEO_Performance"].iloc[0]

    # --- Backlinks ---
    ins["bl_ml_rank"], bl_sorted = rank_of(backlinks, "Backlinks", MULTILAC)
    ins["bl_leader"] = bl_sorted.iloc[0]
    ins["bl_ml_value"] = backlinks.loc[backlinks["Brand"] == MULTILAC, "Backlinks"].iloc[0]

    # --- Keywords ---
    ins["total_kw"] = keywords["Key word"].nunique()
    ml_kw = keywords[keywords["Brand"] == MULTILAC]
    ins["ml_kw_count"] = len(ml_kw)
    ins["ml_kw_missing"] = ins["total_kw"] - ins["ml_kw_count"]
    ins["ml_kw_number1"] = ml_kw[ml_kw["Rank"] == 1]["Key word"].tolist()
    kw_counts = keywords.groupby("Brand").size().sort_values(ascending=False)
    ins["kw_leader_brand"] = kw_counts.index[0]
    ins["kw_leader_count"] = int(kw_counts.iloc[0])

    # --- Instagram ---
    ig = social[social["Platform"] == "Instagram"]
    ins["ig_n"] = len(ig)
    ins["ig_ml_rank"], ig_sorted = rank_of(ig, "Avg_Likes", MULTILAC)
    ins["ig_leader"] = ig_sorted.iloc[0]
    ins["ig_ml_value"] = ig.loc[ig["Brand"] == MULTILAC, "Avg_Likes"].iloc[0]
    ins["ig_lowest_followers"] = ig.sort_values("Followers").iloc[0]
    ins["ig_most_frequent"] = ig.sort_values("Post_Frequency", ascending=False).iloc[0]
    ins["ig_least_active_month"] = ig.sort_values("August_Posts").iloc[0]

    # --- Facebook (exclude global/outlier pages from local follower comparisons) ---
    fb = social[social["Platform"] == "Facebook"]
    ins["fb_n"] = len(fb)
    fb_local = fb[fb["Followers"] <= FOLLOWER_OUTLIER_THRESHOLD]
    fb_global = fb[fb["Followers"] > FOLLOWER_OUTLIER_THRESHOLD]
    ins["fb_global"] = fb_global
    ins["fb_local_followers_sorted"] = fb_local.sort_values("Followers", ascending=False)
    ins["fb_ml_rank"], fb_sorted = rank_of(fb, "Avg_Likes", MULTILAC)
    ins["fb_leader"] = fb_sorted.iloc[0]
    ins["fb_ml_value"] = fb.loc[fb["Brand"] == MULTILAC, "Avg_Likes"].iloc[0]
    ins["fb_sorted"] = fb_sorted

    # --- Google Ratings ---
    ins["rev_ml_rank"], rev_sorted = rank_of(google, "Total_Reviews", MULTILAC)
    ins["rev_leader"] = rev_sorted.iloc[0]
    ins["rev_ml_value"] = int(google.loc[google["Brand"] == MULTILAC, "Total_Reviews"].iloc[0])
    star_sorted = google.sort_values("Star_Rating", ascending=False)
    top_star_value = star_sorted.iloc[0]["Star_Rating"]
    top_star_brands = star_sorted[star_sorted["Star_Rating"] == top_star_value]
    ins["top_star_value"] = top_star_value
    ins["top_star_brands"] = top_star_brands
    ins["low_visibility_high_rating"] = top_star_brands.sort_values("Total_Reviews").iloc[0]
    ins["ml_star"] = google.loc[google["Brand"] == MULTILAC, "Star_Rating"].iloc[0]

    return ins

INSIGHTS = compute_insights(google, keywords, social, backlinks)

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

    ins = INSIGHTS

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("SEO Score",           f"{int(ml_seo['SEO_Performance'])}%",
              f"{ordinal(ins['seo_ml_rank'])} of {ins['n_brands']}")
    c2.metric("Backlinks",           f"{int(ml_seo['Backlinks'])}",
              f"{ordinal(ins['bl_ml_rank'])} of {ins['n_brands']}")
    c3.metric("Keywords Ranked",     f"{len(ml_kw)}",
              f"of {ins['total_kw']} tracked")
    c4.metric("Google Rating",       f"⭐ {ml_g['Star_Rating']}",          f"{int(ml_g['Total_Reviews'])} reviews")
    c5.metric("Instagram Followers", f"{int(ml_ig['Followers']):,}")

    st.divider()

    # Build strength / improvement bullets dynamically from where Multilac ranks
    metrics = [
        ("SEO performance", ins["seo_ml_rank"], ins["n_brands"],
         f"{int(ins['seo_ml_value'])}% — {ins['seo_leader']['Brand']} leads at {int(ins['seo_leader']['SEO_Performance'])}%"),
        ("Backlink count", ins["bl_ml_rank"], ins["n_brands"],
         f"{int(ins['bl_ml_value'])} backlinks — {ins['bl_leader']['Brand']} leads with {int(ins['bl_leader']['Backlinks'])}"),
        ("Instagram engagement", ins["ig_ml_rank"], ins["ig_n"],
         f"{ins['ig_ml_value']:.2f} avg likes/post — {ins['ig_leader']['Brand']} leads at {ins['ig_leader']['Avg_Likes']:.2f}"),
        ("Facebook engagement", ins["fb_ml_rank"], ins["fb_n"],
         f"{ins['fb_ml_value']:.2f} avg likes/post — {ins['fb_leader']['Brand']} leads at {ins['fb_leader']['Avg_Likes']:.2f}"),
        ("Google review volume", ins["rev_ml_rank"], ins["n_brands"],
         f"{ins['rev_ml_value']} reviews — {ins['rev_leader']['Brand']} leads with {int(ins['rev_leader']['Total_Reviews'])}"),
    ]
    strengths   = [m for m in metrics if m[1] <= 2]
    weaknesses  = [m for m in metrics if m[1] > 2]

    strength_lines = "<br>".join(
        f"• <b>{name}</b>: {ordinal(rank)} of {total} — {detail}" for name, rank, total, detail in strengths
    )
    weakness_lines = "<br>".join(
        f"• <b>{name}</b>: {ordinal(rank)} of {total} — {detail}" for name, rank, total, detail in weaknesses
    )
    lead_safe_note = (
        f' Multilac also uniquely ranks #1 for "{ins["ml_kw_number1"][0]}" — a key differentiator no competitor holds.'
        if ins["ml_kw_number1"] else ""
    )

    st.markdown(f"""
    <div class="multilac-box">
    🟢 <b>Multilac Strengths</b> (top-2 of {ins['n_brands']} on these metrics):<br>
    {strength_lines if strength_lines else "None of the tracked metrics currently rank Multilac in the top 2 — see improvement areas below."}
    {lead_safe_note}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="warning-box">
    ⚠️ <b>Areas to Improve:</b> Multilac is absent from {ins['ml_kw_missing']} out of {ins['total_kw']} category keywords
    ({ins['kw_leader_brand']} ranks for the most, at {ins['kw_leader_count']}).<br>
    {weakness_lines if weakness_lines else "Multilac leads or ties for 2nd on every other tracked metric this period."}
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

    ins = INSIGHTS
    lead_safe_text = (
        f' including the unique "{ins["ml_kw_number1"][0]}" at position #1 — a strong niche advantage worth promoting further'
        if ins["ml_kw_number1"] else ""
    )
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Insight:</b> {ins['kw_leader_brand']} ranks for the most keywords ({ins['kw_leader_count']} of {ins['total_kw']}).
    Multilac ranks for {ins['ml_kw_count']} keyword{'s' if ins['ml_kw_count'] != 1 else ''}{lead_safe_text}.
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

    ml_top_kw_text = (
        f' Multilac\'s green cell on "{INSIGHTS["ml_kw_number1"][0]}" is its strongest digital asset with zero competition.'
        if INSIGHTS["ml_kw_number1"] else " Multilac does not currently hold a #1 keyword position."
    )
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Insight:</b> Green cells = top positions.{ml_top_kw_text}
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

    ins = INSIGHTS
    seo_box_class = "multilac-box" if ins["seo_ml_rank"] == 1 else "warning-box"
    seo_box_icon  = "🟢" if ins["seo_ml_rank"] == 1 else "⚠️"
    seo_label     = "Strength" if ins["seo_ml_rank"] == 1 else "Watch-out"
    seo_seo_line = (
        f"Multilac leads SEO performance at {int(ins['seo_ml_value'])}%."
        if ins["seo_ml_rank"] == 1 else
        f"{ins['seo_leader']['Brand']} now leads SEO performance with {int(ins['seo_leader']['SEO_Performance'])}%, "
        f"ahead of Multilac's {int(ins['seo_ml_value'])}% ({ordinal(ins['seo_ml_rank'])} place)."
    )
    seo_bl_line = (
        f"Multilac also leads on backlinks with {int(ins['bl_ml_value'])}."
        if ins["bl_ml_rank"] == 1 else
        f"Multilac has {int(ins['bl_ml_value'])} backlinks ({ordinal(ins['bl_ml_rank'])} of {ins['n_brands']}), "
        f"while {ins['bl_leader']['Brand']} leads with {int(ins['bl_leader']['Backlinks'])}."
    )
    st.markdown(f"""
    <div class="{seo_box_class}">
    {seo_box_icon} <b>Multilac {seo_label}:</b> {seo_seo_line} {seo_bl_line}
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

    n = INSIGHTS["n_brands"]
    bl_pos = "top" if INSIGHTS["bl_ml_rank"] <= (n + 1) / 2 else "bottom"
    seo_pos = "right" if INSIGHTS["seo_ml_rank"] <= (n + 1) / 2 else "left"
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Quadrant reading:</b> Ideal position is top-right (high backlinks + high SEO score).
    Multilac currently sits {bl_pos}-{seo_pos} — {ordinal(INSIGHTS['seo_ml_rank'])} of {n} on SEO score
    and {ordinal(INSIGHTS['bl_ml_rank'])} of {n} on backlink count.
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
        st.caption("📅 Avg Likes based on last 20 posts | August Posts = posts published in August 2026")
    else:
        st.caption("📅 Avg Likes based on last 30 days | August Posts = posts published in August 2026")

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

    # Row 2 — August Posts and Total Posts
    col_left2, col_right2 = st.columns(2)
    with col_left2:
        st.subheader(f"📅 {platform} Posts in August 2026")
        fig3 = px.bar(
            platform_data.sort_values("August_Posts", ascending=False),
            x="Brand", y="August_Posts", color="Brand",
            title=f"{platform} Number of Posts — August 2026",
            labels={"August_Posts": "Posts in August 2026"},
            text="August_Posts",
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

    ins = INSIGHTS
    if platform == "Instagram":
        ig_engagement_line = (
            f"Multilac has the highest average likes ({ins['ig_ml_value']:.2f}) among all tracked brands."
            if ins["ig_ml_rank"] == 1 else
            f"Multilac's average likes ({ins['ig_ml_value']:.2f}) rank {ordinal(ins['ig_ml_rank'])} of {ins['ig_n']}, "
            f"behind {ins['ig_leader']['Brand']} ({ins['ig_leader']['Avg_Likes']:.2f})."
        )
        st.markdown(f"""
        <div class="insight-box">
        💡 <b>Instagram Insight:</b> {ins['ig_most_frequent']['Brand']} has the highest tracked posting
        frequency this period ({ins['ig_most_frequent']['Posting_Frequency'].lower()}), while {ins['ig_lowest_followers']['Brand']}
        has the fewest followers ({int(ins['ig_lowest_followers']['Followers']):,}) among tracked brands.
        {ig_engagement_line}
        {ins['ig_least_active_month']['Brand']} posted only {int(ins['ig_least_active_month']['August_Posts'])} time(s)
        in August 2026 — the lowest posting volume this month.
        </div>
        """, unsafe_allow_html=True)
    else:
        global_note = (
            f"{', '.join(ins['fb_global']['Brand'].tolist())}'s follower count is a global page and excluded from local comparisons. "
            if len(ins["fb_global"]) > 0 else ""
        )
        local_leader = ins["fb_local_followers_sorted"].iloc[0]
        fb_box_class = "multilac-box" if ins["fb_ml_rank"] <= 2 else "insight-box"
        fb_icon = "🟢" if ins["fb_ml_rank"] <= 2 else "💡"
        fb_engagement_line = (
            f"Multilac leads Facebook engagement at {ins['fb_ml_value']:.2f} avg likes/post."
            if ins["fb_ml_rank"] == 1 else
            f"Multilac's average likes ({ins['fb_ml_value']:.2f}) rank {ordinal(ins['fb_ml_rank'])} of {ins['fb_n']}, "
            f"close behind {ins['fb_leader']['Brand']} ({ins['fb_leader']['Avg_Likes']:.2f})."
        )
        st.markdown(f"""
        <div class="{fb_box_class}">
        {fb_icon} <b>Facebook Insight:</b> {global_note}Among local brands, {local_leader['Brand']}
        ({int(local_leader['Followers']):,} followers) leads on follower count.
        On engagement, {fb_engagement_line}
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

    ins = INSIGHTS
    rev_box_class = "multilac-box" if ins["rev_ml_rank"] <= 2 else "insight-box"
    rev_icon = "🟢" if ins["rev_ml_rank"] <= 2 else "💡"
    rev_line = (
        f"Multilac leads all brands with {ins['rev_ml_value']} reviews."
        if ins["rev_ml_rank"] == 1 else
        f"Multilac has the {ordinal(ins['rev_ml_rank'])} highest review count ({ins['rev_ml_value']}) "
        f"behind {ins['rev_leader']['Brand']} ({int(ins['rev_leader']['Total_Reviews'])}) — showing solid customer engagement."
    )
    st.markdown(f"""
    <div class="{rev_box_class}">
    {rev_icon} <b>Multilac Review Volume:</b> {rev_line}
    Actively encouraging customers to leave Google reviews could push Multilac
    higher in review volume, strengthening trust signals for new buyers.
    </div>
    """, unsafe_allow_html=True)

    top_star_names = " and ".join(ins["top_star_brands"]["Brand"].tolist())
    low_vis = ins["low_visibility_high_rating"]
    tie_phrase = "are tied for" if len(ins["top_star_brands"]) > 1 else "leads with"
    st.markdown(f"""
    <div class="insight-box">
    💡 <b>Opportunity:</b> {top_star_names} {tie_phrase} the top star rating ({ins['top_star_value']}).
    {low_vis['Brand']} has the fewest reviews ({int(low_vis['Total_Reviews'])}) among the top-rated brands,
    meaning its strong rating carries relatively little visibility.
    Multilac's combination of a {ins['ml_star']} rating AND the {ordinal(ins['rev_ml_rank'])} highest review count
    ({ins['rev_ml_value']}) is a strong trust position that should be highlighted in all marketing materials.
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Google Ratings Data")
    st.dataframe(google_filtered, use_container_width=True)