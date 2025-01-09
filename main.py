import streamlit as st
import pandas as pd
import re
from io import StringIO



st.set_page_config(layout="wide")
st.title('Script Translator')

# Read the file content

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:

    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    data = stringio.read()

    # Extract owner and name using regular expressions
    pattern = re.compile(r'name="([^"]+)" owner=([^ ]+)')
    matches = pattern.findall(data)

    # Create a list of dictionaries
    data_list = [{'owner': match[1], 'name': match[0]} for match in matches]

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data_list)

    # Replace '-|-' with '|'
    df['name'] = df['name'].str.replace('-|-', '|')

    # Split the 'name' column by the new separator '|'
    split_df = df['name'].str.split('|', expand=True)

    # Assign column names to the new DataFrame
    split_df.columns = ['date', 'time', 'id', 'value', 'ip', 'mac', 'duration', 'code', 'status']
    split_df['id'] = split_df['id'].str.replace(' ', '').str.replace('-', '').str.replace('\\', '')
    split_df['status']=split_df['status'].str.replace(' ', '')
    split_df['time'] = split_df['time'].str.replace('-', '')
    split_df['value'] = split_df['value'].astype(int)

    # Convert 'date' column to datetime format
    split_df['date'] = pd.to_datetime(split_df['date'], format='%b/%d/%Y')
    # Extract month and year
    split_df['month_year'] = split_df['date'].dt.to_period('M')

    # Calculate total_jual and format it as currency
    total_jual = split_df['value'].sum()
    # total_jual_formatted = locale.currency(total_jual, grouping=True)

    # Display the formatted total_jual
    st.metric(label="Total Jual", value=total_jual)

    # Group by 'month_year' and sum the 'value' column
    grouped_df = split_df.groupby('month_year')['value'].sum().reset_index()
    # Identify duplicated 'id' values
    duplicated_ids = split_df[split_df['id'].duplicated(keep=False)]
    # Create a new DataFrame with the duplicated 'id' values
    duplicated_df = duplicated_ids.copy()

    st.subheader('PENDAPATAN PER BULAN Rp.')
    st.dataframe(grouped_df)

    cola, colb = st.columns(2)
    with cola:

        st.subheader('DATA YANG DI UPLOAD')
        total_jual_true = split_df[split_df['id'].duplicated(keep=False)].groupby('month_year')['value'].sum().sum()
        st.metric(label="PENDAPATAN  BERSIH", value=total_jual-total_jual_true)

        st.subheader('DATA YANG DI UPLOAD')
        st.dataframe(split_df)

    with colb:

        st.subheader ('Total Kemungkinan Kerugian')
        st.metric(label="PENDAPATAN TERDUPLIKAT", value=total_jual_true)

        st.subheader('ID YANG DUPLIKAT DAN DI GUNAKAN KEMBALI')
        st.dataframe(duplicated_df)