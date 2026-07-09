/*
 * Meta Pixel loader — GATED (Operação Alvorada, MSN-009 C).
 * Não faz NADA até FB_PIXEL_ID ser preenchido com o ID real
 * (criado pelo Caio no Meta Events Manager, sessão guiada D1).
 * Depois de preenchido: PageView automático em toda página;
 * eventos Lead/InitiateCheckout/Purchase disparados pelas páginas.
 */
window.FB_PIXEL_ID = window.FB_PIXEL_ID || "1012110551536514";

(function () {
  if (!window.FB_PIXEL_ID) return; /* gate: sem ID, sem pixel, sem erro */
  !(function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () {
      n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
    };
    if (!f._fbq) f._fbq = n;
    n.push = n;
    n.loaded = !0;
    n.version = "2.0";
    n.queue = [];
    t = b.createElement(e);
    t.async = !0;
    t.src = v;
    s = b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t, s);
  })(window, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
  fbq("init", window.FB_PIXEL_ID);
  fbq("track", "PageView");
})();

/* helper seguro: nunca quebra a página se o pixel estiver desligado */
window.fdaTrack = function (eventName, params) {
  if (window.fbq && window.FB_PIXEL_ID) {
    window.fbq("track", eventName, params || {});
  }
};
