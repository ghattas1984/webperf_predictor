
# WebPerf Predictor

A Streamlit app to predict web page performance using a pre-trained ML model and GTmetrix API.

## Features
- Input a URL and get performance prediction (Excellent / Good / Unacceptable)
- Automatically fetch features using GTmetrix API

## Setup

1. Replace GTmetrix credentials in `extract_features.py`.
2. Add your trained `model.pkl` to the project directory.
3. Run the app using:

```bash
streamlit run app.py
```
