# -------------------- IMPORTS --------------------
from flask import Flask, render_template, request, send_file, jsonify, redirect, flash, send_from_directory
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from email.message import EmailMessage
import smtplib, os
from flask_cors import CORS
from deep_translator import GoogleTranslator

# -------------------- APP CONFIG --------------------
app = Flask(__name__)
app.secret_key = "Krish123"
CORS(app)

# Create directory for receipts if not exist
if not os.path.exists("receipts"):
    os.makedirs("receipts")


# -------------------- 🌍 TRANSLATION ENDPOINT --------------------
# @app.route("/translate", methods=["POST"])
# def translate():
#     """Translate text dynamically using deep_translator.GoogleTranslator"""
#     try:
#         data = request.get_json()
#         text = data.get("text", "").strip()
#         lang = data.get("lang", "en")

#         if not text:
#             return jsonify({"translated_text": ""})

#         translated = GoogleTranslator(source="auto", target=lang).translate(text)
#         print(f"🔄 [{lang}] {text[:30]} ➜ {translated[:30]}")
#         return jsonify({"translated_text": translated})
#     except Exception as e:
#         print("❌ Translation error:", e)
#         # Fallback: return same text if translation fails
#         return jsonify({"translated_text": text})


# -------------------- 🏠 HOME PAGE --------------------
@app.route("/", methods=["GET", "POST"])
def home():
    """Home route with feedback email integration"""
    if request.method == "POST":
        name = request.form.get("name", "Unknown User")
        email = request.form.get("email", "No Email")
        message = request.form.get("message", "No Message")

        email_message = EmailMessage()
        email_message["Subject"] = f"💬 New Feedback from {name}"
        email_message["From"] = "krishgupta6502@gmail.com"
        email_message["To"] = "krishgupta6502@gmail.com"
        email_message.set_content(
            f"📋 Feedback Received:\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n\n"
            f"💬 Message:\n{message}\n\n"
            f"🕒 Sent on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        )

        try:
            # ⚠️ Use your Gmail App Password (not real password)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login("krishgupta6502@gmail.com", "aznd zend uexg zdtn")
                smtp.send_message(email_message)
            flash("✅ Feedback sent successfully!", "success")
        except Exception as e:
            flash(f"❌ Error sending feedback: {e}", "error")

        return redirect("/")

    return render_template("index2.html")


# -------------------- 💸 PLANS PAGE --------------------
@app.route("/plan")
def plan():
    """Show plans page"""
    return render_template("plan.html")


# -------------------- 🧾 RECEIPT GENERATION --------------------
@app.route("/generate_receipt", methods=["POST"])
def generate_receipt():
    """Generate PDF receipt for successful UPI transaction"""
    data = request.get_json()
    name = data.get("name", "Unknown")
    amount = data.get("amount", "0")
    upi_id = data.get("upi_id", "N/A")
    txn_id = data.get("txn_id", f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}")

    filename = f"receipt_{txn_id}.pdf"
    filepath = os.path.join("receipts", filename)

    # ✅ PDF Generation using reportlab
    c = canvas.Canvas(filepath, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 800, "Jay Ambe Broadband Service")
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"Customer Name: {name}")
    c.drawString(50, 740, f"Amount Paid: ₹{amount}")
    c.drawString(50, 720, f"UPI ID: {upi_id}")
    c.drawString(50, 700, f"Transaction ID: {txn_id}")
    c.drawString(50, 680, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    c.line(50, 660, 550, 660)
    c.drawString(50, 640, "Thank you for your payment! 💙")
    c.save()

    return jsonify({"file": filename})


@app.route("/download_receipt/<filename>")
def download_receipt(filename):
    """Download generated receipt as PDF"""
    filepath = os.path.join("receipts", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "❌ Receipt not found", 404


# -------------------- 🤖 ROBOTS + SITEMAP --------------------
@app.route("/robots.txt")
def robots():
    return send_from_directory(".", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(".", "sitemap.xml")


# -------------------- 🚀 MAIN ENTRY --------------------
if __name__ == "__main__":
    print("✅ Jay Ambe Broadband Flask App Running...")
    app.run(debug=True)
