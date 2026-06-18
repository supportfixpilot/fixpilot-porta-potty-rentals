#!/usr/bin/env python3
"""Standardize header nav across service, blog, and city pages."""
import re
from pathlib import Path

ROOT = Path(__file__).parent

INACTIVE = "text-slate-600 hover:text-emerald-600 font-medium transition-colors"
ACTIVE   = "text-emerald-600 font-semibold"
M_INACTIVE = "text-slate-600 font-medium"
M_ACTIVE   = "text-emerald-600 font-semibold"

MOBILE_JS = """<script>
(function(){
  var btn = document.getElementById('mobile-menu-btn');
  var menu = document.getElementById('mobile-menu');
  if (btn && menu) btn.addEventListener('click', function(){ menu.classList.toggle('hidden'); });
})();
</script>"""

def make_header(active):
    def cls(key):
        return ACTIVE if key == active else INACTIVE
    def mcls(key):
        return M_ACTIVE if key == active else M_INACTIVE
    return f"""    <header class="bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16 md:h-20">
                <a href="/" class="flex items-center gap-3 group">
                    <div class="w-10 h-10 md:w-12 md:h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
                        <i class="fas fa-toilet text-white text-lg md:text-xl"></i>
                    </div>
                    <div>
                        <span class="text-xl md:text-2xl font-bold bg-gradient-to-r from-slate-800 to-slate-600 bg-clip-text text-transparent">FixPilot</span>
                        <span class="hidden sm:block text-xs text-slate-500 -mt-1">Porta Potty Rentals</span>
                    </div>
                </a>
                <nav class="hidden md:flex items-center gap-8">
                    <a href="/" class="{cls('home')}">Home</a>
                    <a href="/locations" class="{cls('locations')}">Locations</a>
                    <a href="/services/standard-porta-potty" class="{cls('services')}">Services</a>
                    <a href="/blog/porta-potty-rental-costs-2026.html" class="{cls('blog')}">Blog</a>
                    <a href="tel:+18336529344" class="inline-flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-full font-semibold transition-all hover:shadow-lg hover:shadow-emerald-500/25">
                        <i class="fas fa-phone text-sm"></i>
                        (833) 652-9344
                    </a>
                </nav>
                <button id="mobile-menu-btn" class="md:hidden p-2 text-slate-600">
                    <i class="fas fa-bars text-xl"></i>
                </button>
            </div>
        </div>
        <div id="mobile-menu" class="hidden md:hidden border-t border-slate-200 bg-white">
            <div class="px-4 py-4 space-y-3">
                <a href="/" class="block py-2 {mcls('home')}">Home</a>
                <a href="/locations" class="block py-2 {mcls('locations')}">Locations</a>
                <a href="/services/standard-porta-potty" class="block py-2 {mcls('services')}">Services</a>
                <a href="/blog/porta-potty-rental-costs-2026.html" class="block py-2 {mcls('blog')}">Blog</a>
                <a href="tel:+18336529344" class="block w-full text-center bg-emerald-600 text-white py-3 rounded-xl font-semibold mt-4">
                    <i class="fas fa-phone mr-2"></i>(833) 652-9344
                </a>
            </div>
        </div>
    </header>"""

# Pattern 1: normal <header>...</header>
HEADER_RE = re.compile(r'[ \t]*<header\b[^>]*>.*?</header>', re.DOTALL)
# Pattern 2: <nav class="...sticky...">...</nav> used instead of <header>
NAV_RE = re.compile(r'[ \t]*<nav\b[^>]*sticky[^>]*>.*?</nav>', re.DOTALL)
# Pattern 3: broken <header> with no </header>, ends at first </section>
BROKEN_HEADER_RE = re.compile(r'<header\b[^>]*>.*?</section>', re.DOTALL)

def fix_file(path, active, add_js=False):
    text = path.read_text(encoding='utf-8')
    # Skip if already standardized
    if 'backdrop-blur-md' in text and 'mobile-menu-btn' in text:
        return False
    new_header = make_header(active)
    for pattern in (HEADER_RE, NAV_RE, BROKEN_HEADER_RE):
        new_text, n = pattern.subn(new_header, text, count=1)
        if n:
            break
    else:
        print(f"  SKIP (no match): {path}")
        return False
    if 'mobile-menu-btn' not in new_text:
        new_text = new_text.replace('</body>', MOBILE_JS + '\n</body>', 1)
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        return True
    return False

def main():
    counts = {'service': 0, 'blog': 0, 'city': 0, 'skip': 0}

    # Service pages
    for f in sorted(ROOT.glob('services/*.html')):
        if fix_file(f, 'services', add_js=True):
            counts['service'] += 1
            print(f"  service: {f.name}")
        else:
            counts['skip'] += 1

    # Blog pages
    for f in sorted(ROOT.glob('blog/*.html')):
        if fix_file(f, 'blog', add_js=True):
            counts['blog'] += 1
            print(f"  blog: {f.name}")
        else:
            counts['skip'] += 1

    # City pages
    for f in sorted(ROOT.glob('porta-potty-rental-*/index.html')):
        if fix_file(f, 'locations', add_js=False):
            counts['city'] += 1
        else:
            counts['skip'] += 1

    print(f"\nDone — service:{counts['service']} blog:{counts['blog']} city:{counts['city']} skipped:{counts['skip']}")

if __name__ == '__main__':
    main()
