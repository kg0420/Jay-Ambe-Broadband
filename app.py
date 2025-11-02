from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route('/')
def home():
    # This will render your main HTML page (saved in templates folder)
    return render_template('index2.html')

@app.route("/plan")
def plan():
    return render_template("plan.html")


@app.route('/generate_receipt', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    txn_id = data.get("txnId")
    plan_name = data.get("planName")
    amount = data.get("amount")
    now = datetime.now().strftime("%d/%m/%Y, %I:%M:%S %p")

    # ✅ Generate PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(130, 800, "Jay Ambe Broadband Service")
    c.setFont("Helvetica", 12)
    c.drawString(100, 770, f"Payment Receipt")
    c.line(100, 765, 400, 765)
    c.drawString(100, 740, f"Plan: {plan_name}")
    c.drawString(100, 720, f"Amount: ₹{amount}")
    c.drawString(100, 700, f"Transaction ID: {txn_id}")
    c.drawString(100, 680, f"Date: {now}")
    c.drawString(100, 660, "Payment Mode: UPI (GPay / PhonePe / Paytm)")
    c.drawString(100, 640, "UPI ID: jayambe@oksbi")
    c.setFillColorRGB(0, 0.6, 0)
    c.drawString(100, 610, "✅ Payment Verified Successfully")
    c.setFillColorRGB(0, 0, 0)
    c.drawString(100, 580, "Thank you for choosing Jay Ambe Broadband Service!")
    c.showPage()
    c.save()

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, as_attachment=True, download_name=f"JayAmbe_Receipt_{txn_id}.pdf")

if __name__ == "__main__":
    app.run(debug=True)

