
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
app = Flask(__name__)
CORS(app)
# Store conversation per session (in-memory, not persistent)
user_state = {
    "stage": "start",
    "sub_stage": "",
    "data": {},
    "flow": ""
}
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/message", methods=["POST"])
def message():
    user_input = request.json.get("message", "").strip().lower()
    response = ""
    def match(input_str, keywords):
        return any(re.search(rf"\b{kw}\b", input_str, re.I) for kw in keywords)
    # START: Greeting
    if user_state["stage"] == "start":
        if match(user_input, ["hi", "hello", "hey", "hola"]):
            user_state["stage"] = "identify_customer"
            return jsonify({
                "reply": "Hi I am Brian, I am your customer relationship manager. How can I help you today? Are you an existing customer or a new customer?",
                "buttons": ["existing customer", "new customer"]
            })
        return jsonify({"reply": "Please say Hi to start the conversation with Brian."})
        # IDENTIFY CUSTOMER TYPE
    if user_state["stage"] == "identify_customer":
        if "existing" in user_input:
            user_state["stage"] = "verify_existing_dob"
            return jsonify({
                "reply": "I would need to validate your identity. Could you please provide your Date of Birth (e.g. 09/09/2000)?"
            })
        elif "new" in user_input:
            user_state["stage"] = "new_menu"
            return jsonify({
                "reply": "Welcome to Feno B2B Financial services.\nHow can I assist you today?",
                "buttons": [
                    "B2B Loans",
                    "Loan consultation",
                    "Loan restructuring",
                    "Financial Consulting"
                ]
            })
        else:
            return jsonify({
                "reply": "Please respond with 'existing customer' or 'new customer'."
            })
    # EXISTING CUSTOMER FLOW
    if user_state["stage"].startswith("verify_existing"):
        if user_state["stage"] == "verify_existing_dob":
            user_state["data"]["dob"] = user_input
            user_state["stage"] = "verify_existing_acc"
            return jsonify({"reply": "Could you provide your final 3 digits of your account number?"})
        if user_state["stage"] == "verify_existing_acc":
            user_state["data"]["acc"] = user_input
            user_state["stage"] = "verify_existing_code"
            return jsonify({"reply": "Please provide the one-time code sent to your registered email address."})
        if user_state["stage"] == "verify_existing_code":
            user_state["data"]["code"] = user_input
            user_state["stage"] = "existing_menu"
            return jsonify({
                "reply": "Great! You’re verified. How can I assist you today?",
                "buttons": [
                    "Book an appointment",
                    "Download statement",
                    "Connect to a live chat",
                    "Ticket progress",
                    "Get a new quote",
                    "Provide a Google review",
                    "Contact complaints team",
                    "New Product / Services"
                ]
            })
    # EXISTING MENU
    if user_state["stage"] == "existing_menu":
        if "book" in user_input:
            user_state["stage"] = "existing_book_reason"
            return jsonify({"reply": "Describe in brief what we will be discussing."})
        if "statement" in user_input:
            user_state["stage"] = "end"
            return jsonify({"reply": "Latest statement sent via registered email. Is there anything that I can help you with?"})
        if "live" in user_input:
            user_state["stage"] = "end"
            return jsonify({"reply": "Please click on the link sent to you via registered email. Is there anything that I can help you with?"})
        if "ticket" in user_input:
            user_state["stage"] = "end"
            return jsonify({"reply": "Status: Under approval. Is there anything that I can help you with?"})
        if "quote" in user_input:
            user_state["stage"] = "existing_book_reason"
            return jsonify({"reply": "Book an appointment."})
        if "google" in user_input:
            user_state["stage"] = "end"
            return jsonify({"reply": "Please click on the link and you will be redirected to Google reviews. Is there anything that I can help you with?"})
        if "complaint" in user_input:
            user_state["stage"] = "existing_complaint_text"
            return jsonify({"reply": "Please write your complaint in brief. A member of one of our team will contact you shortly."})
        if "product" in user_input or "service" in user_input:
            user_state["stage"] = "existing_new_product_book"
            return jsonify({"reply": "Our new services give loans to EdTech companies at 0.5% less than market rate.\nPlease book an appointment to discuss it further."})
    if user_state["stage"] == "existing_complaint_text":
        user_state["stage"] = "end"
        return jsonify({"reply": "We have created a ticket. Your ticket no is 23433. We will reach out to you shortly. Is there anything that I can help you with?"})
    if user_state["stage"] in ["existing_book_reason", "existing_new_product_book"]:
        user_state["stage"] = "existing_book_datetime"
        return jsonify({"reply": "Please give your availability - Date and Time"})
    if user_state["stage"] == "existing_book_datetime":
        user_state["stage"] = "end"
        return jsonify({"reply": "Thank You, your appointment is booked. Is there anything that I can help you with?"})
    # NEW CUSTOMER PATHS
    if user_state["stage"] == "new_menu":
        if "b2b" in user_input:
            user_state["stage"] = "new_b2b_loan"
            return jsonify({
                "reply": "We offer the following B2B loans. Please choose one:",
                "buttons": ["Secured Loans", "Unsecured Loans"]
            })
        elif "loan consultation" in user_input:
            user_state["stage"] = "new_loan_consult"
            return jsonify({
                "reply": "We offer support with the following loan consultation services:",
                "buttons": ["Business Loan Eligibility Check", "Document Review & Assistance"]
            })
        elif "financial" in user_input:
            user_state["stage"] = "new_financial_consult"
            return jsonify({
                "reply": "We offer support with the following financial consulting areas:",
                "buttons": ["Business Budgeting & Forecasting", "Tax Efficiency Strategies", "HMRC Compliance & Filing Support"]
           })
    if user_state["stage"] in ["new_b2b_loan", "new_loan_consult", "new_financial_consult"]:
        if any(keyword in user_input for keyword in ["yes", "secured", "unsecured", "document", "business", "refinance", "tax", "forecasting", "hmrc"]):
            user_state["stage"] = "new_name"
            return jsonify({"reply": "Great! To schedule a meeting could you please provide your name?"})
        if "no" in user_input:
            user_state["stage"] = "end"
            return jsonify({"reply": "Thank you for contacting Feno Financial Services."})
    if user_state["stage"] == "new_name":
        user_state["data"]["name"] = user_input
        user_state["stage"] = "new_email"
        return jsonify({"reply": "Please give us your email address."})
    elif user_state["stage"] == "new_email":
        user_state["data"]["email"] = user_input
        user_state["stage"] = "new_time"
        return jsonify({"reply": "Please give your availability - Date and Time"})
    elif user_state["stage"] == "new_time":
        user_state["data"]["datetime"] = user_input
        name = user_state["data"].get("name")
        email = user_state["data"].get("email")
        datetime_str = user_state["data"].get("datetime")
        if not all([name, email, datetime_str]):
            user_state["stage"] = "end"
            return jsonify({"reply": "⚠️ Missing details. Please ensure name, email, and datetime are all provided."})
        try:
            from calendar_event import create_google_calendar_event
            create_google_calendar_event(name, email, datetime_str)
            user_state["stage"] = "end"
            return jsonify({"reply": f"📅 Your appointment has been booked for {datetime_str}. A confirmation email will be sent to {email}."})
        except Exception as e:
            user_state["stage"] = "end"
            return jsonify({"reply": f"⚠️ Failed to book your appointment due to: {str(e)}"})
    # END STAGE
    if user_state["stage"] == "end":
        if "no" in user_input:
            return jsonify({"reply": "Thank you for contacting Feno financial service."})
        else:
            return jsonify({"reply": "Is there anything else I can help you with?"})
    return jsonify({"reply": "Sorry, I didn’t understand that. Can you rephrase?"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
