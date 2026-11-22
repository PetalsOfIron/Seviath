// Click tracking for GoatCounter (no cookies, no personal data): counts downloads and links that leave the site.
document.addEventListener("click", function (e) {
  var a = e.target.closest && e.target.closest("a[href]");
  if (!a || !window.goatcounter || !window.goatcounter.count) return;
  var h = a.getAttribute("href") || "";
  var leaves = /^(https?:)?\/\//.test(h) || /^[a-z][a-z0-9+.-]*:/i.test(h);
  if (!leaves && !/\.(zip|exe|pdf)(\?|$)/i.test(h)) return;
  var label = (a.textContent || h).replace(/\s+/g, " ").trim().slice(0, 60);
  window.goatcounter.count({path: "click/" + label, title: h, event: true});
}, true);
