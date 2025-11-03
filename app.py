from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    # This will render your main HTML page (saved in templates folder)
    return render_template('index2.html')

@app.route("/plan")
def plan():
    return render_template("plan.html")


def generate_receipt():
    data = request.json
    name = data.get('name', 'Unknown')
    amount = data.get('amount', '0')
    upi_id = data.get('upi_id', 'N/A')
    txn_id = data.get('txn_id', f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}")

    filename = f"receipt_{txn_id}.pdf"
    filepath = os.path.join("receipts", filename)

    # Generate PDF receipt
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


@app.route('/download_receipt/<filename>')
def download_receipt(filename):
    filepath = os.path.join("receipts", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return "Receipt not found", 404
if __name__ == "__main__":
    app.run(debug=True)edit my flask app
