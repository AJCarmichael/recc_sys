import os
import pandas as pd
import google.generativeai as genai
from flask import Flask, request, jsonify
import re
import google.api_core.exceptions  # Add this import

app = Flask(__name__)

# Load Gemini API Key
GEMINI_API_KEY = "AIzaSyDVJdRye4ECAFhpd2Lib7rnv-B-tRl5BPw"
genai.configure(api_key=GEMINI_API_KEY)

# Paths
SERVICES_CSV_PATH = "services.csv"

def load_services():
    """Load Union Bank's available services from CSV."""
    if not os.path.exists(SERVICES_CSV_PATH):
        return None, {"error": f"File '{SERVICES_CSV_PATH}' not found."}
    
    try:
        return pd.read_csv(SERVICES_CSV_PATH), None
    except Exception as e:
        return None, {"error": f"Error reading '{SERVICES_CSV_PATH}': {e}"}

def extract_transaction_insights(user_df):
    """Extract useful transaction details for LLM processing."""
    insights = {
        "age": int(user_df["age"].mode()[0]),  # Most common age
        "occupation": user_df["occupation"].mode()[0],  # Most common occupation
        "top_categories": list(user_df["rmt_inf_ustrd1"].value_counts().keys())[:5],  # Top 5 spending categories
        "top_merchants": list(user_df["ctpty_nm"].value_counts().keys())[:5],  # Top 5 merchants
        "average_balance": user_df["bal_aftr"].mean(),
    }
    return insights

def query_gemini(insights, services_df):
    """Use Gemini API to generate personalized recommendations."""
    prompt = f"""
    You are an AI financial advisor for Union Bank. Based on the user's data below, return ONLY the service numbers that best match the user's profile.
    
    User Details:
    - Age: {insights['age']}
    - Occupation: {insights['occupation']}
    - Top Spending Categories: {', '.join(insights['top_categories'])}
    - Frequent Merchants: {', '.join(insights['top_merchants'])}
    - Average Account Balance: {insights['average_balance']:.2f} CAD

    Union Bank Services:
    {services_df.to_string(index=False)}

    Respond ONLY with a comma-separated list of service numbers, without any explanations. Example response format: "1, 5, 9".
    """

    try:
        response = genai.GenerativeModel("gemini-2.0-flash-thinking-exp").generate_content(prompt)
        if response and response.text:
            # Extract only numbers using regex
            service_numbers = re.findall(r'\d+', response.text)
            return service_numbers
    except google.api_core.exceptions.NotFound as e:
        print(f"Model not found: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    return []

@app.route('/process', methods=['GET'])
def process_transaction():
    """Process user transactions and return only service numbers."""
    file_path = request.args.get('file_path')

    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"Transaction file '{file_path}' not found."}), 404

    services_df, error = load_services()
    if error:
        return jsonify(error), 500

    try:
        if os.path.getsize(file_path) == 0:
            raise ValueError("File is empty")
        user_df = pd.read_csv(file_path)
    except Exception as e:
        return jsonify({"error": f"Error reading '{file_path}': {e}"}), 400

    insights = extract_transaction_insights(user_df)
    recommended_services = query_gemini(insights, services_df)

    return jsonify({"recommended_services": recommended_services}), 200

if __name__ == '__main__':
    app.run(debug=True)
