import streamlit as st
import pandas as pd
from scipy import stats
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode

st.header("Recommendations & Next Steps")

st.markdown("""
**1. Data Governance: Creating a Single Source of Truth (SSoT):**
   - **Implement data collection standards.** While centralising the data is important, a first step to stop 
    messy data being continued to be collected is to unify what is being collected. Stakeholders need to be
    consulted to assess reporting requests and requirements, data collection requirements and standardize all 
    surveys. This could include looking at new systems, or just adjusting old, archiving off all unused surveys, 
    and ensuring automations are upto date using the agreed new structure.
   - **Centralize NPS data.** Once data coming in is agreed upon and organised, old data can be looked at to 
    try to centralise all responses. This will likely include using ETL to unify data in the DataLake, ensuring there
    are correct foreign keys so tables can be joined for indepth future reporting.""")
st.markdown("""
**2. Visibility: Reporting & Dashboards:**
   - **Central NPS Dashboard.** Use BI tools connected to the datalake (e.g., Power BI, Tableau, Looker Studio, Python etc).  
     Potential views include:
     - Overall NPS trend over time
     - NPS by course, trainer, cohort
     - Views on unstructured data (i.e., further comments and feedback) such as wordclouds
     - Self service - filters including dropdown select/slider bars to allow people to view data in whatever subset they're interested in
   - **Automated Alerts & KPIs:**  
     - System dependent - Trigger alerts for sudden drops in NPS or high volumes of detractors.
     - Track response rates to ensure there's no unusual bias in the data. Encourage/send reminders when response rate is low.
   - **Natural Language Processing:**
     - An eventual goal would be to have the abiilty to interogate the data with natural language processing. This would of course
       be dependant on data privacy etc.
""")
st.markdown("""
**3. Actionability: Embedding NPS into Workflows:**
   - **Integrate NPS into Daily Workflows.** Feed key NPS metrics into team stand-ups or monthly performance reviews.
   - **Create automated workflows.** e.g., detractor feedback triggers a follow-up task in HubSpot. Create that personal
    out reach so detractors feel heard. This can help with future surveys.
   - **Recognition.** Encourage teams to act on NPS insights by linking improvements to performance metrics or recognition programs.
""")
