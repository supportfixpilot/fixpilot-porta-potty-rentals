#!/usr/bin/env python3
"""Add the dismissable mobile sticky CTA to every page that doesn't have one.

Insertion point: just before </body>. Idempotent.
"""
from __future__ import annotations
import glob
import re

CTA_HTML = """
<!-- Mobile sticky call CTA (added site-wide) -->
<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-green-600 shadow-2xl transform translate-y-full transition-transform duration-300 z-50 md:hidden flex items-stretch" style="z-index: 9999;">
  <a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg">
    <i class="fas fa-phone-alt mr-2 animate-pulse"></i>Call (833) 652-9344
  </a>
  <button id="mobile-cta-dismiss" type="button" aria-label="Hide call button" class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button>
</div>
<script>
(function () {
  var cta = document.getElementById('mobile-cta');
  var dismiss = document.getElementById('mobile-cta-dismiss');
  if (!cta) return;
  var dismissed = false;
  try { dismissed = sessionStorage.getItem('mobileCtaDismissed') === '1'; } catch (e) {}
  if (dismissed) { cta.style.display = 'none'; return; }
  window.addEventListener('scroll', function () {
    if (dismissed) return;
    cta.style.transform = window.scrollY > 300 ? 'translateY(0)' : 'translateY(100%)';
  }, { passive: true });
  if (dismiss) {
    dismiss.addEventListener('click', function (e) {
      e.preventDefault();
      dismissed = true;
      cta.style.transform = 'translateY(100%)';
      setTimeout(function () { cta.style.display = 'none'; }, 300);
      try { sessionStorage.setItem('mobileCtaDismissed', '1'); } catch (e) {}
    });
  }
})();
</script>
"""


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if 'id="mobile-cta"' in html:
        return False
    new_html, n = re.subn(r"</body>", CTA_HTML + "</body>", html, count=1)
    if n == 0:
        return False
    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    paths = (
        glob.glob("porta-potty-rental-*-*/index.html")
        + glob.glob("services/*.html")
        + glob.glob("blog/*.html")
        + ["locations.html"]
    )
    fixed = 0
    skipped = 0
    for path in sorted(set(paths)):
        try:
            if patch(path):
                fixed += 1
            else:
                skipped += 1
        except FileNotFoundError:
            pass
    print(f"Added mobile sticky CTA to {fixed} pages; {skipped} already had one.")


if __name__ == "__main__":
    main()
