# AGENTS.md - FixPilot Porta Potty Rental Website

## Project Overview

Static single-page website for a porta potty rental business. Built with plain HTML, Tailwind CSS (CDN), and Python helper scripts. Deployed to Cloudflare Pages.

```
index.html              # Main landing page (~3700 lines)
locations/              # City-specific landing pages
hero-banner-images/     # Hero banner images
service-images/         # Service-related images
script.py               # Creates new city page structure
populate_images.py      # Populates HTML with random image links
smart_indexer.py        # Google Indexing API submission
```

---

## Commands

### Local Development
```bash
python3 -m http.server 8000
# Open http://localhost:8000/
```

### Python Scripts

**Create city page:**
```bash
python3 script.py "City Name"
# Creates locations/city-name/index.html and opens in editor
```

**Populate images in city page:**
```bash
python3 populate_images.py locations/austin [--hero-dir ./hero-banner-images] [--service-dir ./service-images]
```

**Submit sitemap to Google Indexing API:**
```bash
python3 smart_indexer.py
```

### Linting
```bash
# Python syntax check
python3 -m py_compile script.py populate_images.py smart_indexer.py

# HTML validation (manual)
# https://validator.w3.org/
```

### Testing
This project has no automated tests. Verify changes by:
1. Opening HTML in browser
2. Checking browser console for errors
3. Validating at https://validator.w3.org/
4. Testing mobile responsiveness via dev tools

---

## Code Style Guidelines

### HTML

- Use semantic HTML5: `<header>`, `<main>`, `<section>`, `<footer>`, `<nav>`
- Always include `lang="en"` on `<html>`
- Include meta tags: charset, viewport, description, OG tags, Twitter cards
- Use Tailwind via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Use Font Awesome: `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">`
- Use `&amp;` instead of `&` in HTML attributes
- Use kebab-case for CSS classes
- Include schema.org LocalBusiness JSON-LD structured data
- Make phone numbers clickable: `<a href="tel:+15551234567">`
- Always add alt text to images

### Python

**Imports (in order):**
1. Standard library (`os`, `re`, `sys`, `subprocess`)
2. Third-party (`requests`, `google.oauth2`)
3. Local/relative

**Naming:**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- File names: `snake_case.py`

**Type Hints:**
```python
def get_best_match(service_slug: str, service_dir: str) -> str | None:
    """Find the folder in service_dir that best matches the service slug."""
    ...
    return folder_name
```

**Docstrings:**
```python
def slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug.
    
    Args:
        name: The input string to slugify.
    
    Returns:
        A lowercase slug with spaces replaced by hyphens.
    """
```

**Error Handling:**
```python
# Use specific exception types when possible
try:
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
except FileNotFoundError:
    print("❌ index.html not found")
    return
except PermissionError:
    print("❌ Permission denied reading index.html")
    raise

# For API calls, return status + message pattern
def index_url(url: str) -> tuple[int, str]:
    try:
        res = requests.post(endpoint, headers=headers, json=data)
        return res.status_code, res.text
    except requests.RequestException as e:
        return 500, str(e)
```

**File Operations:**
- Always specify encoding: `open(path, "r", encoding="utf-8")`
- Use context managers: `with open(...) as f:`
- Close files immediately after writing

---

## SEO Requirements

- Unique `<title>` and `<meta name="description">` per page
- Open Graph tags: `og:title`, `og:description`, `og:image`, `og:url`
- Twitter Card tags
- Canonical URL
- schema.org LocalBusiness JSON-LD
- Update `sitemap.xml` for new pages

---

## Common Tasks

### Add New City
1. `python3 script.py "New City"`
2. Edit generated `index.html` with city-specific content
3. `python3 populate_images.py locations/new-city`
4. Add entry to `sitemap.xml`

### Location Page Structure
1. Copy from existing location (e.g., `locations/austin/`)
2. Update: title, h1, address, schema.org data
3. Run `populate_images.py` to link images
4. Test in browser

---

## Deployment

The site is deployed to Cloudflare Pages (see `.wrangler/`). Deployment is automatic on push to main branch.
