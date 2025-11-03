from flask import Flask, render_template, request, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from io import BytesIO
import pandas as pd

app = Flask(__name__)

# ---------- Database Setup ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Excel file name
PAYMENT_EXCEL = "payments.xlsx"


# ---------- Payment Model ----------
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    amount = db.Column(db.Float)
    upi_id = db.Column(db.String(100))
    txn_id = db.Column(db.String(100), unique=True)
    date = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.String(20), default="Success")


# Create database tables if not exist
with app.app_context():
    db.create_all()


# ---------- Helper Function: Save Payment to Excel ----------
def save_payment_to_excel(name, amount, upi_id, txn_id, status):
    data = {
        "Name": [name],
        "Amount": [amount],
        "UPI ID": [upi_id],
        "Transaction ID": [txn_id],
        "Status": [status],
        "Date": [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]
    }

    new_df = pd.DataFrame(data)

    if os.path.exists(PAYMENT_EXCEL):
        old_df = pd.read_excel(PAYMENT_EXCEL)
        updated_df = pd.concat([old_df, new_df], ignore_index=True)
        updated_df.to_excel(PAYMENT_EXCEL, index=False)
    else:
        new_df.to_excel(PAYMENT_EXCEL, index=False)


# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index2.html')


@app.route('/plan')
def plan():
    return render_template('plan.html')


@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    name = data.get('name', 'Unknown')
    amount = float(data.get('amount', 0))
    upi_id = data.get('upi_id', 'N/A')
    txn_id = data.get('txn_id', f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}")

    # ---------- Save to Database ----------
    new_payment = Payment(
        name=name,
        amount=amount,
        upi_id=upi_id,
        txn_id=txn_id,
        status="Success"
    )
    db.session.add(new_payment)
    db.session.commit()

    # ---------- Save to Excel ----------
    save_payment_to_excel(name, amount, upi_id, txn_id, "Success")

    # ---------- Generate PDF Receipt ----------
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 800, "Jay Ambe Broadband Service")
    c.setFont("Helvetica", 12)
    c.drawString(50, 760, f"Customer Name: {name}")
    c.drawString(50, 740, f"Amount Paid: ₹{amount}")
    c.drawString(50, 720, f"UPI ID: {upi_id}")
    c.drawString(50, 700, f"Transaction ID: {txn_id}")
    c.drawString(50, 680, f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    c.line(50, 660, 550, 660)
    c.drawString(50, 640, "Payment Status: Success ✅")
    c.drawString(50, 620, "Thank you for your payment!")
    c.save()

    pdf_buffer.seek(0)

    # Return the PDF as a downloadable file
    return send_file(pdf_buffer, as_attachment=True,
                     download_name=f"receipt_{txn_id}.pdf",
                     mimetype='application/pdf')


@app.route('/payments', methods=['GET'])
def view_payments():
    """View all payments in JSON format."""
    payments = Payment.query.order_by(Payment.date.desc()).all()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "amount": p.amount,
            "upi_id": p.upi_id,
            "txn_id": p.txn_id,
            "date": p.date.strftime('%d-%m-%Y %H:%M:%S'),
            "status": p.status
        } for p in payments
    ]
    return jsonify(data)


@app.route('/download_excel')
def download_excel():
    """Download the payments Excel file."""
    if os.path.exists(PAYMENT_EXCEL):
        return send_file(PAYMENT_EXCEL, as_attachment=True)
    else:
        return jsonify({"error": "No payment records found yet!"}), 404


if __name__ == '__main__':
    os.makedirs("receipts", exist_ok=True)
    app.run(debug=True)
