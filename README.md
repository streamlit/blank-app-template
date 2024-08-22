# My First Streamlit Web App
- The following are the lines of code used to develop my first web Application for classifying higher education institutions to either high or low class as per the number of awards issued to fulltime undergraduate students.
## Requirements:
- import streamlit as st
- import pandas as pd
- from pycaret.classification import load_model, predict_model
- import numpy as np

## Created Containers
- header = st.container()
- dataset = st.container()
- features = st.container()
- footer = st.container()

## Selected Background color for the Web App
st.markdown(
    """
<style> .main {background-color: #F5F5F8;
}
</style>
""",
    unsafe_allow_html=True
)

## Defined a Function for Storing Data
@st.cache_data
def load_data():
    return pd.read_csv('ml_dataset.csv')

### Title and Description of the App
with header:
    st.title("🎈 College Classification Web App")
    st.divider()
    st.write("This application classifies universities and colleges into two classes: 'High class' - meaning the university offers a high number of awards for every 100-fulltime students, and 'Low class' - for institutions offering small number of awards for every 100-fulltime students.")

## Dataset:
with dataset:
    st.header('College completion dataset')
    st.write(
        'I obtained this dataset from Kaggle. Credit to Jonathan Ortiz (https://data.world/databeats).')

    data = load_data()
    st.write(data.head())

    st.subheader('Funds spent per award')
    chart_data = pd.DataFrame(np.random.randn(20, 4), columns=['exp_award_value', 'ft_pct',
                                                               'grad_100_value', 'cohort_size'])
    st.bar_chart(chart_data)
## Features:
with features:
    st.header('Input Features:')

    features = data.columns.tolist()
    selected_features = st.multiselect(
        'Select features for analysis:', features, default=features)

    if selected_features:
        filtered_data = data.copy()
        for feature in selected_features:
            min_value, max_value = data[feature].min(), data[feature].max()
            st.sidebar.write(f"Adjust the range for {feature}:")
            min_slider, max_slider = st.sidebar.slider(
                f'{feature} Range',
                min_value=float(min_value),
                max_value=float(max_value),
                value=(float(min_value), float(max_value)
                       ))
            # Filter the dataframe based on slider values
            filtered_data = filtered_data[(filtered_data[feature] >= min_slider) & (
                filtered_data[feature] <= max_slider)]
### Loading a Trained Model
        model = load_model('my_first_best_pipeline')
### Making Predictions
        # Make prediction
        if st.button("Classify"):
            prediction = predict_model(model, data=filtered_data)
            # prediction_label = prediction.get('Label', 'Label key not found')
            st.write(prediction)

### User Experience Forum
with footer:
    # User rating feature
    st.subheader("Rate this App")
    st.feedback("stars")

    # User chat feature
    st.subheader("Message us:")
    prompt = st.text_input("Your message")
    if prompt:
        st.write(f"The user has sent: {prompt}")
