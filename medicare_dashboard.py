import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

# Load your actual data into a DataFrame
df = pd.read_csv('Medicare_clean.csv')

# Streamlit App
st.title("Medicare Part B Dashboard")

# Sidebar for filter options and navigation
st.sidebar.header('Filter Options')
selected_states = st.sidebar.multiselect('Select State(s)', df['State_Abrvtn'].unique())

# Filter the DataFrame based on selected states
if selected_states:
    df = df[df['State_Abrvtn'].isin(selected_states)]

# Sidebar for navigation
st.sidebar.header('Navigation')
tab = st.sidebar.radio("Go to", ["Provider Analysis", "Speciality Analysis", "Maps"])

def abbreviate_number(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}MM"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return str(value)
    
# Provider Analysis
if tab == "Provider Analysis":
    st.header("Provider Analysis")
    
    col1, col2, col3, col4 = st.columns(4)

    total_providers = df['NPI'].nunique()
    col1.metric("Total Providers", abbreviate_number(total_providers))

    total_charges = df['Avg_Sbmtd_Chrg'].sum()
    col2.metric("Total Charges", abbreviate_number(total_charges))

    total_services = df['Tot_Srvcs'].sum()
    col3.metric("Total Services Provided", abbreviate_number(total_services))
    
    total_beneficiaries = df['Tot_Benes'].sum()
    col4.metric("Total Beneficiaries", abbreviate_number(total_beneficiaries))
     
    col5, col6 = st.columns([3, 2])

    with col5:
        st.subheader("Top Providers by Total Charges")
        top_providers = df.groupby('Last_Org_Name').agg(
            {'Avg_Sbmtd_Chrg': 'sum', 'Provider_Type': 'first'}).nlargest(15, 'Avg_Sbmtd_Chrg').reset_index()
        fig_providers = alt.Chart(top_providers).mark_bar().encode(
            y=alt.Y('Last_Org_Name:N', title='Provider Name', sort='-x'),
            x=alt.X('Avg_Sbmtd_Chrg:Q', title='Total Charges'),
            color=alt.Color('Provider_Type:N', legend=alt.Legend(title="Provider Type")), 
        )
        st.altair_chart(fig_providers, use_container_width=True)
            

    with col6:
        st.subheader("Total Charges and Distribution by Provider Type")
        
        # Calculate percentages
        provider_type_pct = df['Provider_Type'].value_counts(normalize=True).reset_index()
        provider_type_pct.columns = ['Provider_Type', 'Percentage']  
        provider_type_pct['Percentage'] = provider_type_pct['Percentage'] * 100  # Convert to percentage
        provider_type_pct['Percentage'] = provider_type_pct['Percentage'].map(lambda x: f"{x:.2f}%")

        # Calculate counts
        provider_type_distribution = df['Provider_Type'].value_counts().reset_index()
        provider_type_distribution.columns = ['Provider_Type', 'Count']     

        # Calculate sum of Avg_Sbmtd_Chrg for each Provider_Type
        provider_type_charge_sum = df.groupby('Provider_Type')['Avg_Sbmtd_Chrg'].sum().reset_index()
        provider_type_charge_sum.columns = ['Provider_Type', 'Total_Avg_Sbmtd_Chrg']
        provider_type_charge_sum['Total_Avg_Sbmtd_Chrg_txt'] = provider_type_charge_sum['Total_Avg_Sbmtd_Chrg'].apply(abbreviate_number)

        # Combine counts and percentages for the inner donut
        provider_type_distribution = provider_type_distribution.merge(provider_type_pct, on='Provider_Type')

        # Inner donut chart    

        inner_donut = alt.Chart(provider_type_distribution).mark_arc(
            innerRadius=30, outerRadius=85, opacity=0.7).encode(
            color=alt.Color('Provider_Type:N', legend=alt.Legend(title="Provider Type")),
            theta=alt.Theta("Count:Q").stack(True),   
       
            tooltip=['Provider_Type', 'Count', alt.Tooltip('Percentage')]
        )  

        # Inner text for percentages
        inner_text = inner_donut.mark_text(radius=60, align='center', fontSize=12, fontWeight='bold').encode(text='Percentage')

        # Outer donut chart
        outer_donut = alt.Chart(provider_type_charge_sum).mark_arc(
            innerRadius=90, outerRadius=130, opacity=0.7).encode(
            theta=alt.Theta('Total_Avg_Sbmtd_Chrg:Q', stack=True),
            color=alt.Color('Provider_Type:N', legend=None),
            tooltip=['Provider_Type', 'Total_Avg_Sbmtd_Chrg']
        )

        # Outer text for total average submitted charge
        outer_text = outer_donut.mark_text(radius=110, align='center', fontSize=12, fontWeight='bold').encode(text='Total_Avg_Sbmtd_Chrg_txt')

        # Layer the inner and outer donuts together
        final_chart = alt.layer(inner_donut, inner_text, outer_donut, outer_text).resolve_scale(theta='independent')
        st.altair_chart(final_chart, use_container_width=True)

# Service Analysis
elif tab == "Speciality Analysis":
    st.header("Speciality Analysis")

    # Calculate KPIs
    total_specialities = df['Speciality'].nunique()
    most_common_speciality = df['Speciality'].mode()[
        0]
    speciality_most_charge = df.groupby('Speciality')['Avg_Sbmtd_Chrg'].sum().idxmax()

    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Specialities", total_specialities)
    kpi2.metric("Most Common Speciality", most_common_speciality)
    kpi3.metric("Highest Total Charges", speciality_most_charge)

    st.subheader("Pareto Chart of Specialities by Total Charges")
    # Pareto Chart
    speciality_charges = df.groupby('Speciality')['Avg_Sbmtd_Chrg'].sum().reset_index()
    speciality_charges = speciality_charges.sort_values('Avg_Sbmtd_Chrg', ascending=False)
    speciality_charges['Cumulative_Charges'] = speciality_charges['Avg_Sbmtd_Chrg'].cumsum()
    speciality_charges['Cumulative_Percentage'] = 100 * speciality_charges['Cumulative_Charges'] / speciality_charges['Avg_Sbmtd_Chrg'].sum()
    filter_speciality_charges = speciality_charges[speciality_charges['Cumulative_Percentage'] <= 85]

    bar = alt.Chart(filter_speciality_charges).mark_bar().encode(
        x=alt.X('Speciality:N', title='Speciality', sort='-y'),
        y=alt.Y('Avg_Sbmtd_Chrg:Q', title='Total Charges'),
    ).properties(
        width=800,
        height=400
    )

    line = alt.Chart(filter_speciality_charges).mark_line(color='red').encode(
        y=alt.Y('Cumulative_Percentage:Q', title='Cumulative Percentage', axis=alt.Axis(grid=True)),
        x=alt.X('Speciality:N', title='Speciality', sort=alt.EncodingSortField(
        field='Avg_Sbmtd_Chrg', order='descending')),
        tooltip=['Speciality', 'Cumulative_Percentage']
    )
  
    pareto_chart = alt.layer(bar, line).resolve_scale(
        y='independent'
    )
    st.altair_chart(pareto_chart, use_container_width=True)

    # Calculate data for the chart
    speciality_summary = df.groupby('Speciality').agg({
        'NPI': 'count',  # Count of providers
        'Avg_Sbmtd_Chrg': ['sum', 'median']  # Sum and median of average submitted charges
    }).reset_index()
    speciality_summary.columns = ['Speciality', 'Provider_Count', 'Total_Charges', 'Median_Charges']
    
    svc_col1, svc_col2 = st.columns([3, 2])

    with svc_col1:
        st.subheader("Scatter Plot of Total Charges vs Median Charges by Speciality")

        scatter = alt.Chart(speciality_summary).mark_circle().encode(
            x=alt.X('Total_Charges:Q', title='Total Charges', scale=alt.Scale(zero=False, type='log')),
            y=alt.Y('Median_Charges:Q', title='Median Charges', scale=alt.Scale(zero=False, padding=1, type='log')),
            size=alt.Size('Provider_Count:Q', title='Provider Count', scale=alt.Scale(range=[10, 100])),
            tooltip=['Speciality', 'Provider_Count', 'Total_Charges', 'Median_Charges']
        ).properties(
            width=400,  # Adjust width to fit within the column
            height=400
        )

        st.altair_chart(scatter, use_container_width=True)

    with svc_col2:
        
        st.subheader("Data Table")
        # Add a selectbox for interactive sorting column
        sort_column = st.selectbox(
            'Select column to sort by:',
            options=['Speciality', 'Provider_Count', 'Total_Charges', 'Median_Charges', 'Cumulative_Percentage'],
            index=2  # Default sorting by 'Total_Charges'
        )
        # Add a selectbox for interactive sorting order
        sort_order = st.selectbox(
            'Select sort order:',
            options=['Ascending', 'Descending'],
            index=1  # Default sorting order is 'Descending'
        )

        # Determine the ascending boolean based on sort_order selection
        ascending = True if sort_order == 'Ascending' else False

        # Sort the table based on the selected column and order
        sorted_speciality_summary = speciality_summary.sort_values(by=sort_column, ascending=ascending)

        st.dataframe(sorted_speciality_summary)
    
# Geographical Analysis
elif tab == "Maps":
    
    st.header("Maps")

    providers_by_state = df['State_Abrvtn'].value_counts().reset_index()
    providers_by_state.columns = ['State', 'Provider_Count']

    total_payment_by_state = df.groupby('State_Abrvtn')['Avg_Sbmtd_Chrg'].sum().reset_index()
    total_payment_by_state.columns = ['State', 'Total_Avg_Sbmtd_Chrg']

    median_payment_by_state = df.groupby('State_Abrvtn')['Avg_Sbmtd_Chrg'].median().reset_index()
    median_payment_by_state.columns = ['State', 'Avg_Sbmtd_Chrg']

    tot_bene_median = df.groupby('State_Abrvtn')['Tot_Bene_Day_Srvcs'].median().reset_index()
    tot_bene_median.columns = ['State', 'tot_bene_median']

    # Merge these DataFrames into a single DataFrame
    merged_df = providers_by_state.merge(total_payment_by_state, on='State').merge(median_payment_by_state, on='State').merge(tot_bene_median, on='State')

    # Load US states data directly from the URL
    url = 'https://raw.githubusercontent.com/vega/vega-datasets/master/data/us-10m.json'
    states = alt.topo_feature(url, 'states')

    # Create a dictionary to map state abbreviations to state IDs (needed for merging with topojson data)
    state_id_map = {
        'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10, 'FL': 12,
        'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18, 'IA': 19, 'KS': 20, 'KY': 21,
        'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25, 'MI': 26, 'MN': 27, 'MS': 28, 'MO': 29,
        'MT': 30, 'NE': 31, 'NV': 32, 'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37,
        'ND': 38, 'OH': 39, 'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46,
        'TN': 47, 'TX': 48, 'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55,
        'WY': 56, 'DC': 11
    }

    # Add state ID to the merged DataFrame
    merged_df['id'] = merged_df['State'].map(state_id_map)

    merged_df.rename(columns={
        'Provider_Count': 'Provider Count',
        'Total_Avg_Sbmtd_Chrg': 'Total Charges',
        'Avg_Sbmtd_Chrg': 'Median Ticket Price',
        'tot_bene_median':'Unique Services per Day'
    }, inplace=True)

    # Define the list of variables to visualize
    variable_list1 = ['Provider Count', 'Unique Services per Day']
    variable_list2 = ['Total Charges', 'Median Ticket Price']

    # Create the Altair chart
    map1 = alt.Chart(states).mark_geoshape().encode(
        alt.Color(alt.repeat('row'), type='quantitative'), 
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(merged_df, 'id', variable_list1)
    ).properties(
        width=500,
        height=300
    ).project(
        type='albersUsa'
    ).repeat(
        row=variable_list1
    ).resolve_scale(
        color='independent'
    )
    
    map2 = alt.Chart(states).mark_geoshape().encode(
        alt.Color(alt.repeat('row'), type='quantitative'), 
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(merged_df, 'id', variable_list2)
    ).properties(
        width=500,
        height=300
    ).project(
        type='albersUsa'
    ).repeat(
        row=variable_list2
    ).resolve_scale(
        color='independent'
    )


    map_col1, map_col2 = st.columns(2)
    with map_col1:
         st.altair_chart(map1, use_container_width=True)

    with map_col2:
         st.altair_chart(map2, use_container_width=True)
