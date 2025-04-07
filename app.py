import streamlit as st
from extract_features import extract_features_from_url, get_recommendations
import joblib
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os
import pandas as pd
import time

model = joblib.load("svm_model (3).pkl")

st.set_page_config(page_title="WebPulse AI", page_icon="🌐")
#st.title("🌐 WebPulse AI — Smart Website Performance Predictor")


st.markdown("""
<h1 style='font-size: 32px;'>🌐 WebPulse AI — <span style='font-size: 20px;'>Smart Website Performance Predictor</span></h1>
""", unsafe_allow_html=True)



st.caption("Developed by PhD Candidate Mohammad Ghattas")


st.markdown("""

📌 **Important Note**

This application is part of a scientific research project that uses machine learning to evaluate website performance.  
It extracts 10 real-world features from web pages without relying on any third-party APIs.  
The model was trained on a balanced dataset and aims to provide accurate predictions to support web performance optimization.



""")

url = st.text_input("Enter Website URL:", placeholder="e.g. https://www.example.com")


if st.button("Analyze") and url:
    start_time = time.time()
    with st.spinner("Analyzing the website, please wait..."):
        features = extract_features_from_url(url)
    elapsed_time = round(time.time() - start_time, 2)

    feature_names = [
        "Response Time (s)", "Load Time (s)", "Page Size (MB)", "Broken Links",
        "Number of Requests", "Start Render Time (s)", "Time to Interactive (s)",
        "HTML Validation Errors", "Compression (KB)", "Document Complete Time (s)"
    ]
    feature_dict = dict(zip(feature_names, features))

    if all(v == 0 for v in features):
        st.error("❌ Analysis failed or timed out. Please try again later or with another URL.")
    else:
        prediction = model.predict([features])[0]
        performance_levels = {
            "Excellent": "✅ Excellent",
            "Good": "⚠️ Good",
            "Unacceptable": "❌ Unacceptable"
        }
        performance_label = performance_levels.get(prediction, "Unknown")

        st.subheader("🔆 Predicted Performance")
        st.success(f"Predicted Website Performance: {performance_label}")
        st.info(f"🕒 Analysis Duration: {elapsed_time} seconds")

        st.subheader("🔍 Extracted Features")
        df_features = pd.DataFrame.from_dict(feature_dict, orient='index', columns=['Value'])
        st.table(df_features)

        recommendations = get_recommendations(features)
        if recommendations:
            st.subheader("💡 Recommendations for Improvement")
            for tip in recommendations:
                st.warning(tip)

        st.subheader("📊 Feature Analysis")
        fig, ax = plt.subplots()
        ax.barh(list(feature_dict.keys()), list(feature_dict.values()), color='skyblue')
        ax.set_xlabel("Value")
        ax.set_title("Feature Analysis")
        st.pyplot(fig)

        st.subheader("")
        if st.button("📄 Download PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(0, 10, "Website Performance Evaluation Report", ln=True, align='C')

            pdf.set_font("Arial", "", 12)
            pdf.ln(10)
            pdf.cell(0, 10, f"URL: {url}", ln=True)
            pdf.cell(0, 10, f"Predicted Performance: {performance_label}", ln=True)
            pdf.cell(0, 10, f"Analysis Duration: {elapsed_time} seconds", ln=True)

            pdf.ln(5)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Extracted Features:", ln=True)
            pdf.set_font("Arial", "", 12)
            for k, v in feature_dict.items():
                pdf.cell(0, 10, f"{k}: {v}", ln=True)

            if recommendations:
                pdf.ln(5)
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "Recommendations:", ln=True)
                pdf.set_font("Arial", "", 12)
                for tip in recommendations:
                    pdf.multi_cell(0, 10, f"- {tip}")

            chart_path = os.path.join(tempfile.gettempdir(), "chart.png")
            fig.savefig(chart_path)
            pdf.image(chart_path, x=10, y=pdf.get_y() + 10, w=180)

            pdf_path = os.path.join(tempfile.gettempdir(), "report.pdf")
            pdf.output(pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download PDF Report", f, file_name="performance_report.pdf")
