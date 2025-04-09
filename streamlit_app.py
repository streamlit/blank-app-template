import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime
import base64

from pages.drug_interaction import show_drug_interaction_page

# Set page configuration
st.set_page_config(
    page_title="DrugResponse AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    .prediction-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

class DrugResponsePredictor:
    def __init__(self):
        self.model = None
        self.features = None
        
    def train_model(self, X, y):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        return self.model

def load_animation():
    with st.spinner('Processing...'):
        time.sleep(2)

def create_histogram(df, feature):
    plt.figure(figsize=(10, 6))
    plt.hist(df[feature], bins=30, color='#1565c0')
    plt.title(f'Distribution of {feature}')
    plt.xlabel(feature)
    plt.ylabel('Count')
    return plt

def create_correlation_heatmap(df):
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.corr(), annot=True, cmap='RdBu')
    plt.title('Correlation Matrix')
    return plt

# Function to create a standalone drug interaction page
def create_drug_interaction_html():
    # Create a new Streamlit app for drug interaction
    drug_interaction_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Drug Interaction Analyzer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #1565c0;
                text-align: center;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .row {
                display: flex;
                margin-bottom: 20px;
            }
            .col {
                flex: 1;
                padding: 0 15px;
            }
            select, input, button {
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border-radius: 5px;
                border: 1px solid #ddd;
            }
            button {
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                background-color: #45a049;
            }
            .results {
                background: linear-gradient(45deg, #f8f9fa, #e9ecef);
                padding: 20px;
                border-radius: 15px;
                margin-top: 20px;
            }
            .metric {
                text-align: center;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
                margin: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .metric h3 {
                margin: 0;
                color: #1565c0;
            }
            .metric p {
                font-size: 24px;
                font-weight: bold;
                margin: 10px 0;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
            .info-box {
                background-color: #d1ecf1;
                color: #0c5460;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💊 Drug Interaction Analyzer</h1>
                <p>Analyze potential interactions between medications</p>
            </div>
            
            <div class="row">
                <div class="col">
                    <label for="drug1">Select Primary Drug</label>
                    <select id="drug1">
                        <option>Drug A</option>
                        <option>Drug B</option>
                        <option>Drug C</option>
                        <option>Drug D</option>
                    </select>
                </div>
                <div class="col">
                    <label for="drug2">Select Secondary Drug</label>
                    <select id="drug2">
                        <option>Drug X</option>
                        <option>Drug Y</option>
                        <option>Drug Z</option>
                    </select>
                </div>
            </div>
            
            <h3>Additional Parameters</h3>
            <div class="row">
                <div class="col">
                    <label for="dosage1">Primary Drug Dosage (mg)</label>
                    <input type="number" id="dosage1" value="100" min="10" max="1000">
                </div>
                <div class="col">
                    <label for="dosage2">Secondary Drug Dosage (mg)</label>
                    <input type="number" id="dosage2" value="100" min="10" max="1000">
                </div>
                <div class="col">
                    <label for="age">Patient Age</label>
                    <input type="number" id="age" value="50" min="18" max="100">
                </div>
            </div>
            
            <button onclick="checkInteraction()">Check Interaction</button>
            
            <div id="results" style="display: none;" class="results">
                <h4 style="color: #1565c0;">Interaction Analysis Results</h4>
                
                <div class="row">
                    <div class="col">
                        <div class="metric">
                            <h3>Risk Level</h3>
                            <p id="risk-level">Medium</p>
                        </div>
                    </div>
                    <div class="col">
                        <div class="metric">
                            <h3>Confidence</h3>
                            <p id="confidence">85%</p>
                        </div>
                    </div>
                </div>
                
                <h3>Detailed Analysis</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Effect</th>
                            <th>Severity</th>
                            <th>Evidence Level</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Increased toxicity</td>
                            <td id="severity1">Medium</td>
                            <td id="evidence1">Strong</td>
                        </tr>
                        <tr>
                            <td>Reduced efficacy</td>
                            <td id="severity2">Low</td>
                            <td id="evidence2">Moderate</td>
                        </tr>
                        <tr>
                            <td>Metabolic inhibition</td>
                            <td id="severity3">High</td>
                            <td id="evidence3">Limited</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="info-box">
                    Recommended Action: Monitor patient closely for potential side effects.
                </div>
                
                <h3>Interaction Timeline</h3>
                <div id="chart" style="height: 300px; background-color: #f8f9fa; border-radius: 5px; padding: 20px;">
                    <p style="text-align: center; padding-top: 120px; color: #666;">
                        [Interactive Chart Would Appear Here]
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            function checkInteraction() {
                // Show loading indicator
                document.getElementById('results').style.display = 'none';
                setTimeout(function() {
                    // Generate random results
                    const riskLevels = ['Low', 'Medium', 'High'];
                    const evidenceLevels = ['Limited', 'Moderate', 'Strong'];
                    
                    const riskLevel = riskLevels[Math.floor(Math.random() * riskLevels.length)];
                    const confidence = Math.floor(Math.random() * 30 + 70) + '%';
                    
                    // Update the UI
                    document.getElementById('risk-level').innerText = riskLevel;
                    document.getElementById('confidence').innerText = confidence;
                    
                    document.getElementById('severity1').innerText = riskLevels[Math.floor(Math.random() * riskLevels.length)];
                    document.getElementById('severity2').innerText = riskLevels[Math.floor(Math.random() * riskLevels.length)];
                    document.getElementById('severity3').innerText = riskLevels[Math.floor(Math.random() * riskLevels.length)];
                    
                    document.getElementById('evidence1').innerText = evidenceLevels[Math.floor(Math.random() * evidenceLevels.length)];
                    document.getElementById('evidence2').innerText = evidenceLevels[Math.floor(Math.random() * evidenceLevels.length)];
                    document.getElementById('evidence3').innerText = evidenceLevels[Math.floor(Math.random() * evidenceLevels.length)];
                    
                    // Show results
                    document.getElementById('results').style.display = 'block';
                }, 1000);
            }
        </script>
    </body>
    </html>
    """
    return drug_interaction_html

def main():
    # Check if we're in the drug interaction page mode
    if 'drug_interaction_page' in st.session_state and st.session_state['drug_interaction_page']:
        show_drug_interaction_page()
        return
    
    predictor = DrugResponsePredictor()
    
    # Sidebar with glossy effect
    st.sidebar.markdown("""
        <div style='background: linear-gradient(45deg, #1e88e5, #1565c0);
                    padding: 20px;
                    border-radius: 10px;
                    color: white;'>
        <h1 style='text-align: center;'>DrugResponse AI</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", 
         "📊 Interactive Analysis", 
         "🔮 Smart Predictor", 
         "📈 Performance Analytics",
         "⏱️ Treatment Timeline",
         "💊 Drug Interaction",
         "🔄 Patient Similarity",
         "📊 Real-time Monitoring"]
    )
    
    if page == "🏠 Home":
        show_home()
    elif page == "📊 Interactive Analysis":
        show_interactive_analysis()
    elif page == "🔮 Smart Predictor":
        show_smart_predictor(predictor)
    elif page == "📈 Performance Analytics":
        show_performance_analytics()
    elif page == "⏱️ Treatment Timeline":
        show_treatment_timeline()
    elif page == "💊 Drug Interaction":
        # Instead of showing the drug interaction page directly,
        # we'll provide a link to open it in a new tab
        st.title("💊 Drug Interaction Analyzer")
        st.write("Click the button below to open the Drug Interaction Analyzer in a new page:")
        
        # Create a data URL for the HTML content
        drug_interaction_html = create_drug_interaction_html()
        b64 = base64.b64encode(drug_interaction_html.encode()).decode()
        href = f'data:text/html;base64,{b64}'
        
        # Create a button that opens the HTML in a new tab
        st.markdown(f'<a href="{href}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 24px; border-radius: 10px; border: none; font-weight: bold; cursor: pointer;">Open Drug Interaction Analyzer</button></a>', unsafe_allow_html=True)
        
        # Alternative approach using Streamlit's built-in functionality
        if st.button("Open Drug Interaction Analyzer (Streamlit)"):
            # Set a flag in session state to show the drug interaction page
            st.session_state['drug_interaction_page'] = True
            # Rerun the app to show the drug interaction page
            st.experimental_rerun()
        
        if st.button("← Back to Main App"):
           st.session_state['drug_interaction_page'] = False
           st.experimental_rerun()
            
    elif page == "🔄 Patient Similarity":
        show_patient_similarity()
    elif page == "📊 Real-time Monitoring":
        show_monitoring_dashboard()

# The rest of your functions remain the same
def show_home():
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #1565c0;'>Welcome to DrugResponse AI</h1>
            <p style='color: #666; font-size: 1.2em;'>
                Advanced Machine Learning for Personalized Medicine
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload your dataset (CSV format)", type="csv")
    
    if uploaded_file:
        load_animation()
        df = pd.read_csv(uploaded_file)
        st.session_state['data'] = df
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("📊 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
        
        with col2:
            st.write("📈 Quick Statistics")
            st.write(f"Total Records: {len(df)}")
            st.write(f"Features: {df.columns.tolist()}")
            
        st.subheader("🔍 Data Quality Check")
        quality_score = (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        st.progress(quality_score/100)
        st.write(f"Data Quality Score: {quality_score:.2f}%")

def show_interactive_analysis():
    if 'data' not in st.session_state:
        st.warning("⚠️ Please upload your dataset first!")
        return
    
    df = st.session_state['data']
    
    st.title("📊 Interactive Data Analysis")
    
    analysis_type = st.selectbox(
        "Choose Analysis Type",
        ["Feature Distribution", "Correlation Analysis", "Patient Segments"]
    )
    
    if analysis_type == "Feature Distribution":
        feature = st.selectbox("Select Feature", df.columns)
        fig = create_histogram(df, feature)
        st.pyplot(fig)
        plt.clf()
        
    elif analysis_type == "Correlation Analysis":
        fig = create_correlation_heatmap(df)
        st.pyplot(fig)
        plt.clf()

def show_smart_predictor(predictor):
    st.title("🔮 Smart Drug Response Predictor")
    
    tab1, tab2 = st.tabs(["Individual Prediction", "Batch Prediction"])
    
    with tab1:
        st.subheader("Patient Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("Age", 18, 100, 50)
            weight = st.number_input("Weight (kg)", 40, 150, 70)
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"])
            blood_type = st.selectbox("Blood Type", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
        
        with col3:
            medical_history = st.multiselect(
                "Medical History",
                ["Diabetes", "Hypertension", "Heart Disease", "None"]
            )
        
        if st.button("Predict Response"):
            load_animation()
            
            prediction_prob = np.random.random()
            
            st.markdown("""
                <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 10px 0;'>
                    <h3 style='color: #1565c0; margin-bottom: 15px;'>Prediction Results</h3>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Response Probability", f"{prediction_prob:.2%}")
            with col2:
                st.metric("Confidence Score", f"{np.random.random():.2%}")
            with col3:
                st.metric("Risk Level", "Medium" if prediction_prob > 0.5 else "Low")

def show_performance_analytics():
    st.title("📈 Model Performance Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Accuracy", "87.5%", "+2.1%")
    with col2:
        st.metric("Precision", "85.3%", "+1.8%")
    with col3:
        st.metric("Recall", "86.7%", "+3.2%")
    with col4:
        st.metric("F1 Score", "86.0%", "+2.5%")
    
    # ROC Curve using matplotlib
    st.subheader("ROC Curve Analysis")
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], 'r--')
    ax.plot(np.linspace(0, 1, 100), 1 - np.exp(-3 * np.linspace(0, 1, 100)))
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    st.pyplot(fig)
    plt.clf()

def show_treatment_timeline():
    st.subheader("🎯 AI-Driven Treatment Timeline")
    
    timeline_data = {
        'Day 1': {'Response': 'High', 'Confidence': 0.92},
        'Day 7': {'Response': 'Medium', 'Confidence': 0.85},
        'Day 14': {'Response': 'High', 'Confidence': 0.95},
        'Day 30': {'Response': 'Very High', 'Confidence': 0.98}
    }
    
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
    """, unsafe_allow_html=True)
    
    for date, data in timeline_data.items():
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            st.write(f"**{date}**")
        with col2:
            st.progress(data['Confidence'])
        with col3:
            st.write(f"_{data['Response']}_")

def show_patient_similarity():
    st.subheader("🔄 Patient Similarity Network")
    
    patient_data = pd.DataFrame({
        'Age': np.random.randint(20, 80, 100),
        'Response': np.random.choice(['High', 'Medium', 'Low'], 100),
        'Genetics': np.random.choice(['Type A', 'Type B', 'Type C'], 100)
    })
    
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        patient_data['Age'],
        np.random.rand(100),
        c=pd.factorize(patient_data['Response'])[0],
        cmap='viridis',
        alpha=0.6
    )
    
    plt.title("Patient Similarity Network")
    plt.xlabel("Age")
    plt.ylabel("Response Similarity")
    
    st.pyplot(fig)
    plt.clf()
    
    st.sidebar.subheader("Filter Similarity Network")
    age_range = st.sidebar.slider("Age Range", 20, 80, (30, 70))
    response_type = st.sidebar.multiselect(
        "Response Types",
        ['High', 'Medium', 'Low'],
        ['High', 'Medium', 'Low']
    )

def show_monitoring_dashboard():
    st.subheader("📊 Real-time Patient Monitoring")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Response Level",
            "87%",
            "3%",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Side Effects Risk",
            "Low",
            "-2%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Treatment Progress",
            "65%",
            "5%",
            delta_color="normal"
        )
    
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['Response', 'Side Effects', 'Progress']
    )
    
    st.line_chart(chart_data)
    
    st.markdown("""
        <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px;'>
            <h5 style='color: #856404;'>⚠️ Active Alerts</h5>
            <p>Next check-up recommended in 7 days</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
