#  FAKE SECRET FOR DEMO
# API_SECRET = "sk_test_12345_abcde"

import streamlit as st
import json
import io
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Email Sending ---
def send_email(to_email, subject, body):
    from_email = st.secrets["EMAIL_ADDRESS"]
    password = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_email, password)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# --- Groq Summary + Response ---
def generate_summary_and_response(complaint_text):
    prompt = f"""You are a helpful customer support assistant. Given the following customer complaint, first provide a concise summary, and then write a professional, empathetic, and actionable response.

Complaint:
{complaint_text}

Summary:"""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful and empathetic customer support assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        try:
            content = result["choices"][0]["message"]["content"].strip()
            try:
                summary, response_text = content.split("Response:")
            except ValueError:
                summary = "Could not extract summary."
                response_text = content
            return summary.strip(), response_text.strip()
        except Exception as e:
            raise Exception(f"Failed to parse response: {e}")
    else:
        raise Exception(f"Groq API error: {response.status_code} - {response.text}")

# --- Regenerate Response Only ---
def regenerate_response(ticket_text, summary):
    prompt = f"""You are a helpful customer support assistant. Based on the following customer complaint and its summary, write a professional, empathetic, and actionable response. Be concise, polite, and helpful.

Complaint:
{ticket_text}

Summary:
{summary}

Response:"""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a helpful and empathetic customer support assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        try:
            return result["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            raise Exception("Unexpected response format from Groq API.")
    else:
        raise Exception(f"Groq API error: {response.status_code} - {response.text}")

# --- Load & Save ---
def load_tickets(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tickets(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- App State ---
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = {}

# --- Load Data ---
st.title("🛠️ Customer Support Dashboard")
tickets = load_tickets("sample_tickets.json")

# --- Display Tickets ---
for i, ticket in enumerate(tickets):
    with st.expander(f"📨 Ticket #{i+1}"):
        st.markdown("**🗣️ Complaint:**")
        st.write(ticket['ticket'])

        st.markdown("**🧾 Summary:**")
        st.write(ticket['summary'])

        st.markdown("**✉️ Drafted Response:**")
        st.write(ticket['ideal_response'])

        status = ticket.get("status", "Pending")
        if status == "Sent":
            st.success("✅ Sent")
        else:
            st.warning("🕒 Pending")

        st.caption(f"🕒 Submitted: {ticket.get('timestamp', 'N/A')}")

        if st.session_state.edit_mode.get(i, False):
            edited_text = st.text_area("Edit Response", ticket['ideal_response'], key=f"edit_box_{i}")
            if st.button("✅ Save", key=f"save_{i}"):
                ticket['ideal_response'] = edited_text
                st.session_state.edit_mode[i] = False
                save_tickets("sample_tickets.json", tickets)
                st.success("Response updated and saved!")

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏️ Edit", key=f"edit_{i}"):
                st.session_state.edit_mode[i] = True
        with col2:
            if st.button("🔄 Regenerate", key=f"regen_{i}"):
                with st.spinner("Regenerating response..."):
                    try:
                        new_response = regenerate_response(ticket['ticket'], ticket['summary'])
                        ticket['ideal_response'] = new_response
                        save_tickets("sample_tickets.json", tickets)
                        st.success("Response regenerated and saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to regenerate: {e}")
        with col3:
            with st.form(key=f"send_form_{i}"):
                to_email = st.text_input("Recipient Email", value="support@example.com", key=f"email_{i}")
                submitted = st.form_submit_button("📤 Send")
                if submitted:
                    subject = f"Response to Ticket #{i+1}"
                    body = ticket['ideal_response']
                    if send_email(to_email, subject, body):
                        ticket["status"] = "Sent"
                        save_tickets("sample_tickets.json", tickets)
                        st.success("Email sent successfully!")
                        st.rerun()

# --- New Complaint Submission ---
st.markdown("---")
st.header("🆕 Submit a New Complaint")

if "user_complaint" not in st.session_state:
    st.session_state.user_complaint = ""
if "generated_summary" not in st.session_state:
    st.session_state.generated_summary = ""
if "generated_response" not in st.session_state:
    st.session_state.generated_response = ""

st.session_state.user_complaint = st.text_area("Enter a customer complaint", value=st.session_state.user_complaint)

if st.button("Generate Summary & Response"):
    if st.session_state.user_complaint.strip() == "":
        st.warning("Please enter a complaint before generating.")
    else:
        with st.spinner("Generating..."):
            try:
                summary, response_text = generate_summary_and_response(st.session_state.user_complaint)
                st.session_state.generated_summary = summary
                st.session_state.generated_response = response_text
                st.success("Summary and response generated!")
            except Exception as e:
                st.error(f"Error generating summary/response: {e}")

if st.session_state.generated_summary and st.session_state.generated_response:
    st.subheader("🧾 Summary")
    st.write(st.session_state.generated_summary)
    st.subheader("✉️ Suggested Response")
    st.write(st.session_state.generated_response)
    

    def clear_new_complaint():
        st.session_state.user_complaint = ""
        st.session_state.generated_summary = ""
        st.session_state.generated_response = ""
        st.rerun()

    if st.button("➕ Add to Dashboard"):
        new_ticket = {
            "timestamp": datetime.now().isoformat(),
            "ticket": st.session_state.user_complaint,
            "summary": st.session_state.generated_summary,
            "ideal_response": st.session_state.generated_response,
            "status": "Pending"
        }
        tickets.append(new_ticket)
        save_tickets("sample_tickets.json", tickets)
        st.success("New complaint added to dashboard!")
        clear_new_complaint()


# --- Download JSON ---
json_str = json.dumps(tickets, indent=2, ensure_ascii=False)
json_bytes = io.BytesIO(json_str.encode('utf-8'))
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
file_name = f"updated_tickets_{timestamp}.json"

st.download_button(
    label="📥 Download Updated JSON",
    data=json_bytes,
    file_name=file_name,
    mime="application/json"
)

st.caption("⬇️ Click the button above to download your updated file with a timestamped name.")
