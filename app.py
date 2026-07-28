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

    # Clean No_of_Posts column
    social["No_of_Posts"] = social["No_of_Posts"].astype(str).str.replace(",", "").str.strip()
    social["No_of_Posts"] = pd.to_numeric(social["No_of_Posts"], errors="coerce")

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
            x="Brand",
            y="Backlinks",
            color="Brand",
            title="Number of Backlinks per Brand",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("📈 SEO Performance Score")
        fig2 = px.bar(
            backlinks.sort_values("SEO_Performance", ascending=False),
            x="Brand",
            y="SEO_Performance",
            color="Brand",
            title="SEO Performance Score (%) by Brand",
            labels={"SEO_Performance": "SEO Score (%)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.subheader("🔵 Backlinks vs SEO Performance")
    fig3 = px.scatter(
        backlinks,
        x="Backlinks",
        y="SEO_Performance",
        color="Brand",
        size="Backlinks",
        hover_name="Brand",
        title="Backlinks vs SEO Performance Score",
        labels={"SEO_Performance": "SEO Score (%)"},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig3, use_container_width=True)

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

    # Platform toggle
    platform = st.radio(
        "Select Platform",
        ["Instagram", "Facebook"],
        horizontal=True
    )

    platform_data = social[social["Platform"] == platform]

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader(f"👥 {platform} Followers")
        fig1 = px.bar(
            platform_data.sort_values("Followers", ascending=False),
            x="Brand",
            y="Followers",
            color="Brand",
            title=f"{platform} Followers by Brand",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader(f"❤️ {platform} Average Likes")
        fig2 = px.bar(
            platform_data.sort_values("Avg_Likes", ascending=False),
            x="Brand",
            y="Avg_Likes",
            color="Brand",
            title=f"{platform} Average Likes per Post",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.subheader(f"📅 {platform} Posting Frequency")
        fig3 = px.bar(
            platform_data.sort_values("Post_Frequency", ascending=False),
            x="Brand",
            y="Post_Frequency",
            color="Brand",
            title=f"{platform} Post Frequency (Posts per Day)",
            labels={"Post_Frequency": "Posts per Day"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_right2:
        st.subheader(f"📝 {platform} Number of Posts")
        fig4 = px.bar(
            platform_data.sort_values("No_of_Posts", ascending=False),
            x="Brand",
            y="No_of_Posts",
            color="Brand",
            title=f"{platform} Total Number of Posts",
            labels={"No_of_Posts": "Number of Posts"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    st.subheader("📋 Social Media Data")
    st.dataframe(social_filtered, use_container_width=True)

# =====================
# GOOGLE RATINGS PAGE
# =====================
elif page == "Google Ratings":
    st.title("⭐ Google Map Ratings")
    st.caption("Star ratings and total review counts by brand")
    st.divider()
    st.dataframe(google_filtered, use_container_width=True)
    