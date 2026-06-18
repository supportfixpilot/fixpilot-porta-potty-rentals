# GEMINI.md

## Directory Overview

This directory contains a single-page, static website for a porta potty rental business called "FixPilot". The website is designed for a national audience across the USA, with a focus on generating leads through phone calls.

The structure includes a main `index.html`, various image assets, and a `locations` directory intended to house location-specific pages.

## Key Files

*   `index.html`: The main and only HTML file for the website. It contains the entire structure, content, and styling (via Tailwind CSS and inline styles). It also includes schema.org structured data for local businesses and an FAQ section.
*   `images/`: This directory contains all the image assets used on the website, such as photos of different porta potty units and service icons.
*   `hero-banner-images/`: Contains a collection of images presumably for use in the hero banner section of the website.
*   `locations/`: This directory contains numerous subdirectories, each named after a city. The intention is likely to create separate landing pages for each location to target local search queries. Currently, most of these directories are empty.
*   `robots.txt`: Specifies the parts of the site that web crawlers should not access.
*   `sitemap.xml`: Provides a map of the website's pages to help search engines better crawl the site.

## Usage

This is a static website. To view or serve it, you can:

1.  **Open Locally:** Open the `index.html` file directly in a web browser.
2.  **Serve with a simple HTTP server:** Run a simple web server from the root of this directory. For example, using Python:

    ```bash
    python3 -m http.server
    ```

    Then, navigate to `http://localhost:8000/` in your browser.
