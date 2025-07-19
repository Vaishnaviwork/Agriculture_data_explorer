import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Set page config for better look
st.set_page_config(page_title="AgriData Explorer", page_icon="🌱", layout="wide")

# Custom CSS for background and colored containers
st.markdown("""
    <style>
        body {
            background-color: #f0f7fa;
        }
        .main-title {
            color: #2e8b57;
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
        }
        .desc {
            color: #444;
            font-size: 1.1rem;
            text-align: center;
        }
        .stButton>button {
            background-color: #2e8b57;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 2em;
        }
        .stButton>button:hover {
            background-color: #1e5d3b;
            color: #fff;
        }
        .result-container {
            background-color: #e6f2ff;
            border-radius: 10px;
            padding: 1em;
            margin-bottom: 1em;
        }
        .metric-container {
            display: flex;
            gap: 2em;
            justify-content: center;
            margin-bottom: 1em;
        }
    </style>
""", unsafe_allow_html=True)


st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2909/2909765.png", width=100)
st.sidebar.markdown("<h2 style='color:#2e8b57;'>AgriData Explorer</h2>", unsafe_allow_html=True)
st.sidebar.markdown("Analyze Indian agriculture data with interactive SQL-powered dashboards. Select a query and visualize insights instantly!")

# Database connection
db_url = "postgresql://enter_your_db_url"
engine = create_engine(db_url)

# SQL queries for various analyses
queries = {
    "🌾 Year-wise Trend of Rice Production Across States (Top 3)": """
        SELECT "Year", "State Name", SUM("RICE PRODUCTION (1000 tons)") AS rice_prod
        FROM agridata_explorer
        GROUP BY "Year", "State Name"
    """,
    "🍞 Top 5 Districts by Wheat Yield Increase Over the Last 5 Years": """
        SELECT "Dist Name", 
            MAX("WHEAT YIELD (Kg per ha)") - MIN("WHEAT YIELD (Kg per ha)") AS yield_increase
        FROM agridata_explorer
        WHERE "Year" >= (SELECT MAX("Year")-4 FROM agridata_explorer)
        GROUP BY "Dist Name"
        ORDER BY yield_increase DESC
        LIMIT 5
    """,
    "🌻 States with the Highest Growth in Oilseeds Production (5-Year Growth Rate)": """
        SELECT "State Name",
            (MAX("OILSEEDS PRODUCTION (1000 tons)") - MIN("OILSEEDS PRODUCTION (1000 tons)"))::float
            / NULLIF(MIN("OILSEEDS PRODUCTION (1000 tons)"),0) AS growth_rate
        FROM agridata_explorer
        WHERE "Year" >= (SELECT MAX("Year")-4 FROM agridata_explorer)
        GROUP BY "State Name"
        ORDER BY growth_rate DESC
        LIMIT 5
    """,
    "📊 District-wise Correlation Between Area and Production for Major Crops (Rice, Wheat, and Maize)": """
        SELECT "Dist Name", 
            CORR("RICE AREA (1000 ha)", "RICE PRODUCTION (1000 tons)") AS rice_corr,
            CORR("WHEAT AREA (1000 ha)", "WHEAT PRODUCTION (1000 tons)") AS wheat_corr,
            CORR("MAIZE AREA (1000 ha)", "MAIZE PRODUCTION (1000 tons)") AS maize_corr
        FROM agridata_explorer
        GROUP BY "Dist Name"
    """,
    "🧵 Yearly Production Growth of Cotton in Top 5 Cotton Producing States": """
        SELECT "Year", "State Name", SUM("COTTON PRODUCTION (1000 tons)") AS cotton_prod
        FROM agridata_explorer
        WHERE "State Name" IN (
            SELECT "State Name"
            FROM agridata_explorer
            GROUP BY "State Name"
            ORDER BY SUM("COTTON PRODUCTION (1000 tons)") DESC
            LIMIT 5
        )
        GROUP BY "Year", "State Name"
        ORDER BY "Year", cotton_prod DESC
    """,
    "🥜 Districts with the Highest Groundnut Production in 2020": """
        SELECT "Dist Name", SUM("GROUNDNUT PRODUCTION (1000 tons)") AS groundnut_prod
        FROM agridata_explorer
        WHERE "Year" = 2020
        GROUP BY "Dist Name"
        ORDER BY groundnut_prod DESC
        LIMIT 10
    """,
    "🌽 Annual Average Maize Yield Across All States": """
        SELECT "Year", AVG("MAIZE YIELD (Kg per ha)") AS avg_maize_yield
        FROM agridata_explorer
        GROUP BY "Year"
        ORDER BY "Year"
    """,
    "🟫 Total Area Cultivated for Oilseeds in Each State": """
        SELECT "State Name", SUM("OILSEEDS AREA (1000 ha)") AS total_oilseeds_area
        FROM agridata_explorer
        GROUP BY "State Name"
        ORDER BY total_oilseeds_area DESC
    """,
    "🥇 Districts with the Highest Rice Yield": """
        SELECT "Dist Name", AVG("RICE YIELD (Kg per ha)") AS avg_rice_yield
        FROM agridata_explorer
        GROUP BY "Dist Name"
        ORDER BY avg_rice_yield DESC
        LIMIT 10
    """,
    "⚖️ Compare the Production of Wheat and Rice for the Top 5 States Over 10 Years": """
        SELECT "Year", "State Name",
            SUM("RICE PRODUCTION (1000 tons)") AS rice_prod,
            SUM("WHEAT PRODUCTION (1000 tons)") AS wheat_prod
        FROM agridata_explorer
        WHERE "State Name" IN (
            SELECT "State Name"
            FROM agridata_explorer
            GROUP BY "State Name"
            ORDER BY SUM("RICE PRODUCTION (1000 tons)" + "WHEAT PRODUCTION (1000 tons)") DESC
            LIMIT 5
        )
        GROUP BY "Year", "State Name"
        ORDER BY "Year", "State Name"
    """
}

# Query insights/summaries
insights = {
    "🌾 Year-wise Trend of Rice Production Across States (Top 3)": "Shows how rice production has changed over the years for the top 3 producing states.",
    "🍞 Top 5 Districts by Wheat Yield Increase Over the Last 5 Years": "Highlights districts with the most improvement in wheat yield recently.",
    "🌻 States with the Highest Growth in Oilseeds Production (5-Year Growth Rate)": "Finds states with the fastest oilseeds production growth in the last 5 years.",
    "📊 District-wise Correlation Between Area and Production for Major Crops (Rice, Wheat, and Maize)": "See how strongly area and production are correlated for each crop at the district level.",
    "🧵 Yearly Production Growth of Cotton in Top 5 Cotton Producing States": "Tracks cotton production trends in the top 5 states.",
    "🥜 Districts with the Highest Groundnut Production in 2020": "Top groundnut producing districts for the year 2020.",
    "🌽 Annual Average Maize Yield Across All States": "Average maize yield per year across India.",
    "🟫 Total Area Cultivated for Oilseeds in Each State": "Total oilseeds area cultivated in each state.",
    "🥇 Districts with the Highest Rice Yield": "Districts with the highest average rice yield.",
    "⚖️ Compare the Production of Wheat and Rice for the Top 5 States Over 10 Years": "Compare wheat and rice production trends for the top 5 states."
}

# Main title and description
st.markdown("<div class='main-title'>🌱 AgriData Explorer</div>", unsafe_allow_html=True)
st.markdown("<div class='desc'>A colorful dashboard to explore Indian agriculture data with interactive SQL queries and visualizations.</div>", unsafe_allow_html=True)
st.write("")

# Query selection in sidebar
query_name = st.sidebar.selectbox("🔎 Select a Query", list(queries.keys()))

# Main area: show insight/summary
st.markdown(f"<div class='result-container'><b>📝 Insight:</b> {insights[query_name]}</div>", unsafe_allow_html=True)

if st.button("▶️ Run Query"):
    sql = queries[query_name]
    df = pd.read_sql(sql, engine)
    st.markdown("<div class='result-container'><b>📋 Results:</b></div>", unsafe_allow_html=True)
    st.dataframe(df.head(50), use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv,
        file_name='query_results.csv',
        mime='text/csv',
        key="download-csv"
    )

    # Show summary metrics if available
    if "rice_prod" in df.columns:
        st.metric("Total Rice Production (1000 tons)", int(df["rice_prod"].sum()))
    if "wheat_prod" in df.columns:
        st.metric("Total Wheat Production (1000 tons)", int(df["wheat_prod"].sum()))
    if "groundnut_prod" in df.columns:
        st.metric("Total Groundnut Production (1000 tons)", int(df["groundnut_prod"].sum()))

    # Visualization logic for each query
    if query_name.startswith("🌾"):
        top_states = df.groupby("State Name")["rice_prod"].sum().nlargest(3).index
        plot_df = df[df["State Name"].isin(top_states)]
        fig, ax = plt.subplots(figsize=(8,4))
        for state in top_states:
            state_df = plot_df[plot_df["State Name"] == state]
            ax.plot(state_df["Year"], state_df["rice_prod"], marker='o', label=state)
        ax.set_title("Year-wise Rice Production Trend (Top 3 States)", color="#2e8b57")
        ax.set_xlabel("Year")
        ax.set_ylabel("Rice Production (1000 tons)")
        ax.legend()
        st.pyplot(fig)

    elif query_name.startswith("🍞"):
        st.bar_chart(df.set_index("Dist Name")["yield_increase"])

    elif query_name.startswith("🌻"):
        st.bar_chart(df.set_index("State Name")["growth_rate"])

    elif query_name.startswith("📊"):
        st.write(df.style.background_gradient(cmap="YlGn"))

    elif query_name.startswith("🧵"):
        fig, ax = plt.subplots(figsize=(8,4))
        for state in df["State Name"].unique():
            state_df = df[df["State Name"] == state]
            ax.plot(state_df["Year"], state_df["cotton_prod"], marker='o', label=state)
        ax.set_title("Yearly Cotton Production in Top 5 States", color="#2e8b57")
        ax.set_xlabel("Year")
        ax.set_ylabel("Cotton Production (1000 tons)")
        ax.legend()
        st.pyplot(fig)

    elif query_name.startswith("🥜"):
        st.bar_chart(df.set_index("Dist Name")["groundnut_prod"])
        # Map visualization if lat/lon columns exist
        if "Latitude" in df.columns and "Longitude" in df.columns:
            st.markdown("#### 📍 Top Districts on Map")
            st.map(df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))

    elif query_name.startswith("🌽"):
        st.line_chart(df.set_index("Year")["avg_maize_yield"])

    elif query_name.startswith("🟫"):
        st.bar_chart(df.set_index("State Name")["total_oilseeds_area"])

    elif query_name.startswith("🥇"):
        st.bar_chart(df.set_index("Dist Name")["avg_rice_yield"])

    elif query_name.startswith("⚖️"):
        fig, ax = plt.subplots(figsize=(8,4))
        for state in df["State Name"].unique():
            state_df = df[df["State Name"] == state]
            ax.plot(state_df["Year"], state_df["rice_prod"], label=f"{state} - Rice", linestyle='-', marker='o')
            ax.plot(state_df["Year"], state_df["wheat_prod"], label=f"{state} - Wheat", linestyle='--', marker='x')
        ax.set_title("Wheat vs Rice Production (Top 5 States, Last 10 Years)", color="#2e8b57")
        ax.set_xlabel("Year")
        ax.set_ylabel("Production (1000 tons)")
        ax.legend()
        st.pyplot(fig)
