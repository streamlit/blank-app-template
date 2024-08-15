import streamlit as st
import pandas as pd
from pycaret.classification import load_model, predict_model

header = st.container()
dataset = st.container()
features = st.container()
model_section = st.container()

st.markdown(
    """
<style> .main {background-color: #F5F5F8;
}
</style>
""",
unsafe_allow_html=True
)

@st.cache_data
def load_data():
    return pd.read_csv('ml_dataset.csv')


with header:
    st.title("🎈 My First College Classification Web App")
    st.divider()
    st.text("This application classifies universities and colleges.")

with dataset:
    st.header('College completion dataset')
    st.text('I obtained this dataset from Kaggle')
    
    data = load_data()
    st.write(data.head())
    
with features:
    st.header('Input Features:')

    exp_award_value = st.slider("Funds per award", min_value=float(
        data['exp_award_value'].min()), max_value=float(data['exp_award_value'].max()))
    awards_per_state_value = st.slider("Awards given per State", min_value=float(
        data['awards_per_state_value'].min()), max_value=float(data['awards_per_state_value'].max()))
    grad_100_value = st.slider("Graduate within time", min_value=float(
        data['grad_100_value'].min()), max_value=float(data['grad_100_value'].max()))
    counted_pct = st.slider("Counted percent", min_value=float(
        data['counted_pct'].min()), max_value=float(data['counted_pct'].max()))
    ft_pct = st.slider("Percent of fulltime students", min_value=float(
        data['ft_pct'].min()), max_value=float(data['ft_pct'].max()))
    pell_value = st.slider("Pell grant amount", min_value=float(
        data['pell_value'].min()), max_value=float(data['pell_value'].max()))
    ft_fac_value = st.slider("Fulltime faculty contributions", min_value=float(
        data['ft_fac_value'].min()), max_value=float(data['ft_fac_value'].max()))
    grad_150_value = st.slider("Graduate within 1.5 time", min_value=float(
        data['grad_150_value'].min()), max_value=float(data['grad_150_value'].max()))
    cohort_size = st.slider("Cohort size", min_value=float(
        data['cohort_size'].min()), max_value=float(data['cohort_size'].max()))
    aid_value = st.slider("Aid value", min_value=float(
        data['aid_value'].min()), max_value=float(data['aid_value'].max()))

with model_section:
    # Load the model
    model = load_model('my_first_best_pipeline')

    st.write("After selecting the above features using the slider, press on the 'Classify' button below to determine whether it is a high- or low-award institution.")
    
    # Make a prediction
    if st.button("Classify"):
        prediction = predict_model(model, data=data)
        st.write(f"Prediction: {prediction['Label'][0]}")
    else:
        st.write("There's something wrong with the model. Please fix any errors.")


    st.subheader("Rate this App")
    st.feedback("stars")

    st.subheader("Message us:")
    prompt = st.text_input("Your message")
    if prompt:
        st.write(f"The user has sent: {prompt}")



