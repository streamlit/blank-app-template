import streamlit as st
import joblib
import numpy as np

# Load the trained model
model = joblib.load("delivery_time_model.pkl")

# Streamlit UI
st.title("Order to Delivery Time Prediction")

st.write("Enter order details to predict estimated delivery time.")

# User Input Fields
product_category = st.selectbox("Product Category", ["Electronics", "Clothing", "Furniture", "Books"])
customer_location = st.text_input("Customer Location (e.g., City/ZIP Code)")
shipping_method = st.selectbox("Shipping Method", ["Standard", "Express", "Same-Day"])

# Convert inputs into numerical format (example encoding)
category_mapping = {"Electronics": 0, "Clothing": 1, "Furniture": 2, "Books": 3}
shipping_mapping = {"Standard": 0, "Express": 1, "Same-Day": 2}

if st.button("Predict Delivery Time"):
    # Convert categorical inputs to numerical values
    category_val = category_mapping[product_category]
    shipping_val = shipping_mapping[shipping_method]

    # Dummy input features (modify based on your model)
    input_features = np.array([[category_val, shipping_val]])

    # Make prediction
    predicted_days = model.predict(input_features)[0]

    st.success(f"Estimated delivery time: {predicted_days:.2f} days")

import streamlit as st
import joblib
import numpy as np

# Load the trained model
model = joblib.load("delivery_time_model.pkl")

# Streamlit UI
st.title("Order to Delivery Time Prediction")

st.write("Enter order details to predict estimated delivery time.")

# User Input Fields
product_category = st.selectbox("Product Category", ["Electronics", "Clothing", "Furniture", "Books"])
customer_location = st.text_input("Customer Location (e.g., City/ZIP Code)")
shipping_method = st.selectbox("Shipping Method", ["Standard", "Express", "Same-Day"])

# Convert inputs into numerical format (example encoding)
category_mapping = {"Electronics": 0, "Clothing": 1, "Furniture": 2, "Books": 3}
shipping_mapping = {"Standard": 0, "Express": 1, "Same-Day": 2}

if st.button("Predict Delivery Time"):
    # Convert categorical inputs to numerical values
    category_val = category_mapping[product_category]
    shipping_val = shipping_mapping[shipping_method]

    # Dummy input features (modify based on your model)
    input_features = np.array([[category_val, shipping_val]])

    # Make prediction
    predicted_days = model.predict(input_features)[0]

    st.success(f"Estimated delivery time: {predicted_days:.2f} days")

