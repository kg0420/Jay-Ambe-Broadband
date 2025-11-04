from flask import Flask, render_template, request, send_file, jsonify, redirect, flash
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime
import smtplib
from email.message import EmailMessage
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = "Krish123"

# Ensure receipts folder exists
if not os.path.exists("receipts"):
    os.makedirs("receipts")

# -------------------- Home Page --------------------
@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Compose email
        email_message = EmailMessage()
        email_message['Subject'] = f'💬 New Feedback from {name}'
        email_message['From'] = "your_email@gmail.com"
        email_message['To'] = "your_email@gmail.com"
        email_message.set_content(
            f"📋 Feedback Received:\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n\n"
            f"💬 Message:\n{message}\n\n"
        )

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("krishgupta6502@gmail.com", "aznd zend uexg zdtn")
                smtp.send_message(email_message)

            flash("✅ Feedback sent successfully!", "success")
        except Exception as e:
            flash(f"❌ Error sending feedback: {e}", "error")

        return redirect("/")  # Redirect back to homepage after submission

    return render_template("index2.html")  # Render homepage


# -------------------- Plan Page --------------------
@app.route("/plan")
def plan():
    return render_template("plan.html")

# -------------------- Generate PDF Receipt --------------------
@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    name = data.get('name', 'Unknown')
    amount = data.get('amount', '0')
    upi_id = data.get('upi_id', 'N/A')
    txn_id = data.get('txn_id', f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}")

    filename = f"receipt_{txn_id}.pdf"
    filepath = os.path.join("receipts", filename)

    # Generate PDF
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
    c.drawString(50, 640, "Thank you for your payment!")
    c.save()

    return jsonify({"file": filename})

# -------------------- Download Receipt --------------------
@app.route('/download_receipt/<filename>')
def download_receipt(filename):
    filepath = os.path.join("receipts", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "Receipt not found", 404

# -------------------- Feedback Form --------------------
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        name = request.form.get("name", "Unknown")
        email = request.form.get("email", "N/A")
        message = request.form.get("message", "")

        # Compose email
        email_message = EmailMessage()
        email_message['Subject'] = f'💬 New Feedback from {name}'
        email_message['From'] = "krishgupta6502@gmail.com"  # Your Gmail
        email_message['To'] = "krishgupta6502@gmail.com"    # Receiver (you)
        email_message.set_content(
            f"📋 Feedback Received:\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n\n"
            f"💬 Message:\n{message}\n\n"
            f"🕒 Sent on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
        )

        try:
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("krishgupta6502@gmail.com", "aznd zend uexg zdtn")  # App password
                smtp.send_message(email_message)
            flash("✅ Feedback sent successfully!", "success")
        except Exception as e:
            flash(f"❌ Error sending feedback: {e}", "error")

        return redirect("/feedback")

    return render_template("feedback.html")  # Feedback page


@app.route('/robots.txt')
def robots():
    return send_from_directory('.', 'robots.txt')


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('.', 'sitemap.xml')

# -------------------- Run the Flask App --------------------
if __name__ == "__main__":
    app.run(debug=True)
