#!/usr/bin/env python3
"""Update locations.html with all current city pages grouped by state."""

import glob
import os
import re

STATE_NAMES = {
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
    'WI': 'Wisconsin', 'WY': 'Wyoming',
}

STATE_HUB_SLUGS = {
    'AL': 'alabama', 'AZ': 'arizona', 'AR': 'arkansas', 'CA': 'california',
    'CO': 'colorado', 'CT': 'connecticut', 'FL': 'florida', 'GA': 'georgia',
    'ID': 'idaho', 'IL': 'illinois', 'IN': 'indiana', 'IA': 'iowa',
    'KS': 'kansas', 'KY': 'kentucky', 'LA': 'louisiana', 'MA': 'massachusetts',
    'MD': 'maryland', 'MI': 'michigan', 'MN': 'minnesota', 'MS': 'mississippi',
    'MO': 'missouri', 'MT': 'montana', 'NE': 'nebraska', 'NV': 'nevada',
    'NJ': 'new-jersey', 'NM': 'new-mexico', 'NY': 'new-york', 'NC': 'north-carolina',
    'ND': 'north-dakota', 'OH': 'ohio', 'OK': 'oklahoma', 'OR': 'oregon',
    'PA': 'pennsylvania', 'SC': 'south-carolina', 'SD': 'south-dakota',
    'TN': 'tennessee', 'TX': 'texas', 'UT': 'utah', 'VA': 'virginia',
    'WA': 'washington', 'WI': 'wisconsin', 'WY': 'wyoming',
}


def build_state_sections():
    # Collect city pages by state
    state_cities = {}
    for path in sorted(glob.glob('porta-potty-rental-*-*/index.html')):
        m = re.search(r'porta-potty-rental-(.+)-([a-z]{2})/index\.html$', path)
        if not m:
            continue
        city_slug = m.group(1)
        state = m.group(2).upper()
        city_name = city_slug.replace('-', ' ').title()
        state_cities.setdefault(state, []).append((city_name, city_slug + '-' + m.group(2)))

    html = ''
    for state_code in sorted(STATE_NAMES.keys()):
        cities = state_cities.get(state_code, [])
        if not cities:
            continue
        state_name = STATE_NAMES[state_code]
        hub_slug = STATE_HUB_SLUGS.get(state_code, '')
        hub_exists = hub_slug and os.path.exists(f'porta-potty-rental-{hub_slug}/index.html')

        state_link = f'/porta-potty-rental-{hub_slug}' if hub_exists else '#'
        state_href = f'href="{state_link}"' if hub_exists else ''

        html += f'''
      <div class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-xl font-bold text-gray-800">{state_name} ({len(cities)} cities)</h3>
          {'<a ' + state_href + ' class="text-sm text-blue-600 hover:underline font-medium">View ' + state_name + ' →</a>' if hub_exists else ''}
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2">'''

        for city_name, full_slug in sorted(cities):
            html += f'''
          <a href="/porta-potty-rental-{full_slug}" class="text-sm text-blue-700 hover:text-blue-900 hover:underline font-medium py-1 px-2 rounded bg-blue-50 hover:bg-blue-100 transition truncate">{city_name}</a>'''

        html += '''
        </div>
      </div>'''

    return html


def update_locations_html():
    html = open('locations.html', encoding='utf-8').read()

    state_sections = build_state_sections()

    # Find and replace the city grid section
    # Look for the section after "top-cities" grid
    injection_section = f'''
  <!-- All Locations by State - Auto-generated -->
  <section class="py-16 bg-white" id="all-locations">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold text-gray-900 mb-3 text-center">All Locations by State</h2>
      <p class="text-gray-600 text-center mb-10 max-w-2xl mx-auto">Browse all {len(list(glob.glob("porta-potty-rental-*-*/index.html")))} cities we serve. Click any city for local pricing and same-day availability.</p>
      <div class="max-w-7xl mx-auto">
        {state_sections}
      </div>
    </div>
  </section>
'''

    # Check if section already exists
    if 'id="all-locations"' in html:
        # Replace existing section
        new_html = re.sub(
            r'<!-- All Locations by State.*?</section>',
            injection_section.strip(),
            html,
            flags=re.DOTALL
        )
    else:
        # Inject before footer
        footer_idx = html.rfind('<footer')
        if footer_idx == -1:
            footer_idx = html.rfind('</body>')
        new_html = html[:footer_idx] + injection_section + '\n' + html[footer_idx:]

    with open('locations.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

    total_cities = len(list(glob.glob('porta-potty-rental-*-*/index.html')))
    print(f'Updated locations.html with {total_cities} city links')


if __name__ == '__main__':
    update_locations_html()
