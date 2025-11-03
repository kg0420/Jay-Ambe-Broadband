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

// 💳 Pay Now Function (Unified with Excel Data + Receipt)
function payNow(amount, planName) {
  const username = prompt("Enter your name to proceed with payment:");

  if (!username) {
    alert("⚠️ Please enter your name to continue.");
    return;
  }

  const upiId = "bajajpay.6879729.01561666@indus"; // ✅ Your actual UPI ID
  const note = encodeURIComponent(`Payment for ${planName}`);
  const upiLink = `upi://pay?pa=${upiId}&pn=${encodeURIComponent("Jay Ambe Broadband")}&am=${amount}&cu=INR&tn=${note}`;

  // 📦 Step 1: Save user details to Flask backend (Excel)
  fetch("/store_data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, plan: planName, amount })
  })
  .then(res => res.json())
  .then(data => console.log("✅ User data stored:", data))
  .catch(err => console.error("❌ Error saving data:", err));

  // 📲 Step 2: Open UPI App (Mobile)
  if (isMobile()) {
    window.location.href = upiLink;

    // Wait for user to return from payment app
    document.addEventListener("visibilitychange", function handleReturn() {
      if (document.visibilityState === "visible") {
        document.removeEventListener("visibilitychange", handleReturn);
        setTimeout(() => {
          const txnId = prompt("📩 Enter your UPI Transaction ID after successful payment:");
          if (txnId && txnId.trim() !== "") {
            verifyTransaction(txnId.trim(), planName, amount, username, upiId);
          } else {
            alert("❌ No Transaction ID entered. Payment not verified.");
          }
        }, 1200);
      }
    });
  } 
  else {
    // 💻 Desktop fallback – show QR modal
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

// 🧾 Verify Payment & Generate Receipt (via Flask)
function verifyTransaction(txnId, planName, amount, username, upiId) {
  fetch("/generate_receipt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: username, amount, upi_id: upiId, txn_id: txnId })
  })
    .then(res => res.blob())
    .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `JayAmbe_Receipt_${txnId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("✅ Receipt generated successfully!");
    })
    .catch(err => alert("⚠️ Error generating receipt: " + err.message));
}

// ❌ Close Modal
function closeModal() {
  document.getElementById("paymentModal").classList.add("hidden");
}

// ✅ Toast Notification
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}
