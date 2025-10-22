import streamlit as st
import pandas as pd
import altair as alt
import plotly.graph_objects as go

# --- Load CSVs ---
df_form = pd.read_csv('google_form.csv')
df_hubspot = pd.read_csv('hubspot.csv')

st.set_page_config(layout='wide')
st.sidebar.success('Select a page above.')

st.header("Key Findings") 
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("""Wordcloud""")
    st.image("promoter.jpg", width=500)
    st.markdown("""
**The comments from promoters were run through a custom word cloud generator:**

- Clearly, support and support with items (jobs, interviews) are key in keeping people happy.
- Getting jobs and interviews appear to be important as these show up frequently.
- CV help is also a big feature.

And to a slightly lesser extent: - coaches, processes, advice, and help all feature highly in comments, showing these are also important to candidates.
""")

# --- Clean column names ---
df_hubspot.columns = df_hubspot.columns.str.strip()
df_form.columns = df_form.columns.str.strip()

# --- Keep only needed columns ---
# HubSpot already has 'Rating' and 'Date'
df_hubspot = df_hubspot[['Rating', 'Date']].copy()

# Form CSV: rename and keep only Rating + Date
df_form = df_form.rename(columns={
    "How likely are you to recommend the Makers Academy Careers Team to future cohorts?": "Rating",
    "Conversion Date": "Date"
})

columns_to_keep = ['Rating', 'Date']
df_form = df_form[[col for col in columns_to_keep if col in df_form.columns]].copy()

# --- Cleaning function ---
def clean_df(df):
    df = df.copy()
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.normalize()
    df = df.dropna(subset=['Rating', 'Date'])
    return df

df_hubspot = clean_df(df_hubspot)
df_form = clean_df(df_form)
df_combined = pd.concat([df_hubspot, df_form], ignore_index=True)

# --- NPS calculation ---
def calculate_nps(scores):
    total = len(scores)
    if total == 0:
        return 0
    promoters = (scores >= 9).sum()
    detractors = (scores <= 6).sum()
    return round((promoters - detractors) / total * 100, 0)

# --- Precompute NPS for plotting ---
def compute_nps_plot_data(df):
    df = df.copy()
    df['quarter_year'] = df['Date'].apply(lambda x: f"{x.year}-Q{x.quarter}")

    # Quarterly NPS
    nps_quarterly = df.groupby('quarter_year')['Rating'].apply(calculate_nps).reset_index()
    nps_quarterly = nps_quarterly.rename(columns={'Rating': 'Value'})
    nps_quarterly['Period'] = 'Quarterly'

    # Yearly NPS (plotted at Q4)
    df['year'] = df['Date'].dt.year
    nps_yearly = df.groupby('year')['Rating'].apply(calculate_nps).reset_index()
    nps_yearly = nps_yearly.rename(columns={'Rating': 'Value'})
    nps_yearly['quarter_year'] = nps_yearly['year'].astype(str) + '-Q4'
    nps_yearly['Period'] = 'Yearly'

    plot_df = pd.concat([
        nps_quarterly[['quarter_year', 'Value', 'Period']],
        nps_yearly[['quarter_year', 'Value', 'Period']]
    ], ignore_index=True)
    
    plot_df = plot_df.sort_values('quarter_year')
    return plot_df

# --- Precompute all datasets once ---
nps_data_dict = {
    "Combined": compute_nps_plot_data(df_combined),
    "HubSpot Only": compute_nps_plot_data(df_hubspot),
    "Forms Only": compute_nps_plot_data(df_form)
}

with col2:
    # --- NPS GAUGE SECTION ---
    st.subheader("Annual NPS Score")

    gauge_col1, gauge_col2 = st.columns([1.5, 2])

    with gauge_col1:
        # Get available years from combined data
        df_combined['year'] = df_combined['Date'].dt.year
        available_years = sorted(df_combined['year'].unique(), reverse=True)
        
        selected_year = st.selectbox(
            "Select Year",
            available_years,
            key="year_selector"
        )
        
        # Calculate NPS for selected year
        year_data = df_combined[df_combined['year'] == selected_year]
        nps_score = calculate_nps(year_data['Rating'])
        
        # Determine color based on NPS score
        if nps_score >= 50:
            gauge_color = "#00CC96"  # Green
        elif nps_score >= 0:
            gauge_color = "#FFA15A"  # Orange
        else:
            gauge_color = "#EF553B"  # Red
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=nps_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'font': {'size': 50}},
            gauge={
                'axis': {'range': [-100, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                'bar': {'color': gauge_color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-100, 0], 'color': '#FFE6E6'},
                    {'range': [0, 50], 'color': '#FFF4E6'},
                    {'range': [50, 100], 'color': '#E6F9F0'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': nps_score
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white",
            font={'color': "darkgray", 'family': "Arial"}
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with gauge_col2:
        st.markdown(f"""
        ### NPS Score Interpretation for {selected_year}
        
        **Score: {nps_score}**
        
        - **Excellent (50-100):** World-class customer satisfaction
        - **Good (0-49):** Room for improvement but positive overall
        - **Needs Improvement (<0):** More detractors than promoters
        
        **For {selected_year}:**
        - Total responses: {len(year_data)}
        - Promoters (9-10): {(year_data['Rating'] >= 9).sum()}
        - Passives (7-8): {((year_data['Rating'] >= 7) & (year_data['Rating'] <= 8)).sum()}
        - Detractors (0-6): {(year_data['Rating'] <= 6).sum()}
        """)

st.markdown("---")

# --- Dropdown to select dataset ---
st.subheader("Quarterly vs Yearly NPS (Yearly Plotted at Q4)")
option = st.selectbox(
    "Select Data Source for NPS Trend",
    list(nps_data_dict.keys())
)

plot_data = nps_data_dict[option]

# --- Altair chart ---
combined_chart = (
    alt.Chart(plot_data)
    .mark_line(point=True)
    .encode(
        x=alt.X('quarter_year', title='Quarter/Year', sort=None),
        y=alt.Y('Value', title='NPS Score'),
        color=alt.Color(
            'Period',
            scale=alt.Scale(domain=['Quarterly', 'Yearly'], range=['cyan', 'purple']),
            title='NPS Type'
        ),
        tooltip=['quarter_year', 'Value', 'Period']
    )
)

st.altair_chart(combined_chart, use_container_width=True)

if option == "Combined":
    st.markdown("""Due to reasons explained in each graph, combined is really the only way to get a true picture on 
                how the NPS score is trending.""")
    st.markdown("""Looking at the combined data, we can see that though there was a dip in the yearly data in 2023, 
                NPS has remained consistently above 20, a good indicaiton that overall for each year, there is a good 
                level of training being delivered. There is a sizable and consistent dip from Q2 - 2023, until Q4 - 2023, 
                but this seems to have been rectified in 2024, and NPS returns to consistently high numbers.""")
    st.markdown("""The only other time we see low NPS is from Q2-2019 - Q3-2020. This is however a long time ago, and the
                curriculum has likely changed, as potentially has coaches or trainers (or retraining has happened).""")
elif option == "HubSpot Only":
    st.markdown("""The HubSpt data does include NPS from both students and companies.""")
    st.markdown("""The HubSpot only data follows a very similar pattern initially to the combined, showing it has a large
                weighting to the early results. Later in the data we see some different dips to the combined data. We see 
                a big drop Q3 2021, and Q4-2023. This last dip does pull the NPS for that year down to just under 20, but 
                otherwise the NPs score does remain above it showing again a consistent service delivery.""")
else:
    st.markdown("""When we look at the forms only data, which is only student data, we can see a clear trend of NPS trending
                down from 2019 to 2023. That said the NPS in the google forms data is consistently higher than the combined
                or the HubSpot data. This was a much longer questionaire, and was sent after someone had successfully secured
                a role, which is going to influence how people feel about the training they received. The score is consistently
                above 30.""")
    st.markdown("""After 2023 it does start to trend back up from it's low point of 34, but overall the NPS in this paints a much
                different picture to the Hubspot, and in isolation does artificially inflate the NPS.""")