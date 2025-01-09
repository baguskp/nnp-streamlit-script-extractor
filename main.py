import streamlit as st
import pandas as pd
import re
from io import StringIO

st.set_page_config(page_title = "MIKHMON SYSTEM SCRIPT TRANSLATOR By MikrotikRumahan", page_icon=":eyes:", layout = "wide")
st.title('MIKHMON SYSTEM SCRIPT TRANSLATOR By MikrotikRumahan')
st.write('Aplikasi ini digunakan untuk menerjemahkan script yang dihasilkan oleh Mikrotik Hotspot System ke dalam bentuk tabel yang lebih mudah dibaca.')
st.write('Untuk melakukan ekstraksi, silahkan upload file export script dengan format .rsc, gunakan fungsi /system/script/export file=namafile.rsc pada terminal mikrotik anda')
st.write('Tested untuk ROS 7.12.1')
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

    # Convert 'date' column to title case to match the format
    split_df['date'] = split_df['date'].str.title()

    # Convert 'date' column to datetime format with dayfirst=True
    split_df['date'] = pd.to_datetime(split_df['date'], format='%b/%d/%Y')

    # Extract month and year
    split_df['month_year'] = split_df['date'].dt.to_period('M')

    # Calculate total_jual and format it as currency
    total_jual = split_df['value'].sum()

    first_date = split_df['date'].min()
    # Get the end date (last date in the sorted 'date' column)
    end_date = split_df['date'].max()
    # Display the formatted total_jual
    st.metric(label=f"Total Jual Periode {first_date} - {end_date}",
              value=f"Rp. {total_jual:,.0f}".replace(",", "."))

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
        st.metric(label="PENDAPATAN  BERSIH", value=f"Rp. {total_jual - total_jual_true:,.0f}".replace(",", "."))

        st.subheader('DATA YANG DI UPLOAD')
        st.dataframe(split_df)

    with colb:

        st.subheader ('Total Kemungkinan Kerugian')
        st.metric(label="PENDAPATAN TERDUPLIKAT", value=f"Rp. {total_jual_true:,.0f}".replace(",", "."))

        st.subheader('ID YANG DUPLIKAT DAN DI GUNAKAN KEMBALI')
        st.dataframe(duplicated_df)