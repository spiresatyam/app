
  2 from flask import Flask, request, jsonify, render_template
  3 from flask_cors import CORS
  4 import re
  5
  6 app = Flask(__name__)
  7 CORS(app)
  8
  9 # Store conversation per session (in-memory, not persistent)
 10 user_state = {
 11     "stage": "start",
 12     "sub_stage": "",
 13     "data": {},
 14     "flow": ""
 15 }
 16
 17 @app.route("/")
 18 def home():
 19     return render_template("index.html")
 20
 21
 22 @app.route("/message", methods=["POST"])
 23 def message():
 24     user_input = request.json.get("message", "").strip().lower()
 25     response = ""
 26
 27     def match(input_str, keywords):
 28         return any(re.search(rf"\b{kw}\b", input_str, re.I) for kw in keywords)
 29
 30     # START: Greeting
 31     if user_state["stage"] == "start":
 32         if match(user_input, ["hi", "hello", "hey", "hola"]):
 33             user_state["stage"] = "identify_customer"
 34             return jsonify({
 35                 "reply": "Hi I am Brian, I am your customer relationship manager. How can I help you today? Are you an existing customer or a new customer?",
 36                 "buttons": ["existing customer", "new customer"]
 37             })
 38         return jsonify({"reply": "Please say Hi to start the conversation with Brian."})
 39
 40         # IDENTIFY CUSTOMER TYPE
 41     if user_state["stage"] == "identify_customer":
 42         if "existing" in user_input:
 43             user_state["stage"] = "verify_existing_dob"
 44             return jsonify({
 45                 "reply": "I would need to validate your identity. Could you please provide your Date of Birth (e.g. 09/09/2000)?"
 46             })
 47         elif "new" in user_input:
 48             user_state["stage"] = "new_menu"
 49             return jsonify({
 50                 "reply": "Welcome to Feno B2B Financial services.\nHow can I assist you today?",
 51                 "buttons": [
 52                     "B2B Loans",
 53                     "Loan consultation",
 54                     "Loan restructuring",
 55                     "Financial Consulting"
 56                 ]
 57             })
 58         else:
 59             return jsonify({
 60                 "reply": "Please respond with 'existing customer' or 'new customer'."
 61             })
 62
 63     # EXISTING CUSTOMER FLOW
 64     if user_state["stage"].startswith("verify_existing"):
 65         if user_state["stage"] == "verify_existing_dob":
 66             user_state["data"]["dob"] = user_input
 67             user_state["stage"] = "verify_existing_acc"
 68             return jsonify({"reply": "Could you provide your final 3 digits of your account number?"})
 69
 70         if user_state["stage"] == "verify_existing_acc":
 71             user_state["data"]["acc"] = user_input
 72             user_state["stage"] = "verify_existing_code"
 73             return jsonify({"reply": "Please provide the one-time code sent to your registered email address."})
 74
 75         if user_state["stage"] == "verify_existing_code":
 76             user_state["data"]["code"] = user_input
 77             user_state["stage"] = "existing_menu"
 78             return jsonify({
 79                 "reply": "Great! You’re verified. How can I assist you today?",
 80                 "buttons": [
 81                     "Book an appointment",
 82                     "Download statement",
 83                     "Connect to a live chat",
 84                     "Ticket progress",
 85                     "Get a new quote",
 86                     "Provide a Google review",
 87                     "Contact complaints team",
 88                     "New Product / Services"
 89                 ]
 90             })
 91
 92     # EXISTING MENU
 93     if user_state["stage"] == "existing_menu":
 94         if "book" in user_input:
 95             user_state["stage"] = "existing_book_reason"
 96             return jsonify({"reply": "Describe in brief what we will be discussing."})
 97         if "statement" in user_input:
 98             user_state["stage"] = "end"
 99             return jsonify({"reply": "Latest statement sent via registered email. Is there anything that I can help you with?"})
100         if "live" in user_input:
101             user_state["stage"] = "end"
102             return jsonify({"reply": "Please click on the link sent to you via registered email. Is there anything that I can help you with?"})
103         if "ticket" in user_input:
104             user_state["stage"] = "end"
105             return jsonify({"reply": "Status: Under approval. Is there anything that I can help you with?"})
106         if "quote" in user_input:
107             user_state["stage"] = "existing_book_reason"
108             return jsonify({"reply": "Book an appointment."})
109         if "google" in user_input:
110             user_state["stage"] = "end"
111             return jsonify({"reply": "Please click on the link and you will be redirected to Google reviews. Is there anything that I can help you with?"})
112         if "complaint" in user_input:
113             user_state["stage"] = "existing_complaint_text"
114             return jsonify({"reply": "Please write your complaint in brief. A member of one of our team will contact you shortly."})
115         if "product" in user_input or "service" in user_input:
116             user_state["stage"] = "existing_new_product_book"
117             return jsonify({"reply": "Our new services give loans to EdTech companies at 0.5% less than market rate.\nPlease book an appointment to discuss it further."})
118
119     if user_state["stage"] == "existing_complaint_text":
120         user_state["stage"] = "end"
121         return jsonify({"reply": "We have created a ticket. Your ticket no is 23433. We will reach out to you shortly. Is there anything that I can help you with?"})
122
123     if user_state["stage"] in ["existing_book_reason", "existing_new_product_book"]:
124         user_state["stage"] = "existing_book_datetime"
125         return jsonify({"reply": "Please give your availability - Date and Time"})
126
127     if user_state["stage"] == "existing_book_datetime":
128         user_state["stage"] = "end"
129         return jsonify({"reply": "Thank You, your appointment is booked. Is there anything that I can help you with?"})
130     # NEW CUSTOMER PATHS
131     if user_state["stage"] == "new_menu":
132         if "b2b" in user_input:
133             user_state["stage"] = "new_b2b_loan"
134             return jsonify({
135                 "reply": "We offer the following B2B loans. Please choose one:",
136                 "buttons": ["Secured Loans", "Unsecured Loans"]
137             })
138
139         elif "loan consultation" in user_input:
140             user_state["stage"] = "new_loan_consult"
141             return jsonify({
142                 "reply": "We offer support with the following loan consultation services:",
143                 "buttons": ["Business Loan Eligibility Check", "Document Review & Assistance"]
144             })
145
146         elif "financial" in user_input:
147             user_state["stage"] = "new_financial_consult"
148             return jsonify({
149                 "reply": "We offer support with the following financial consulting areas:",
150                 "buttons": ["Business Budgeting & Forecasting", "Tax Efficiency Strategies", "HMRC Compliance & Filing Support"]
151            })
152
153     if user_state["stage"] in ["new_b2b_loan", "new_loan_consult", "new_financial_consult"]:
154         if any(keyword in user_input for keyword in ["yes", "secured", "unsecured", "document", "business", "refinance", "tax", "forecasting", "hmrc"]):
155             user_state["stage"] = "new_name"
156             return jsonify({"reply": "We can book an appointment to discuss it further. Would you like to proceed?"})
157         if "no" in user_input:
158             user_state["stage"] = "end"
159             return jsonify({"reply": "Thank you for contacting Feno Financial Services."})
160
161     if user_state["stage"] == "new_name":
162         user_state["data"]["name"] = user_input
163         user_state["stage"] = "new_email"
164         return jsonify({"reply": "Please give us your email address."})
165
166     elif user_state["stage"] == "new_email":
167         user_state["data"]["email"] = user_input
168         user_state["stage"] = "new_time"
169         return jsonify({"reply": "Please give your availability - Date and Time"})
170
171     elif user_state["stage"] == "new_time":
172         user_state["data"]["datetime"] = user_input
173
174         name = user_state["data"].get("name")
175         email = user_state["data"].get("email")
176         datetime_str = user_state["data"].get("datetime")
177
178         if not all([name, email, datetime_str]):
179             user_state["stage"] = "end"
180             return jsonify({"reply": "⚠️ Missing details. Please ensure name, email, and datetime are all provided."})
181
182         try:
183             from calendar_event import create_google_calendar_event
184             create_google_calendar_event(name, email, datetime_str)
185             user_state["stage"] = "end"
186             return jsonify({"reply": f"📅 Your appointment has been booked for {datetime_str}. A confirmation email will be sent to {email}."})
187         except Exception as e:
188             user_state["stage"] = "end"
189             return jsonify({"reply": f"⚠️ Failed to book your appointment due to: {str(e)}"})
190
191     # Continue booking flow
192     if user_state["stage"] == "new_name":
193         user_state["stage"] = "new_email"
194         return jsonify({"reply": "Please give us your name."})
195
196     if user_state["stage"] == "new_email":
197        user_state["stage"] = "new_time"
198        return jsonify({"reply": "Please give us your email address."})
199
200     if user_state["stage"] == "new_time":
201        user_state["stage"] = "end"
202        return jsonify({"reply": "Please give your availability - Date and Time"})
203
204     # END STAGE
205     if user_state["stage"] == "end":
206         if "no" in user_input:
207             return jsonify({"reply": "Thank you for contacting Feno financial service."})
208         else:
209             return jsonify({"reply": "Is there anything else I can help you with?"})
210
211     return jsonify({"reply": "Sorry, I didn’t understand that. Can you rephrase?"})
212
213
214 if __name__ == "__main__":
215     app.run(host="0.0.0.0", port=5000)
216
