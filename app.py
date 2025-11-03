from flask import Flask, render_template, request, send_file, jsonify
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
from io import BytesIO
import pandas as pd
import os

app = Flask(__name__)

# ---------- Folder & Excel File Setup ----------
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)
PAYMENT_EXCEL = os.path.join(DATA_FOLDER, "payments.xlsx")


# ---------- Helper Function: Save Payment to Excel ----------
def save_payment_to_excel(name, amount, upi_id, txn_id, status):
    """Appends new payment record to payments.xlsx or creates file if not exists."""
    record = {
        "Name": [name],
        "Amount": [amount],
        "UPI ID": [upi_id],
        "Transaction ID": [txn_id],
        "Status": [status],
        "Date": [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]
    }

    new_df = pd.DataFrame(record)

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

    # Extract payment details
    name = data.get('name', 'Unknown')
    amount = float(data.get('amount', 0))
    upi_id = data.get('upi_id', 'jayambe@ybl')
    txn_id = data.get('txn_id', f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}")
    status = data.get('status', 'Success')  # Default = Success unless frontend sends "Cancelled"

    # Save to Excel
    save_payment_to_excel(name, amount, upi_id, txn_id, status)

    # If payment cancelled — no receipt should be generated
    if status.lower() != "success":
        return jsonify({
            "message": "Payment cancelled. Record saved for reference.",
            "status": status
        }), 200

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
    c.drawString(50, 640, f"Payment Status: {status} {'✅' if status == 'Success' else '❌'}")
    c.drawString(50, 620, "Thank you for your payment!" if status == "Success" else "Payment not completed.")
    c.save()

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"receipt_{txn_id}.pdf",
        mimetype='application/pdf'
    )


@app.route('/payments')
def view_payments():
    """Return all payments in JSON format."""
    if not os.path.exists(PAYMENT_EXCEL):
        return jsonify([])
    df = pd.read_excel(PAYMENT_EXCEL)
    return jsonify(df.to_dict(orient="records"))


@app.route('/download_excel')
def download_excel():
    """Download the Excel file with all transactions."""
    if os.path.exists(PAYMENT_EXCEL):
        return send_file(PAYMENT_EXCEL, as_attachment=True)
    return jsonify({"error": "No payment records found yet!"}), 404


# ---------- Run Server ----------
if __name__ == '__main__':
    app.run(debug=True)
