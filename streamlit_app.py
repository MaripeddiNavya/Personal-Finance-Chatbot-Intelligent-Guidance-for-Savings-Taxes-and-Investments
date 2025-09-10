# frontend/streamlit_app.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"  # Backend API endpoint

st.set_page_config(page_title="Personal Finance Chatbot", layout="centered")
st.title("💰 Personal Finance Chatbot — Demo")

# --- User Input Form ---
with st.form("finance_form"):
    st.subheader("Enter your details")
    occupation = st.selectbox("Occupation", ["Student", "Professional"])
    age = st.number_input("Age", min_value=13, max_value=120, value=22)
    income = st.number_input("Monthly Income (₹)", min_value=0.0, value=15000.0)

    st.subheader("Monthly Expenses")
    rent = st.number_input("Rent (₹)", min_value=0.0, value=4000.0)
    food = st.number_input("Food (₹)", min_value=0.0, value=2000.0)
    transport = st.number_input("Transport (₹)", min_value=0.0, value=500.0)

    source = st.selectbox("Summary Generation Source", ["hf", "ibm"])
    submitted = st.form_submit_button("Generate Summary")

# --- Helper: Local Summary Generation ---
def generate_local_summary(income, expenses):
    total_expenses = sum(expenses.values())
    savings = income - total_expenses
    summary = f"Your total monthly expenses are ₹{total_expenses:.2f}. "
    summary += f"You can save ₹{savings:.2f} per month."
    return summary

# --- Handle Form Submission ---
if submitted:
    payload = {
        "user_id": "demo_user",
        "occupation": occupation.lower(),
        "age": int(age),
        "income_monthly": float(income),
        "expenses": {
            "rent": float(rent),
            "food": float(food),
            "transport": float(transport)
        },
        "prompt_source": source,
    }

    with st.spinner("Generating summary..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            st.subheader("💡 Budget Summary")
            st.write(data.get("summary") or generate_local_summary(income, payload["expenses"]))

            st.subheader("📊 Detailed Calculations")
            st.json(data.get("details") or payload["expenses"])

        except requests.exceptions.RequestException:
            # Fallback to local summary if backend fails
            st.warning("⚠️ Backend unavailable. Showing local summary instead.")
            local_summary = generate_local_summary(income, payload["expenses"])
            st.subheader("💡 Budget Summary")
            st.write(local_summary)

            st.subheader("📊 Detailed Calculations")
            st.json(payload["expenses"])
