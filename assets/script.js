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

