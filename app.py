import streamlit as st
import requests
import json
import pandas as pd

import streamlit as st

st.set_page_config(
    page_title="Rossmann Sales",
    page_icon="💊",
    layout="centered",
    initial_sidebar_state="expanded",
)

def sidebar():
    # logo image
    st.sidebar.image("img/rossmann_logo.png", width = None)

    # create the sidebar
    st.sidebar.title("Forecast Filters")

    # sliders
    value_store = st.sidebar.slider("ID Store:", min_value=1, max_value=1200, value=(0, 1200), step=1, help="Number of the Stores")
    value_store = range(value_store[0], value_store[1] + 1)

    sales_value = st.sidebar.slider( label="Sales:",min_value=0, max_value=1000000, value=500000, step=50000, help="Threshold of Sales")

    budget_value = st.sidebar.slider( label="Budget:",min_value=0, max_value=100, value=20, step=5, help="Percentage of the Budget")



    return value_store, budget_value, sales_value

def convert_df(df):
   return df.to_csv(index=False, sep=';').encode('utf-8')

def load_dataset(value_store):
    # loading test dataset
    df10 = pd.read_csv('/home/tiagobarreto/DS/repos/DS_em_producao/data/test.csv')
    df_store_raw = pd.read_csv('/home/tiagobarreto/DS/repos/DS_em_producao/data/store.csv', low_memory = False)

    # merge test dataset + store
    df_test  = pd.merge(df10, df_store_raw, how='left', on='Store')
    

    # choose store for prediction
    df_test = df_test[df_test['Store'].isin(value_store)]

    # remove closed days
    df_test = df_test[df_test['Open'] != 0]
    df_test = df_test[~df_test['Open'].isnull()]
    df_test = df_test.drop('Id', axis = 1)

    return df_test

def modify_dataset(response, slider_value, sales_value):
    # json to dataframe
    prediction_data = response.json()
    prediction_df = pd.DataFrame(prediction_data, columns=prediction_data[0].keys()).reset_index(drop = True)
    # creating budget column
    budget = slider_value * 0.01
    prediction_df['budget'] = prediction_df['prediction'] * budget 
    prediction_df['budget'] = prediction_df['budget'].astype(int)
    # filgering
    prediction_df = prediction_df.loc[prediction_df['prediction'] < sales_value, :]
    
    return prediction_df

def main():
    # Title
    st.title("Rossmann Sales Forecast")

    # Creating Sidebar
    value_store, budget_value, sales_value = sidebar()
    df_test = load_dataset(value_store)

    # Converta o DataFrame em JSON
    data = json.dumps(df_test.to_dict(orient='records'))

    # URL da sua API Rossman
    url = 'https://rossmann-api-hfjk.onrender.com/rossmann/predict'
    headers = {'Content-type': 'application/json'}

    # Botão para fazer a solicitação

    if st.button("Predict"):
        # post API
        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 200:
            # modify Dataset
            prediction_df = modify_dataset(response, budget_value, sales_value)

            # print Prediction
            st.dataframe(prediction_df, use_container_width= True)

            # convert the dataframe to csv
            csv = convert_df(prediction_df)
            st.download_button("Download CSV", csv, "rossmann_sales.csv","text/csv",key='download-csv')
                    
        else:
            st.error("Error")
if __name__ == "__main__":
    main()
