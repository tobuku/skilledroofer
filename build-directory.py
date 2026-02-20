"""
build-directory.py — Generates the SkilledRoofer contractor directory.
Reads the cleaned CSV and outputs:
  - directory.html  (main hub with state grid)
  - directory/<state>.html  (one page per state with contractor cards)

Re-run whenever the CSV is updated.
"""

import csv
import os
import json
import html as html_mod
from collections import defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'Desktop',
                        'claude-skilled-Roofer-template-CLEANED.csv')
OUT_DIR = os.path.dirname(__file__)

STATE_ABBR_TO_NAME = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming'
}

NAME_TO_ABBR = {v: k for k, v in STATE_ABBR_TO_NAME.items()}


def slug(name):
    return name.lower().replace(' ', '-')


def stars_html(rating):
    """Return HTML for star display given a rating like 4.8."""
    if not rating:
        return ''
    try:
        r = float(rating)
    except ValueError:
        return ''
    full = int(r)
    half = 1 if r - full >= 0.3 else 0
    empty = 5 - full - half
    return '★' * full + ('½' if half else '') + '☆' * empty


def e(text):
    """HTML-escape."""
    return html_mod.escape(str(text)) if text else ''


def read_csv():
    contractors = defaultdict(list)
    total = 0
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            state_abbr = row.get('state', '').strip().upper()
            if state_abbr not in STATE_ABBR_TO_NAME:
                continue
            state_name = STATE_ABBR_TO_NAME[state_abbr]
            contractors[state_name].append({
                'name': row.get('business_name', '').strip(),
                'address': row.get('street_address', '').strip(),
                'city': row.get('city', '').strip(),
                'state': state_abbr,
                'zip': row.get('zip', '').strip(),
                'phone': row.get('phone', '').strip(),
                'website': row.get('website', '').strip(),
                'rating': row.get('google_rating', '').strip(),
                'reviews': row.get('review_count', '').strip(),
            })
            total += 1
    return contractors, total


# ── NAV ──────────────────────────────────────────────────────────────
def nav_html(active='directory', prefix=''):
    return f'''<nav class="nav">
  <div class="nav-inner">
    <a href="{prefix}index.html" class="nav-logo">
      <img src="{prefix}favicon.svg" alt="SR" width="32" height="32">
      <span class="nav-logo-text">Skilled<span>Roofer</span></span>
    </a>
    <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Toggle menu">☰</button>
    <ul class="nav-links">
      <li><a href="{prefix}shingles.html">Shingles</a></li>
      <li><a href="{prefix}metal-roofing.html">Metal Roofing</a></li>
      <li><a href="{prefix}commercial.html">Commercial</a></li>
      <li><a href="{prefix}tools.html">Tools</a></li>
      <li><a href="{prefix}directory.html" class="active">Directory</a></li>
    </ul>
  </div>
</nav>'''


# ── FOOTER ───────────────────────────────────────────────────────────
def footer_html(prefix=''):
    return f'''<footer class="footer">
  <div class="footer-inner">
    <div class="footer-brand">
      <h3>Skilled<span>Roofer</span></h3>
      <p>Expert roofing material reviews and buying guides for professionals and homeowners.</p>
    </div>
    <div class="footer-col">
      <h4>Guides</h4>
      <ul>
        <li><a href="{prefix}shingles.html">Best Shingles</a></li>
        <li><a href="{prefix}metal-roofing.html">Metal Roofing</a></li>
        <li><a href="{prefix}metal-vs-shingles.html">Metal vs Shingles</a></li>
        <li><a href="{prefix}commercial.html">Commercial</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>More</h4>
      <ul>
        <li><a href="{prefix}underlayment.html">Underlayment</a></li>
        <li><a href="{prefix}tools.html">Roofing Tools</a></li>
        <li><a href="{prefix}directory.html">Contractor Directory</a></li>
        <li><a href="{prefix}privacy.html">Privacy Policy</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>&copy; 2026 SkilledRoofer.com — All rights reserved.</span>
    <span>As an Amazon Associate, we earn from qualifying purchases.</span>
  </div>
</footer>'''


# ── GSAP SCRIPT ──────────────────────────────────────────────────────
GSAP_SCRIPT = '''<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger);
  document.querySelectorAll('.animate-in').forEach((el, i) => {
    gsap.fromTo(el,
      { opacity: 0, y: 30 },
      { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none none' },
        delay: i * 0.05
      }
    );
  });
</script>'''


# ── HUB PAGE ─────────────────────────────────────────────────────────
def build_hub(contractors, total):
    state_cards = []
    for state_name in sorted(contractors.keys()):
        count = len(contractors[state_name])
        s = slug(state_name)
        state_cards.append(
            f'    <a href="directory/{s}.html" class="state-card animate-in">'
            f'<span class="state-card-name">{e(state_name)}</span>'
            f'<span class="state-card-count">{count} contractor{"s" if count != 1 else ""}</span></a>'
        )

    # Build JSON for search: [{state, slug, count}]
    state_data = json.dumps([
        {'state': sn, 'slug': slug(sn), 'count': len(contractors[sn])}
        for sn in sorted(contractors.keys())
    ])

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Find Roofing Contractors Near You | SkilledRoofer.com</title>
  <meta name="description" content="Browse {total:,} verified roofing contractors across all 50 states. Find trusted roofers near you with ratings, reviews, and contact info.">
  <meta property="og:title" content="Find Roofing Contractors Near You | SkilledRoofer.com">
  <meta property="og:description" content="Browse {total:,} verified roofing contractors across all 50 states.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://skilledroofer.com/directory.html">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>

{nav_html('directory', '')}

<!-- Page Header -->
<div class="page-header">
  <div class="page-header-content">
    <div class="hero-badge">Contractor Directory</div>
    <h1>Find Roofing Contractors <span class="highlight">Near You</span></h1>
    <p>Browse {total:,} verified roofing contractors across all 50 states. Find trusted roofers with ratings, reviews, and contact information.</p>
  </div>
</div>

<div class="section">
  <div class="directory-search">
    <input type="text" id="stateSearch" placeholder="Search by state name..." oninput="filterStates()">
  </div>
  <div class="directory-count" id="stateCount">Showing all <strong>{len(contractors)}</strong> states &mdash; <strong>{total:,}</strong> contractors total</div>

  <div class="state-grid" id="stateGrid">
{chr(10).join(state_cards)}
  </div>
</div>

{footer_html('')}

{GSAP_SCRIPT}
<script>
const stateData = {state_data};
function filterStates() {{
  const q = document.getElementById('stateSearch').value.toLowerCase().trim();
  const grid = document.getElementById('stateGrid');
  const cards = grid.querySelectorAll('.state-card');
  let shown = 0, contractors = 0;
  stateData.forEach((s, i) => {{
    const match = !q || s.state.toLowerCase().includes(q);
    cards[i].style.display = match ? '' : 'none';
    if (match) {{ shown++; contractors += s.count; }}
  }});
  document.getElementById('stateCount').innerHTML =
    'Showing <strong>' + shown + '</strong> state' + (shown !== 1 ? 's' : '') +
    ' &mdash; <strong>' + contractors.toLocaleString() + '</strong> contractors total';
}}
</script>

</body>
</html>'''
    return page


# ── STATE PAGE ───────────────────────────────────────────────────────
def build_state_page(state_name, items):
    abbr = NAME_TO_ABBR[state_name]
    # Build contractor cards
    cards = []
    for c in items:
        rating_html = ''
        if c['rating']:
            star_display = stars_html(c['rating'])
            review_text = f'({e(c["reviews"])} review{"s" if c["reviews"] != "1" else ""})' if c['reviews'] else ''
            rating_html = (
                f'<div class="contractor-rating">'
                f'<span class="contractor-stars">{star_display}</span>'
                f'<span class="contractor-rating-num">{e(c["rating"])}</span>'
                f'<span class="contractor-reviews">{review_text}</span>'
                f'</div>'
            )

        addr_parts = []
        if c['address']:
            addr_parts.append(e(c['address']))
        city_state_zip = ', '.join(filter(None, [e(c['city']), e(c['state'])]))
        if c['zip']:
            city_state_zip += ' ' + e(c['zip'])
        if city_state_zip:
            addr_parts.append(city_state_zip)
        address_html = '<br>'.join(addr_parts)

        phone_html = ''
        if c['phone']:
            digits = ''.join(ch for ch in c['phone'] if ch.isdigit())
            if digits.startswith('1') and len(digits) > 10:
                digits = digits[1:]
            phone_html = f'<a href="tel:+1{digits}" class="contractor-phone">📞 {e(c["phone"])}</a>'

        website_html = ''
        if c['website']:
            url = c['website'] if c['website'].startswith('http') else 'https://' + c['website']
            website_html = f'<a href="{e(url)}" target="_blank" rel="noopener" class="contractor-website">🌐 Visit Website →</a>'

        cards.append(f'''    <div class="contractor-card animate-in" data-name="{e(c['name']).lower()}" data-city="{e(c['city']).lower()}" data-zip="{e(c['zip'])}">
      {rating_html}
      <h3>{e(c['name'])}</h3>
      <div class="contractor-address">{address_html}</div>
      {phone_html}
      {website_html}
    </div>''')

    # JSON for search
    search_data = json.dumps([
        {'name': c['name'].lower(), 'city': c['city'].lower(), 'zip': c['zip']}
        for c in items
    ])

    count = len(items)

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Roofing Contractors in {e(state_name)} | SkilledRoofer.com</title>
  <meta name="description" content="Find {count} trusted roofing contractors in {e(state_name)}. Browse ratings, reviews, phone numbers, and websites for local roofers.">
  <meta property="og:title" content="Roofing Contractors in {e(state_name)} | SkilledRoofer.com">
  <meta property="og:description" content="Find {count} trusted roofing contractors in {e(state_name)}.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://skilledroofer.com/directory/{slug(state_name)}.html">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css">
</head>
<body>

{nav_html('directory', '../')}

<!-- Page Header -->
<div class="page-header">
  <div class="page-header-content">
    <div class="hero-badge">Contractor Directory</div>
    <h1>Roofing Contractors in <span class="highlight">{e(state_name)}</span></h1>
    <p>Browse {count} verified roofing contractors in {e(state_name)} with ratings, reviews, and contact information.</p>
  </div>
</div>

<div class="section">
  <div class="directory-search">
    <input type="text" id="contractorSearch" placeholder="Search by business name, city, or zip..." oninput="filterContractors()">
  </div>
  <div class="directory-count" id="contractorCount">Showing all <strong>{count}</strong> contractors in {e(state_name)}</div>

  <div class="contractor-grid" id="contractorGrid">
{chr(10).join(cards)}
  </div>
  <div class="no-results" id="noResults" style="display:none;">No contractors found matching your search.</div>
</div>

<div class="section" style="padding-top:0;">
  <a href="../directory.html" class="btn btn-outline">← Back to All States</a>
</div>

{footer_html('../')}

{GSAP_SCRIPT}
<script>
const searchData = {search_data};
function filterContractors() {{
  const q = document.getElementById('contractorSearch').value.toLowerCase().trim();
  const grid = document.getElementById('contractorGrid');
  const cards = grid.querySelectorAll('.contractor-card');
  let shown = 0;
  searchData.forEach((s, i) => {{
    const match = !q || s.name.includes(q) || s.city.includes(q) || s.zip.includes(q);
    cards[i].style.display = match ? '' : 'none';
    if (match) shown++;
  }});
  document.getElementById('contractorCount').innerHTML =
    'Showing <strong>' + shown + '</strong> contractor' + (shown !== 1 ? 's' : '') + ' in {e(state_name)}';
  document.getElementById('noResults').style.display = shown === 0 ? '' : 'none';
}}
</script>

</body>
</html>'''
    return page


# ── MAIN ─────────────────────────────────────────────────────────────
def main():
    print('Reading CSV...')
    contractors, total = read_csv()
    print(f'Found {total} contractors across {len(contractors)} states.')

    # Ensure directory/ folder exists
    dir_path = os.path.join(OUT_DIR, 'directory')
    os.makedirs(dir_path, exist_ok=True)

    # Build hub page
    hub = build_hub(contractors, total)
    hub_path = os.path.join(OUT_DIR, 'directory.html')
    with open(hub_path, 'w', encoding='utf-8') as f:
        f.write(hub)
    print(f'Wrote {hub_path}')

    # Build state pages
    for state_name in sorted(contractors.keys()):
        items = contractors[state_name]
        page = build_state_page(state_name, items)
        page_path = os.path.join(dir_path, f'{slug(state_name)}.html')
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'  {slug(state_name)}.html — {len(items)} contractors')

    print(f'\nDone! Generated hub + {len(contractors)} state pages.')


if __name__ == '__main__':
    main()
