#!/usr/bin/env python3
"""
App Store Screenshot Exporter for MManager
==========================================
Generates PNG screenshots at exact App Store required sizes.

Usage:
  pip install playwright --break-system-packages
  playwright install chromium
  python3 screenshot_export.py

Output:
  ./exports/
    ├── 6.9/    (1320x2868)
    ├── 6.5/    (1284x2778)
    └── 5.5/    (1242x2208)
"""

import os
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Please install playwright first:")
    print("  pip install playwright --break-system-packages")
    print("  playwright install chromium")
    sys.exit(1)

SIZES = {
    "6.9": (1320, 2868),
    "6.5": (1284, 2778),
    "5.5": (1242, 2208),
}

SCREENSHOT_IDS = ["ss1", "ss2", "ss3", "ss4", "ss5", "ss6"]
SCREENSHOT_NAMES = [
    "01_calendar",
    "02_receipt_scan",
    "03_statistics",
    "04_categories",
    "05_widget",
    "06_auto_input",
]

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(script_dir, "screenshot_generator.html")
    export_dir = os.path.join(script_dir, "exports")

    if not os.path.exists(html_path):
        print(f"Error: {html_path} not found")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for size_name, (width, height) in SIZES.items():
            size_dir = os.path.join(export_dir, size_name)
            os.makedirs(size_dir, exist_ok=True)

            print(f"\n--- iPhone {size_name}\" ({width}x{height}) ---")

            for ss_id, ss_name in zip(SCREENSHOT_IDS, SCREENSHOT_NAMES):
                # Create a page with exact device dimensions
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                page.goto(f"file://{html_path}")

                # Inject CSS to make the target screenshot fill the viewport exactly
                page.evaluate(f"""
                    const el = document.getElementById('{ss_id}');
                    if (el) {{
                        // Hide everything else
                        document.querySelectorAll('.screenshot-wrapper').forEach(w => w.style.display = 'none');
                        document.querySelector('.controls').style.display = 'none';
                        document.querySelector('.info').style.display = 'none';

                        // Show and resize target
                        el.closest('.screenshot-wrapper').style.display = 'block';
                        el.style.width = '{width}px';
                        el.style.height = '{height}px';
                        el.style.borderRadius = '0';
                        el.style.boxShadow = 'none';

                        // Scale font sizes proportionally
                        const scale = {width} / 440;
                        el.style.fontSize = scale * 100 + '%';

                        // Remove wrapper padding
                        document.querySelector('.screenshots-grid').style.padding = '0';
                        document.querySelector('.screenshots-grid').style.gap = '0';
                        document.body.style.padding = '0';
                        document.body.style.margin = '0';
                        document.body.style.background = 'transparent';
                    }}
                """)

                page.wait_for_timeout(500)

                output_path = os.path.join(size_dir, f"{ss_name}.png")
                el = page.query_selector(f"#{ss_id}")
                if el:
                    el.screenshot(path=output_path)
                    print(f"  ✓ {ss_name}.png")
                else:
                    print(f"  ✗ {ss_name} - element not found")

                page.close()

        browser.close()

    print(f"\n✅ All screenshots exported to: {export_dir}")


if __name__ == "__main__":
    main()
