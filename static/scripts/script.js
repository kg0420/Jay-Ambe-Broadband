// 🌟 Initialize AOS Animations
AOS.init({ once: true, duration: 800, offset: 100 });

// 💰 Broadband Plan Prices
const planPrices = {
  "20 Mbps": { "1 Month": 400, "3 Month": 1150, "6 Month": 2300, "Yearly": 4600 },
  "40 Mbps": { "1 Month": 450, "3 Month": 1300, "6 Month": 2600, "Yearly": 5200 },
  "60 Mbps": { "1 Month": 500, "3 Month": 1450, "6 Month": 2900, "Yearly": 5800 },
  "75 Mbps": { "1 Month": 600, "3 Month": 1750, "6 Month": 3500, "Yearly": 7000 },
  "100 Mbps": { "1 Month": 700, "3 Month": 2000, "6 Month": 4000, "Yearly": 8000 },
  "150 Mbps": { "1 Month": 900, "3 Month": 2600, "6 Month": 5200, "Yearly": 10400 },
};

// 📱 Detect Mobile Device
function isMobile() {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

// 🎨 OTT Hover Animation
document.querySelectorAll(".ott-item").forEach((item) => {
  item.addEventListener("mouseenter", () => item.classList.add("animate-bounce-once"));
  item.addEventListener("mouseleave", () => item.classList.remove("animate-bounce-once"));
});

// 🔻 Toggle Plan Table
function togglePlan(header) {
  const table = header.nextElementSibling;
  const icon = header.querySelector("i");
  table.classList.toggle("hidden");
  icon.classList.toggle("rotate-180");
}

// 💳 Main Payment Flow
function payNow(amount, planName) {
  const username = prompt("Enter your name to proceed with payment:");
  if (!username || username.trim() === "") {
    alert("⚠️ Please enter your name to continue.");
    return;
  }

  const upiId = "7219570360@okbizaxis"; // ✅ Business UPI
  const note = encodeURIComponent(`Payment for ${planName}`);
  const upiLink = `upi://pay?pa=${upiId}&pn=${encodeURIComponent(
    "Jay Ambe Broadband"
  )}&am=${amount}&cu=INR&tn=${note}`;

  // Step 1️⃣ Store preliminary transaction (Pending)
  fetch("/store_data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, plan: planName, amount, status: "Pending" }),
  }).catch(console.error);

  // Step 2️⃣ Mobile flow
  if (isMobile()) {
    window.location.href = upiLink;

    document.addEventListener("visibilitychange", function handleReturn() {
      if (document.visibilityState === "visible") {
        document.removeEventListener("visibilitychange", handleReturn);

        setTimeout(() => {
          const txnId = prompt("📩 Enter your UPI Transaction ID after payment:");
          if (txnId && txnId.trim() !== "") {
            verifyTransaction(txnId.trim(), planName, amount, username, upiId);
          } else {
            alert("❌ Transaction not verified. Payment marked as cancelled.");
            fetch("/store_data", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ username, plan: planName, amount, status: "Cancelled" }),
            }).catch(() => {});
          }
        }, 1200);
      }
    });
  } else {
    // Step 3️⃣ Desktop flow (QR modal)
    const qrImg = document.getElementById("upiQr");
    const qrSection = document.getElementById("qrSection");
    const modal = document.getElementById("paymentModal");
    const selectedPlan = document.getElementById("selectedPlan");

    selectedPlan.textContent = `${planName} - ₹${amount}`;
    qrImg.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(
      upiLink
    )}`;
    qrSection.classList.remove("hidden");
    modal.classList.remove("hidden");
  }
}

// 🧾 Verify Transaction → Generate PDF Receipt
function verifyTransaction(txnId, planName, amount, username, upiId) {
  fetch("/generate_receipt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: username, amount, upi_id: upiId, txn_id: txnId }),
  })
    .then((res) => {
      if (!res.ok) throw new Error("Server error while generating receipt");
      return res.blob();
    })
    .then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `JayAmbe_Receipt_${txnId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      showToast("✅ Receipt generated successfully!");
    })
    .catch((err) => {
      alert("⚠️ Error generating receipt: " + err.message);
      console.error(err);
    });
}

// ❌ Close Payment Modal
function closeModal() {
  document.getElementById("paymentModal").classList.add("hidden");
}

// 🔔 Toast Notification
function showToast(msg) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.classList.remove("hidden");
  setTimeout(() => toast.classList.add("hidden"), 3000);
}

// 🕒 Auto-hide flash message
setTimeout(() => {
  document.querySelectorAll(".flash-message").forEach((msg) => {
    msg.style.opacity = "0";
    msg.style.transition = "opacity 0.5s";
    setTimeout(() => msg.remove(), 500);
  });
}, 4000);

// 🌐 Language Translation Logic
document.addEventListener("DOMContentLoaded", () => {
  const langSelect = document.getElementById("languageSelect");
  const storedLang = localStorage.getItem("siteLang") || "en";
  langSelect.value = storedLang;

  async function translatePage(lang) {
    localStorage.setItem("siteLang", lang);

    const elements = document.querySelectorAll(
      "h1, h2, h3, h4, h5, h6, p, li, button, span, label, th, td, option, strong, em, small, div"
    );

    let count = 0;
    const loader = document.createElement("div");
    loader.innerText = "Translating...";
    Object.assign(loader.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      background: "rgba(0,0,0,0.8)",
      color: "white",
      padding: "8px 20px",
      borderRadius: "10px",
      zIndex: "99999",
      fontSize: "14px",
      fontFamily: "Poppins, sans-serif",
    });
    document.body.appendChild(loader);

    for (const el of elements) {
      const style = window.getComputedStyle(el);
      if (style.display === "none" || !el.textContent.trim()) continue;
      if (el.querySelector("i, svg, img, input, textarea, a")) continue;

      const original = el.getAttribute("data-original-text") || el.textContent.trim();
      if (!el.getAttribute("data-original-text")) {
        el.setAttribute("data-original-text", original);
      }

      if (lang === "en") {
        el.textContent = original;
      } else {
        try {
          const res = await fetch("/translate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: original, lang }),
          });
          const data = await res.json();
          if (data.translated_text && data.translated_text !== original) {
            el.textContent = data.translated_text;
            count++;
          }
        } catch (err) {
          console.error("❌ Translation error:", err);
        }
      }
    }

    loader.innerText = `✅ Translated ${count} elements`;
    setTimeout(() => loader.remove(), 2000);

    // 🔁 Refresh animations
    if (window.AOS) setTimeout(() => AOS.refresh(), 800);

    // 🔁 Reattach interactivity
    rebindInteractiveElements();
  }

  function rebindInteractiveElements() {
    // Keeps payment buttons, Razorpay, toggles etc. alive
    document.querySelectorAll(".plan-header")?.forEach((h) => {
      h.onclick = () => togglePlan(h);
    });
    console.log("♻️ Interactive elements rebound.");
  }

  langSelect.addEventListener("change", (e) => translatePage(e.target.value));

  if (storedLang !== "en") translatePage(storedLang);
});
