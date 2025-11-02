AOS.init({ once: true, duration: 800, offset: 100 });

// 💰 Plan Prices
const planPrices = {
  "20 Mbps": { "1 Month": 400, "3 Month": 1150, "6 Month": 2300, "Yearly": 4600 },
  "40 Mbps": { "1 Month": 450, "3 Month": 1300, "6 Month": 2600, "Yearly": 5200 },
  "60 Mbps": { "1 Month": 500, "3 Month": 1450, "6 Month": 2900, "Yearly": 5800 },
  "75 Mbps": { "1 Month": 600, "3 Month": 1750, "6 Month": 3500, "Yearly": 7000 },
  "100 Mbps": { "1 Month": 700, "3 Month": 2000, "6 Month": 4000, "Yearly": 8000 },
  "150 Mbps": { "1 Month": 900, "3 Month": 2600, "6 Month": 5200, "Yearly": 10400 },
};

// 📱 Detect mobile device
function isMobile() {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

// 🎨 OTT icon hover animation
document.querySelectorAll('.ott-item').forEach(item => {
  item.addEventListener('mouseenter', () => item.classList.add('animate-bounce-once'));
  item.addEventListener('mouseleave', () => item.classList.remove('animate-bounce-once'));
});

// 🔻 Toggle plan visibility
function togglePlan(header) {
  const table = header.nextElementSibling;
  const icon = header.querySelector("i");
  table.classList.toggle("hidden");
  icon.classList.toggle("rotate-180");
}

// 💳 Start Payment using GPay / UPI
function payNow(amount, planName) {
  const upiId = "bajajpay.6879729.01561666@indus"; // ✅ Your actual UPI ID (change if needed)
  const name = "Jay Ambe Broadband Service";
  const note = encodeURIComponent(`Payment for ${planName}`);
  const upiLink = `upi://pay?pa=${upiId}&pn=${encodeURIComponent(name)}&am=${amount}&cu=INR&tn=${note}`;

  if (isMobile()) {
    // 🟢 Open GPay or any UPI app
    window.location.href = upiLink;

    // Wait for user to return from payment app
    document.addEventListener("visibilitychange", function handleReturn() {
      if (document.visibilityState === "visible") {
        document.removeEventListener("visibilitychange", handleReturn);
        setTimeout(() => {
          const txnId = prompt("📩 Enter your UPI Transaction ID after successful payment:");
          if (txnId && txnId.trim() !== "") {
            verifyTransaction(txnId.trim(), planName, amount);
          } else {
            alert("❌ No Transaction ID provided. Payment not verified.");
          }
        }, 1200);
      }
    });

  } else {
    // 💻 Desktop fallback: show QR code
    const qrImg = document.getElementById("upiQr");
    const qrSection = document.getElementById("qrSection");
    const modal = document.getElementById("paymentModal");
    const selectedPlan = document.getElementById("selectedPlan");

    selectedPlan.textContent = `${planName} - ₹${amount}`;
    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(upiLink)}`;
    qrSection.classList.remove("hidden");
    modal.classList.remove("hidden");
  }
}

// ❌ Close payment modal
function closeModal() {
  document.getElementById("paymentModal").classList.add("hidden");
}

// ✅ Show toast alert
function showToast(msg = "✅ Receipt generated successfully!") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

// 🧾 Verify Transaction & Request Flask to Generate Receipt
function verifyTransaction(txnId, planName, amount) {
  if (txnId.length >= 8) {
    fetch("/generate_receipt", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ txnId, planName, amount })
    })
      .then(res => {
        if (!res.ok) throw new Error("Server Error");
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `JayAmbe_Receipt_${txnId}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast();
      })
      .catch(err => alert("⚠️ Failed to generate receipt: " + err.message));
  } else {
    alert("⚠️ Invalid Transaction ID. Please check and try again.");
  }
}

document.getElementById("payButton").addEventListener("click", () => {
  const name = document.getElementById("name").value.trim();
  const amount = document.getElementById("amount").value.trim();

  if (!name || !amount) {
    alert("Please enter your name and amount.");
    return;
  }

  const upiId = "jayambe@ybl"; // Your GPay UPI ID
  const txnId = "TXN" + Date.now();

  // Create UPI payment URL (works for GPay, PhonePe, Paytm, etc.)
  const upiUrl = `upi://pay?pa=${upiId}&pn=Jay%20Ambe%20Broadband&am=${amount}&cu=INR&tn=Broadband%20Bill%20Payment`;

  // Open GPay / UPI app
  window.location.href = upiUrl;

  // After payment, generate receipt manually (user confirmation)
  setTimeout(() => {
    if (confirm("Did you complete the payment?")) {
      fetch("/generate_receipt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, amount, upi_id: upiId, txn_id: txnId }),
      })
        .then(res => res.json())
        .then(data => {
          document.getElementById("status").innerText =
            "✅ Payment confirmed! Downloading your receipt...";
          window.location.href = `/download_receipt/${data.file}`;
        })
        .catch(err => alert("Error generating receipt: " + err));
    } else {
      alert("Payment not confirmed. Please try again.");
    }
  }, 5000);
});
