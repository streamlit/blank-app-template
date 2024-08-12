import streamlit as st
import pickle
import catboost
import pandas as pd
import numpy as np
import sklearn
import matplotlib
import pycaret
from pycaret.classification import *
from pycaret.classification import load_model, predict_model
import os

st.title("🎈 College Classification App")
st.divider()
st.write("This application classifies universities and colleges.")

def load_data(x):
    data = pd.read_csv('ml_dataset.csv')
    return data

# Load the model
model = load_model('my_first_best_pipeline_cboost')

def main():
    # Load dataset
    data = load_data('ml_dataset.csv')

    st.subheader("Data")
    st.write(data.head())

    # User input Features
    st.subheader("User Input Features:")

    exp_award_value = st.slider("Funds per award", min_value=float(data['exp_award_value'].min()), max_value=float(data['exp_award_value'].max()))
    awards_per_state_value = st.slider("Awards given per State", min_value=float(data['awards_per_state_value'].min()), max_value=float(data['awards_per_state_value'].max()))
    grad_100_value = st.slider("Graduate within time", min_value=float(data['grad_100_value'].min()), max_value=float(data['grad_100_value'].max()))
    counted_pct = st.slider("Counted percent", min_value=float(data['counted_pct'].min()), max_value=float(data['counted_pct'].max()))
    ft_pct = st.slider("Percent of fulltime students", min_value=float(data['ft_pct'].min()), max_value=float(data['ft_pct'].max()))
    pell_value = st.slider("Pell grant amount", min_value=float(data['pell_value'].min()), max_value=float(data['pell_value'].max()))
    ft_fac_value = st.slider("Fulltime faculty contributions", min_value=float(data['ft_fac_value'].min()), max_value=float(data['ft_fac_value'].max()))
    grad_150_value = st.slider("Graduate within 1.5 time", min_value=float(data['grad_150_value'].min()), max_value=float(data['grad_150_value'].max()))
    cohort_size = st.slider("Cohort size", min_value=float(data['cohort_size'].min()), max_value=float(data['cohort_size'].max()))
    aid_value = st.slider("Aid value", min_value=float(data['aid_value'].min()), max_value=float(data['aid_value'].max()))

    # Prepare the input data
    input_data = {'Funds per award': exp_award_value,
                  'Awards given per State': awards_per_state_value,
                  'Graduate within time': grad_100_value,
                  'Counted percent': counted_pct,
                  'Percent of fulltime students': ft_pct,
                  'Pell grant amount': pell_value,
                  'Fulltime faculty contributions': ft_fac_value,
                  'Graduate within 1.5 time': grad_150_value,
                  'Cohort size': cohort_size,
                  'Aid value': aid_value}

    input_df = pd.DataFrame([input_data])

    # Make a prediction
    if st.button("Classify"):
        prediction = model.predict_model(model, data=input_df)
        st.write(f"Prediction: {prediction['Label'][0]}")

    st.feedback("stars")

prompt = st.chat_input("Your message")
if prompt:
    st.write(f"The user has sent: {prompt}") 
   
if __name__ == "__main__":
    main()