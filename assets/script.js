// Mark active nav link based on current file
(function markActiveNav(){
  const path = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  document.querySelectorAll("[data-nav]").forEach(a=>{
    const target = (a.getAttribute("href") || "").toLowerCase();
    if ((path === "" && target.includes("index")) || target === path) a.classList.add("active");
  });
})();

// Products page: search + sort
(function productsTools(){
  const grid = document.querySelector("[data-products-grid]");
  if(!grid) return;

  const search = document.querySelector("[data-search]");
  const sort = document.querySelector("[data-sort]");

  const getCards = () => Array.from(grid.querySelectorAll("[data-product]"));

  function apply(){
    const q = (search?.value || "").trim().toLowerCase();
    const mode = sort?.value || "featured";

    let cards = getCards();

    // filter
    cards.forEach(card=>{
      const name = (card.getAttribute("data-name") || "").toLowerCase();
      const desc = (card.getAttribute("data-desc") || "").toLowerCase();
      const show = !q || name.includes(q) || desc.includes(q);
      card.style.display = show ? "" : "none";
    });

    // sort (only visible)
    cards = cards.filter(c => c.style.display !== "none");

    const by = {
      "price-asc":  (a,b)=> (+a.dataset.price) - (+b.dataset.price),
      "price-desc": (a,b)=> (+b.dataset.price) - (+a.dataset.price),
      "name-asc":   (a,b)=> (a.dataset.name || "").localeCompare(b.dataset.name || ""),
      "name-desc":  (a,b)=> (b.dataset.name || "").localeCompare(a.dataset.name || ""),
      "featured":   null
    }[mode];

    if(by){
      cards.sort(by).forEach(c => grid.appendChild(c));
    }
  }

  search?.addEventListener("input", apply);
  sort?.addEventListener("change", apply);
  apply();
})();

// Contact page: "fake submit" -> mailto
(function contactForm(){
  const form = document.querySelector("[data-contact-form]");
  if(!form) return;

  form.addEventListener("submit", (e)=>{
    e.preventDefault();
    const name = form.querySelector("[name='name']").value.trim();
    const email = form.querySelector("[name='email']").value.trim();
    const topic = form.querySelector("[name='topic']").value.trim();
    const message = form.querySelector("[name='message']").value.trim();

    const to = form.getAttribute("data-to") || "you@example.com";
    const subject = encodeURIComponent(topic ? `Website enquiry: ${topic}` : "Website enquiry");
    const body = encodeURIComponent(
      `Name: ${name}\nEmail: ${email}\n\n${message}\n`
    );

    window.location.href = `mailto:${to}?subject=${subject}&body=${body}`;
  });
})();

// 🔥 "REAL" SALE COUNTDOWN (persistent across refresh + pages via localStorage)
// + Under 20 min: animate  | Under 5 min: show HURRY + stronger animation
(function saleCountdownPersistent(){
  const cd = document.getElementById("countdown");
  if (!cd) return;

  const bar = document.querySelector(".countdown-wrap");
  const saleText = document.getElementById("saleText");

  const KEY_END = "tpa_sale_end_v1";
  const KEY_DURATION = "tpa_sale_duration_v1";

  const DEFAULT_DURATION_SECONDS = 20 * 60; // 20 minutes
  const duration = Number(localStorage.getItem(KEY_DURATION)) || DEFAULT_DURATION_SECONDS;

  function nowMs(){ return Date.now(); }

  function getOrCreateEndMs(){
    const saved = Number(localStorage.getItem(KEY_END));
    if (!saved || Number.isNaN(saved) || saved <= nowMs()) {
      const newEnd = nowMs() + duration * 1000;
      localStorage.setItem(KEY_END, String(newEnd));
      localStorage.setItem(KEY_DURATION, String(duration));
      return newEnd;
    }
    return saved;
  }

  function format(seconds){
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  function setUrgency(seconds){
    if (!bar) return;

    // Reset classes
    bar.classList.remove("is-urgent", "is-hurry");

    // Default text
    if (saleText) saleText.textContent = "🔥 FLASH SALE — 20% OFF ENDS IN";

    if (seconds <= 300) {
      bar.classList.add("is-hurry");
      if (saleText) saleText.textContent = "⚠️ HURRY — SALE ENDS IN";
    } else if (seconds <= 1200) { // 20 minutes
      bar.classList.add("is-urgent");
    }
  }

  function tick(){
    const endMs = getOrCreateEndMs();
    const remaining = Math.max(0, Math.floor((endMs - nowMs()) / 1000));

    cd.textContent = format(remaining);
    setUrgency(remaining);

    // When it hits 0, start a new sale window automatically
    if (remaining <= 0) {
      localStorage.removeItem(KEY_END);
    }
  }

  tick();
  setInterval(tick, 1000);
})();
