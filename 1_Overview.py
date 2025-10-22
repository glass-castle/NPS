import streamlit as st
import pandas as pd
from scipy import stats
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode

# Load data
df_form = pd.read_csv('google_form.csv')
df_form['How likely are you to recommend the Makers Academy Careers Team to future cohorts?'] = pd.to_numeric(
    df_form['How likely are you to recommend the Makers Academy Careers Team to future cohorts?'], 
    errors='coerce'
)
df_hubspot = pd.read_csv('hubspot.csv')

# Page configuration
st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout='wide',
)

st.sidebar.success('Select a page above.')

st.sidebar.divider()

st.header("Data Exploration")

st.markdown("""To start this project, as with any project, some initial data exploration is needed.
            First some initial calculations were run on the data, including number of responses, first and last use, Min, Max, Mean, Mode, Median 
            and then calculations to work out who were Promoters, Passives and Detractors with an NPS per survey calculated.""")

# Create NPS analysis
grouped = df_hubspot.groupby('Survey Name')
analysis_data = []

for survey_name, group in grouped:
    scores = group['Rating'].dropna()
    
    # Calculate counts
    num_responses = len(group)
    promoters = (scores >= 9).sum()
    passives = ((scores >= 7) & (scores < 9)).sum()
    detractors = (scores < 7).sum()
    
    # Calculate NPS score: (Promoters/Total - Detractors/Total) * 100
    nps_score = int(((promoters / num_responses) - (detractors / num_responses)) * 100)
    
    # Calculate statistics
    first_appearance = group['Date'].min() if len(group) > 0 else None
    last_appearance = group['Date'].max() if len(group) > 0 else None
    min_score = int(scores.min()) if pd.notna(scores.min()) else None
    max_score = int(scores.max()) if pd.notna(scores.max()) else None
    mean_score = scores.mean()
    median_score = int(scores.median()) if pd.notna(scores.median()) else None
    
    # Calculate mode
    try:
        mode_score = scores.mode().iloc[0] if not scores.mode().empty else None
    except:
        mode_score = scores.mode()[0] if len(scores.mode()) > 0 else None
    
    analysis_data.append({
        'Survey Name': survey_name,
        'Number of Responses': num_responses,
        'First Appearance': first_appearance,
        'Last Appearance': last_appearance,
        'Min Score': min_score,
        'Max Score': max_score,
        'Mean': round(mean_score, 2),
        'Mode': int(mode_score) if pd.notna(mode_score) else None,
        'Median': median_score,
        'Promoters (9-10)': promoters,
        'Passives (7-8)': passives,
        'Detractors (0-6)': detractors,
        'NPS Score': nps_score
    })

# Create DataFrame
df_analysis = pd.DataFrame(analysis_data)

# Separate CSAT surveys (max score of 2) from NPS surveys
df_CSAT = df_analysis[df_analysis['Max Score'] == 2].copy()
df_analysis_nps = df_analysis[df_analysis['Max Score'] != 2]

st.markdown('**Initial Data Analysis by Survey**')
st.dataframe(df_analysis, use_container_width=True, hide_index=True)

st.markdown("""This highlighted some problem surveys, where the max score was 2, not 10. These look like CSAT surveys (which the name does imply) so these were 
            separated from the NPS""")

st.markdown('**NPS Analysis by Survey**')
st.dataframe(df_analysis_nps, use_container_width=True, hide_index=True)

# Process CSAT data
if len(df_CSAT) > 0:
    for idx, row in df_CSAT.iterrows():
        survey_name = row['Survey Name']
        group = df_hubspot[df_hubspot['Survey Name'] == survey_name]
        scores = group['Rating'].dropna()
        positives = (scores == 2).sum()
        csat = round((positives / row['Number of Responses']) * 100)
        df_CSAT.at[idx, 'Positive (2)'] = positives
        df_CSAT.at[idx, 'CSAT Score'] = csat
    
    df_CSAT['CSAT Score'] = df_CSAT['CSAT Score'].apply(lambda x: f"{int(x)}%")

    # Drop NPS columns from CSAT
    df_CSAT = df_CSAT.drop(columns=['Promoters (9-10)', 'Passives (7-8)', 'Detractors (0-6)', 'NPS Score'])
    
st.markdown('**CSAT Analysis by Survey**')
st.markdown("""While this project called for NPS data to be analysed, CSAT calculations are easy to run, so this was done quickly, as it's another indication
                of how well a company is performing.""")
st.dataframe(df_CSAT, use_container_width=True, hide_index=True)

st.markdown("""We can see that CSAT is typically over 80%, a good indication that the company is meeting and exceeding people's expectations.""")

st.markdown("""With the HubSpot data looked at, it was time to look at the Google Form Data. A similar set of metrics were looked at for it:""")

grouped_google = df_form.groupby("What's your cohort?")
analysis_data_google = []

for survey_name, group in grouped_google:
    scores = group['How likely are you to recommend the Makers Academy Careers Team to future cohorts?'].dropna()
    
    # Calculate counts
    num_responses = len(group)
    promoters = (scores >= 9).sum()
    passives = ((scores >= 7) & (scores < 9)).sum()
    detractors = (scores < 7).sum()
    
    # Calculate NPS score: (Promoters/Total - Detractors/Total) * 100
    nps_score = int(((promoters / num_responses) - (detractors / num_responses)) * 100)
    
    # Calculate statistics
    first_appearance = group['Conversion Date'].min() if len(group) > 0 else None
    last_appearance = group['Conversion Date'].max() if len(group) > 0 else None
    min_score = int(scores.min()) if pd.notna(scores.min()) else None
    max_score = int(scores.max()) if pd.notna(scores.max()) else None
    mean_score = scores.mean()
    median_score = int(scores.median()) if pd.notna(scores.median()) else None
    
    # Calculate mode
    try:
        mode_score = scores.mode().iloc[0] if not scores.mode().empty else None
    except:
        mode_score = scores.mode()[0] if len(scores.mode()) > 0 else None
    
    analysis_data_google.append({
        'Survey Name': survey_name,
        'Number of Responses': num_responses,
        'First Appearance': first_appearance,
        'Last Appearance': last_appearance,
        'Min Score': min_score,
        'Max Score': max_score,
        'Mean': round(mean_score, 2),
        'Mode': int(mode_score) if pd.notna(mode_score) else None,
        'Median': median_score,
        'Promoters (9-10)': promoters,
        'Passives (7-8)': passives,
        'Detractors (0-6)': detractors,
        'NPS Score': nps_score
    })

# Create DataFrame
df_analysis_google = pd.DataFrame(analysis_data_google)

st.markdown('**Google Form NPS Analysis by Cohort**')
st.dataframe(df_analysis_google, use_container_width=True, hide_index=True)

st.markdown("""Looking at the Google Form data, there doesn't seems to be any option for survey name, so grouping by this wasn't a good idea.
            Also the top row '*redacted*' is showing that there's no data on these lines, so it needs dropping.""")

# Drop unwanted row and column
st.markdown('**Google Form Combined NPS Analysis**')

# Drop any empty or invalid rows
df_form = df_form.dropna(subset=['How likely are you to recommend the Makers Academy Careers Team to future cohorts?'])

# Extract the scores column
scores = df_form['How likely are you to recommend the Makers Academy Careers Team to future cohorts?']

# Calculate counts
num_responses = len(scores)
promoters = (scores >= 9).sum()
passives = ((scores >= 7) & (scores < 9)).sum()
detractors = (scores < 7).sum()

# Calculate NPS
nps_score = int(((promoters / num_responses) - (detractors / num_responses)) * 100)

# Calculate statistics
first_appearance = df_form['Conversion Date'].min() if 'Conversion Date' in df_form.columns else None
last_appearance = df_form['Conversion Date'].max() if 'Conversion Date' in df_form.columns else None
min_score = int(scores.min()) if pd.notna(scores.min()) else None
max_score = int(scores.max()) if pd.notna(scores.max()) else None
mean_score = scores.mean()
median_score = int(scores.median()) if pd.notna(scores.median()) else None

# Mode
try:
    mode_score = scores.mode().iloc[0] if not scores.mode().empty else None
except:
    mode_score = scores.mode()[0] if len(scores.mode()) > 0 else None

# Create a single-row summary DataFrame
df_analysis_google = pd.DataFrame([{
    'Number of Responses': num_responses,
    'First Appearance': first_appearance,
    'Last Appearance': last_appearance,
    'Min Score': min_score,
    'Max Score': max_score,
    'Mean': round(mean_score, 2),
    'Mode': int(mode_score) if pd.notna(mode_score) else None,
    'Median': median_score,
    'Promoters (9-10)': promoters,
    'Passives (7-8)': passives,
    'Detractors (0-6)': detractors,
    'NPS Score': nps_score
}])

# Display final table
st.dataframe(df_analysis_google, use_container_width=True, hide_index=True)

st.markdown("""This table shows the overall NPS results from the entire Google Form dataset, 
providing a single summary view across all cohorts combined.""")

st.subheader("NPS Breakdown by Year")

st.markdown("**HubSpot NPS by Year (CSAT removed)**")

st.markdown("""Just to establish some baseline stats, NPS was looked at yearly for each data set, then combined to give overall yearly scores.""")

if 'Date' in df_hubspot.columns and 'Rating' in df_hubspot.columns:

    # Remove CSAT surveys based on df_CSAT
    if 'Survey Name' in df_hubspot.columns and not df_CSAT.empty:
        csat_survey_names = df_CSAT['Survey Name'].unique()
        df_hubspot_filtered = df_hubspot[~df_hubspot['Survey Name'].isin(csat_survey_names)].copy()
    else:
        df_hubspot_filtered = df_hubspot.copy()

    # Parse Year and numeric ratings safely
    df_hubspot_filtered.loc[:, 'Year'] = pd.to_datetime(df_hubspot_filtered['Date'], errors='coerce').dt.year
    df_hubspot_filtered.loc[:, 'Rating_num'] = pd.to_numeric(df_hubspot_filtered['Rating'], errors='coerce')

    # Keep only valid ratings and years >= 2019
    df_hubspot_filtered = df_hubspot_filtered.dropna(subset=['Rating_num', 'Year'])
    df_hubspot_filtered = df_hubspot_filtered[df_hubspot_filtered['Year'] >= 2019]
    df_hubspot_filtered = df_hubspot_filtered[(df_hubspot_filtered['Rating_num'] >= 0) & (df_hubspot_filtered['Rating_num'] <= 10)]

    # Group by Year and calculate NPS
    yearly_rows = []
    for year, group in df_hubspot_filtered.groupby('Year'):
        scores = group['Rating_num']
        responses = scores.count()
        promoters = (scores >= 9).sum()
        passives = ((scores >= 7) & (scores <= 8)).sum()
        detractors = (scores <= 6).sum()
        nps_score = int(((promoters / responses) - (detractors / responses)) * 100) if responses > 0 else None

        yearly_rows.append({
            'Year': int(year),
            'Responses': int(responses),
            'Promoters (9-10)': int(promoters),
            'Passives (7-8)': int(passives),
            'Detractors (0-6)': int(detractors),
            'NPS Score': nps_score
        })

    df_hubspot_year_summary = pd.DataFrame(sorted(yearly_rows, key=lambda r: r['Year']))
    st.dataframe(df_hubspot_year_summary, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Missing 'Date' or 'Rating' column in HubSpot data — cannot calculate yearly breakdown.")

st.markdown("**Google Form NPS by Year**")

if 'Conversion Date' in df_form.columns and 'How likely are you to recommend the Makers Academy Careers Team to future cohorts?' in df_form.columns:

    df_form_filtered = df_form.copy()

    # Parse Year and numeric ratings safely
    df_form_filtered.loc[:, 'Year'] = pd.to_datetime(df_form_filtered['Conversion Date'], errors='coerce').dt.year
    df_form_filtered.loc[:, 'Rating_num'] = pd.to_numeric(
        df_form_filtered['How likely are you to recommend the Makers Academy Careers Team to future cohorts?'], errors='coerce'
    )

    # Keep only valid ratings and years >= 2019
    df_form_filtered = df_form_filtered.dropna(subset=['Rating_num', 'Year'])
    df_form_filtered = df_form_filtered[df_form_filtered['Year'] >= 2019]
    df_form_filtered = df_form_filtered[(df_form_filtered['Rating_num'] >= 0) & (df_form_filtered['Rating_num'] <= 10)]

    # Group by Year and calculate NPS
    yearly_rows_google = []
    for year, group in df_form_filtered.groupby('Year'):
        scores = group['Rating_num']
        responses = scores.count()
        promoters = (scores >= 9).sum()
        passives = ((scores >= 7) & (scores <= 8)).sum()
        detractors = (scores <= 6).sum()
        nps_score = int(((promoters / responses) - (detractors / responses)) * 100) if responses > 0 else None

        yearly_rows_google.append({
            'Year': int(year),
            'Responses': int(responses),
            'Promoters (9-10)': int(promoters),
            'Passives (7-8)': int(passives),
            'Detractors (0-6)': int(detractors),
            'NPS Score': nps_score
        })

    df_google_year_summary = pd.DataFrame(sorted(yearly_rows_google, key=lambda r: r['Year']))
    st.dataframe(df_google_year_summary, use_container_width=True, hide_index=True)

else:
    st.warning("⚠️ Missing required columns in Google Form data — cannot calculate yearly breakdown.")

# Concatenate without source
df_combined_raw = pd.concat([df_hubspot_year_summary, df_google_year_summary], ignore_index=True)

# Group by Year and sum numeric columns
df_year_combined = df_combined_raw.groupby('Year', as_index=False).agg({
    'Responses': 'sum',
    'Promoters (9-10)': 'sum',
    'Passives (7-8)': 'sum',
    'Detractors (0-6)': 'sum'
})

# Recalculate NPS based on combined totals
df_year_combined['NPS Score'] = (
    (df_year_combined['Promoters (9-10)'] / df_year_combined['Responses'])
    - (df_year_combined['Detractors (0-6)'] / df_year_combined['Responses'])
) * 100
df_year_combined['NPS Score'] = df_year_combined['NPS Score'].round().astype(int)

# Display result
st.markdown("**Combined NPS by Year (HubSpot + Google Form)**")

st.dataframe(df_year_combined, use_container_width=True, hide_index=True)
