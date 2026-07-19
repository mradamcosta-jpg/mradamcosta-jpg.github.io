# Shared navbar definition for adam-costa.com.
# Used by build_site.py (site generation) and patch_nav.py (patching built pages).
# Edit dropdown entries here, then re-run build_site.py or patch_nav.py.

SECTIONS = [
    {
        "key": "ff",
        "label": "Financial freedom",
        "href": "financial-freedom/",
        "items": [
            ("financial-freedom/ff1-the-exact-roadmap/", "1. The exact roadmap"),
            ("financial-freedom/how-much-money-do-i-need-to-retire-at-40/", "2. How much do you need?"),
            ("financial-freedom/levels-of-financial-freedom/", "3. Levels of financial freedom"),
            ("financial-freedom/difference-between-assets-liabilities/", "4. Assets vs. liabilities"),
            ("financial-freedom/housing/", "5. Housing"),
            ("financial-freedom/taxes/", "6. Taxes"),
            ("financial-freedom/transportation/", "7. Transportation"),
            ("financial-freedom/ask-for-a-raise/", "8. Ask for a raise"),
            ("financial-freedom/work-remotely/", "9. Work remotely"),
            ("financial-freedom/creating-assets/", "10. Create assets"),
            ("financial-freedom/consulting/", "11. Become a consultant"),
            ("financial-freedom/buying-businesses/", "12. Buy businesses"),
            ("financial-freedom/investment-order/", "13. Investment order"),
            ("financial-freedom/asset-allocation/", "14. Asset allocation"),
            ("financial-freedom/build-wealth-automatically/", "15. Automate your investments"),
            ("financial-freedom/withdraw-your-money/", "16. Withdraw your money"),
        ],
    },
    {
        "key": "prod",
        "label": "Productivity",
        "href": "productivity/",
        "items": [
            ("productivity/introduction-what-youll-get-in-this-course/", "Introduction"),
            ("productivity/chapter-1-find-your-purpose/", "1. Find your purpose"),
            ("productivity/chapter-2-pinpoint-and-prioritize-your-goals/", "2. Pinpoint your goals"),
            ("productivity/chapter-3-optimize-your-workflow/", "3. Optimize your workflow"),
            ("productivity/chapter-4-maximize-your-willpower/", "4. Maximize your willpower"),
            ("productivity/chapter-5-build-rock-solid-routines/", "5. Build rock-solid routines"),
            ("productivity/chapter-6-block-distractions/", "6. Block distractions"),
            ("productivity/chapter-7-follow-through/", "7. Follow through"),
            ("productivity/conclusion-what-to-do-next/", "Conclusion"),
            ("productivity/additional-resources/", "More resources"),
        ],
    },
    {
        "key": "life",
        "label": "Life",
        "href": "life/",
        "items": [
            ("life/sleepless/", "Sleep(less)"),
            ("life/journey-through-the-gi-tract/", "Journey through the GI tract"),
            ("life/knots/", "Knots"),
            ("life/save-money-by-traveling/", "Quit yer job and travel"),
            ("life/media-appearances/", "Media appearances"),
        ],
    },
    {
        "key": "tools",
        "label": "Tools",
        "href": "/tools/",           # absolute: served by the separate `tools` repo
        "absolute": True,
        "items": [
            ("/tools/fire-calculator.html", "FIRE calculator"),
        ],
    },
]


def render_nav(rel, active=""):
    """Return the <nav> block. rel is '../' * depth ('' at root, '/' for 404 page)."""
    out = ["<nav>"]
    for s in SECTIONS:
        absolute = s.get("absolute", False)
        top = s["href"] if absolute else rel + s["href"]
        cls = ' class="active"' if s["key"] == active else ""
        out.append(f'      <div class="nav-item"><a href="{top}"{cls}>{s["label"]}</a>')
        out.append('        <div class="dropdown">')
        for href, label in s["items"]:
            full = href if href.startswith("/") else rel + href
            out.append(f'          <a href="{full}">{label}</a>')
        out.append("        </div>")
        out.append("      </div>")
    out.append("    </nav>")
    return "\n".join(out)
