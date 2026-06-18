#!/usr/bin/env python3
"""Add a dismiss button + sessionStorage memory to the mobile sticky CTA.

Operates on:
  - service pages (ada-compliant-units, construction, etc.)
  - city pages
  - any other page where #mobile-cta exists

Idempotent: skips pages already migrated.
"""
from __future__ import annotations
import glob
import re

# Single-line condensed form found on service pages
PATTERN_CONDENSED = re.compile(
    r'<div id="mobile-cta"[^>]*>\s*<a[^>]+>(.*?)</a>\s*</div>',
    re.DOTALL,
)

# Multi-line form on the homepage was already replaced manually.

NEW_CTA = (
    '<div id="mobile-cta" class="fixed bottom-0 left-0 right-0 bg-green-600 shadow-2xl '
    'transform translate-y-full transition-transform duration-300 z-50 md:hidden flex '
    'items-stretch" style="z-index: 9999;">'
    '<a href="tel:+18336529344" class="flex-1 py-4 text-center text-white font-extrabold text-lg">'
    '<i class="fas fa-phone-alt mr-2 animate-pulse"></i>Call (833) 652-9344</a>'
    '<button id="mobile-cta-dismiss" type="button" aria-label="Hide call button" '
    'class="px-4 text-white/80 hover:text-white text-2xl leading-none">&times;</button>'
    '</div>'
)

NEW_SCRIPT = """
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
</script>"""


def patch(path: str) -> bool:
    html = open(path, encoding="utf-8").read()
    if 'mobile-cta-dismiss' in html:
        return False
    if 'id="mobile-cta"' not in html:
        return False

    new_html = PATTERN_CONDENSED.sub(NEW_CTA, html, count=1)
    if new_html == html:
        return False

    # Replace the existing scroll script and append the new one.
    # Try to find an inline script that toggles mobile-cta translateY.
    new_html = re.sub(
        r"<script>\s*window\.addEventListener\(['\"]scroll['\"],\s*function\(\)\s*\{[^}]*mobile-cta[^}]*\}\)\s*;?\s*</script>",
        NEW_SCRIPT.strip(),
        new_html,
        flags=re.DOTALL,
    )
    # If no replacement happened, append before </body>
    if 'mobile-cta-dismiss' not in new_html:
        new_html = re.sub(r"</body>", NEW_SCRIPT + "\n</body>", new_html, count=1)

    open(path, "w", encoding="utf-8").write(new_html)
    return True


def main() -> None:
    paths = (
        glob.glob("services/*.html")
        + glob.glob("porta-potty-rental-*-*/index.html")
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
    print(f"Made mobile-cta dismissable on {fixed} pages; {skipped} skipped.")


if __name__ == "__main__":
    main()
