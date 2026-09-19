#!/usr/bin/env python3
"""
Daily CBSE Class 9 article generator for cbseclass9.com
Generates a complete HTML article using Claude API and saves it to the repo.
Run via GitHub Actions on a daily schedule.
"""

import anthropic
import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
import seo_utils as su

DOMAIN = "cbseclass9.com"
SITE_NAME = "CBSEClass9"

AUTHORS = ["Ananya Sharma", "Rohan Verma", "Priya Nair", "Arjun Mehta", "Sneha Iyer", "Karan Malhotra", "Divya Reddy", "Aditya Joshi"]


def add_byline(html, today_display):
    author = random.choice(AUTHORS)
    byline = (
        '<div style="max-width:800px;margin:20px auto 0;padding:0 24px;'
        'font-family:-apple-system,sans-serif;font-size:0.88rem;color:#6b7280;">'
        f'By <a href="https://padhle.in" style="color:#7C3AED;text-decoration:none;font-weight:600;">{author}</a>'
        f' &middot; \U0001F4C5 {today_display}</div>'
    )
    idx = html.find("<body")
    if idx == -1:
        return byline + html
    end = html.find(">", idx)
    if end == -1:
        return byline + html
    end += 1
    return html[:end] + byline + html[end:]


TOPICS = [
    {"slug": "cbse9-matter-in-our-surroundings", "title": "Matter in Our Surroundings for CBSE Class 9: States, Change and NCERT Questions", "subject": "Science"},
    {"slug": "cbse9-atoms-and-molecules", "title": "Atoms and Molecules for CBSE Class 9: Laws, Formulae and Mole Concept Basics", "subject": "Science"},
    {"slug": "cbse9-structure-of-atom", "title": "Structure of the Atom for CBSE Class 9: Models, Particles and Valency", "subject": "Science"},
    {"slug": "cbse9-fundamental-unit-of-life", "title": "The Fundamental Unit of Life for CBSE Class 9: Cell Structure Made Simple", "subject": "Science"},
    {"slug": "cbse9-tissues", "title": "Tissues for CBSE Class 9: Plant and Animal Tissues Explained with Diagrams", "subject": "Science"},
    {"slug": "cbse9-diversity-in-living-organisms", "title": "Diversity in Living Organisms for CBSE Class 9: Classification Made Easy", "subject": "Science"},
    {"slug": "cbse9-motion", "title": "Motion for CBSE Class 9: Distance, Displacement and Graphs Simplified", "subject": "Science"},
    {"slug": "cbse9-force-and-laws-of-motion", "title": "Force and Laws of Motion for CBSE Class 9: Newton's Laws with Examples", "subject": "Science"},
    {"slug": "cbse9-gravitation", "title": "Gravitation for CBSE Class 9: Universal Law and Numerical Problems", "subject": "Science"},
    {"slug": "cbse9-work-and-energy", "title": "Work and Energy for CBSE Class 9: Formulas and Common Exam Mistakes", "subject": "Science"},
    {"slug": "cbse9-sound", "title": "Sound for CBSE Class 9: Wave Properties, Echo and Human Ear", "subject": "Science"},
    {"slug": "cbse9-natural-resources", "title": "Natural Resources for CBSE Class 9: Air, Water and Soil Chapter Guide", "subject": "Science"},
    {"slug": "cbse9-improvement-in-food-resources", "title": "Improvement in Food Resources for CBSE Class 9: Crops and Animal Husbandry", "subject": "Science"},
    {"slug": "cbse9-number-systems", "title": "Number Systems for CBSE Class 9 Maths: Rational, Irrational and Real Numbers", "subject": "Maths"},
    {"slug": "cbse9-polynomials", "title": "Polynomials for CBSE Class 9 Maths: Factor Theorem and Identities Explained", "subject": "Maths"},
    {"slug": "cbse9-coordinate-geometry", "title": "Coordinate Geometry for CBSE Class 9: Plotting Points the Right Way", "subject": "Maths"},
    {"slug": "cbse9-linear-equations-two-variables", "title": "Linear Equations in Two Variables for CBSE Class 9: Complete Chapter Guide", "subject": "Maths"},
    {"slug": "cbse9-euclids-geometry", "title": "Euclid's Geometry for CBSE Class 9: Axioms, Postulates and Proofs", "subject": "Maths"},
    {"slug": "cbse9-lines-and-angles", "title": "Lines and Angles for CBSE Class 9: Theorems You Must Memorise", "subject": "Maths"},
    {"slug": "cbse9-triangles", "title": "Triangles for CBSE Class 9: Congruence Rules with Solved Examples", "subject": "Maths"},
    {"slug": "cbse9-quadrilaterals", "title": "Quadrilaterals for CBSE Class 9: Properties and Proof-Based Questions", "subject": "Maths"},
    {"slug": "cbse9-circles", "title": "Circles for CBSE Class 9: Chord and Angle Theorems Simplified", "subject": "Maths"},
    {"slug": "cbse9-herons-formula", "title": "Heron's Formula for CBSE Class 9: Area of Triangles Without Height", "subject": "Maths"},
    {"slug": "cbse9-surface-areas-volumes", "title": "Surface Areas and Volumes for CBSE Class 9: Formula Sheet and Tricks", "subject": "Maths"},
    {"slug": "cbse9-statistics", "title": "Statistics for CBSE Class 9: Mean, Median, Mode and Graphs", "subject": "Maths"},
    {"slug": "cbse9-probability", "title": "Probability for CBSE Class 9: Basics Every Student Must Know", "subject": "Maths"},
    {"slug": "cbse9-french-revolution", "title": "The French Revolution for CBSE Class 9 History: Causes, Events and Impact", "subject": "History"},
    {"slug": "cbse9-socialism-in-europe-russian-revolution", "title": "Socialism in Europe and the Russian Revolution for CBSE Class 9: Complete Notes", "subject": "History"},
    {"slug": "cbse9-nazism-and-hitler", "title": "Nazism and the Rise of Hitler for CBSE Class 9: Key Events Explained", "subject": "History"},
    {"slug": "cbse9-forest-society-and-colonialism", "title": "Forest Society and Colonialism for CBSE Class 9: Chapter Summary and Questions", "subject": "History"},
    {"slug": "cbse9-pastoralists-in-the-modern-world", "title": "Pastoralists in the Modern World for CBSE Class 9: Complete Chapter Guide", "subject": "History"},
    {"slug": "cbse9-india-size-and-location", "title": "India Size and Location for CBSE Class 9 Geography: Maps and Key Facts", "subject": "Geography"},
    {"slug": "cbse9-physical-features-of-india", "title": "Physical Features of India for CBSE Class 9: Mountains, Plains and Plateaus", "subject": "Geography"},
    {"slug": "cbse9-drainage", "title": "Drainage for CBSE Class 9 Geography: Rivers and River Systems of India", "subject": "Geography"},
    {"slug": "cbse9-climate", "title": "Climate for CBSE Class 9 Geography: Monsoon and Seasons Explained", "subject": "Geography"},
    {"slug": "cbse9-natural-vegetation-and-wildlife", "title": "Natural Vegetation and Wildlife for CBSE Class 9: Complete Notes", "subject": "Geography"},
    {"slug": "cbse9-population", "title": "Population for CBSE Class 9 Geography: Density, Growth and Distribution", "subject": "Geography"},
    {"slug": "cbse9-democracy-in-the-contemporary-world", "title": "What is Democracy Why Democracy for CBSE Class 9: Key Concepts", "subject": "Civics"},
    {"slug": "cbse9-constitutional-design", "title": "Constitutional Design for CBSE Class 9 Civics: How India's Constitution Was Made", "subject": "Civics"},
    {"slug": "cbse9-electoral-politics", "title": "Electoral Politics for CBSE Class 9: Elections and Democracy Explained", "subject": "Civics"},
    {"slug": "cbse9-working-of-institutions", "title": "Working of Institutions for CBSE Class 9: Parliament, PM and Judiciary", "subject": "Civics"},
    {"slug": "cbse9-democratic-rights", "title": "Democratic Rights for CBSE Class 9 Civics: Fundamental Rights Explained", "subject": "Civics"},
    {"slug": "cbse9-story-of-village-palampur", "title": "The Story of Village Palampur for CBSE Class 9 Economics: Complete Guide", "subject": "Economics"},
    {"slug": "cbse9-people-as-resource", "title": "People as Resource for CBSE Class 9 Economics: Chapter Notes and Questions", "subject": "Economics"},
    {"slug": "cbse9-poverty-as-a-challenge", "title": "Poverty as a Challenge for CBSE Class 9 Economics: Causes and Solutions", "subject": "Economics"},
    {"slug": "cbse9-food-security-in-india", "title": "Food Security in India for CBSE Class 9 Economics: Complete Chapter Guide", "subject": "Economics"},
    {"slug": "cbse9-board-exam-time-table-strategy", "title": "CBSE Class 9 Annual Exam Strategy: How to Plan Your Last 60 Days", "subject": "Strategy"},
    {"slug": "cbse9-how-to-score-90-percent", "title": "How to Score 90%+ in CBSE Class 9: A Realistic Study Plan", "subject": "Strategy"},
]


def get_today_topic():
    day = datetime.now().timetuple().tm_yday
    return TOPICS[day % len(TOPICS)]


def generate_article_html(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%B %d, %Y")
    slug = topic["slug"]
    title = topic["title"]
    subject = topic["subject"]

    prompt = (
        "Write a complete, standalone HTML article page for cbseclass9.com, "
        "a CBSE Class 9 study resource site.\n\n"
        f"Topic: {title}\n"
        f"Subject: {subject}\n"
        f"Slug: {slug}\n"
        f"Date: {today}\n\n"
        "Requirements:\n"
        f"- Title tag: {title} | CBSEClass9\n"
        "- Add a compelling 140-155 char meta description\n"
        f"- Canonical URL: https://cbseclass9.com/{slug}.html\n"
        "- Include Google Fonts 'Plus Jakarta Sans' link\n"
        "- Nav with links back to /\n"
        "- Article hero section with dark purple gradient background (#2E1065 to #5B21B6), subject tag badge, h1 title, date\n"
        "- Body: 800-1100 words, NCERT-grounded, exam-specific content for a CBSE Class 9 student\n"
        "- 3-4 H2 sections with specific NCERT chapter references and exam patterns\n"
        "- 1 highlight-box (background #F5F3FF, left border #7C3AED) with a key tip or common mistake\n"
        "- 1 CTA box linking to https://padhle.in mentioning Padhle Yoddha (Rs.2,000-3,000 mass batch for Class 9-10, daily live classes, study material) as the recommended coaching option\n"
        "- Footer mentioning Padhle Yoddha as the recommended affordable coaching\n"
        "- All inline styles as needed, purple theme (#5B21B6, #7C3AED)\n\n"
        "Return ONLY the complete HTML. No markdown fences, no commentary."
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    html = message.content[0].text.strip()
    for fence in ["```html", "```"]:
        if html.startswith(fence):
            html = html[len(fence):]
    if html.endswith("```"):
        html = html[:-3]
    return html.strip()


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set.")
        sys.exit(1)

    topic = get_today_topic()
    filename = f"{topic['slug']}.html"
    today_str = datetime.now().strftime("%Y-%m-%d")

    print(f"Topic: {topic['title']}")
    print(f"Output: {filename}")

    if os.path.exists(filename):
        print(f"{filename} already exists - skipping.")
        sys.exit(0)

    print("Calling Claude API...")
    html = generate_article_html(topic)
    html = add_byline(html, datetime.now().strftime("%B %d, %Y"))

    url = f"https://{DOMAIN}/{filename}"
    title = topic["title"]
    description = su.extract_description(html, title)

    tagged_html = su.publish_article(
        article_html=html, site_name=SITE_NAME, domain=DOMAIN,
        canonical_url=url, title=title, description=description,
        date_iso=today_str, category=topic["subject"],
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(tagged_html)
    print(f"Saved {filename} ({len(tagged_html):,} bytes)")
    print("SEO tags injected, manifest/sitemap/homepage/archive rebuilt")
    print("Done!")


if __name__ == "__main__":
    main()
