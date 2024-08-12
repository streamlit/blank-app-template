import streamlit as st
import pickle
import pandas as pd
from sklearn import datasets
from catboost import CatBoostClassifier

clf = pickle.load('best_pipeline.pkl')

st.title("🎈 College Classification App")
st.write("This application classifies universities and colleges into two classes: High - meaning those with more than 20 awards issued for every 100 fulltime students enrolled, and Low - those with les than 20 awards.")

st.sidebar.header('User Input Parameters')


def user_input_features():
    f1 = st.sidebar.slider('f1', 1.0, 70.0)
    f2 = st.sidebar.slider('f2', 1.0, 20.0)
    data = {
        'f1': f1,
        'f2': f2
    }
    features = pd.DataFrame(data, index=[0])
    return features


df = user_input_features()

st.subheader('User Input Parameters')
st.write(df)

college = datasets.load_college()
X = college.data
Y = college.target

clf = CatBoostClassifier()
clf.fit(X, Y)

prediction = clf.predict(df)
prediciton_proba = clf.predict_proba(df)

st.subheader('Class labels')
st.write(college.target_names)

st.subheader('Prediction')
st.write(college.target_names[prediction])

st.subheader('Prediction Probability')
st.write(prediction_proba)
