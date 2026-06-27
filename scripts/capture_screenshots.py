"""Capture screenshots of the deployed Streamlit app for README documentation."""

from __future__ import annotations

import html
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

APP_URL = "https://multi-agentresearch-byabhinandpv.streamlit.app/"
SCREENSHOT_DIR = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
VIEWPORT = {"width": 1440, "height": 900}


def capture_streamlit_screenshots(topic: str = "renewable energy") -> list[Path]:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(8000)

        frame = page
        for candidate in page.frames:
            if candidate != page.main_frame and candidate.url and "streamlit" in candidate.url:
                frame = candidate
                break

        home_path = SCREENSHOT_DIR / "streamlit-home.png"
        page.screenshot(path=str(home_path), full_page=True)
        saved.append(home_path)
        print(f"Saved {home_path}")

        topic_input = frame.locator(
            'input[placeholder*="Quantum"], input[aria-label*="Research"], input[type="text"]'
        ).first
        topic_input.wait_for(state="visible", timeout=60_000)
        topic_input.fill(topic)

        form_path = SCREENSHOT_DIR / "streamlit-form-filled.png"
        page.screenshot(path=str(form_path), full_page=True)
        saved.append(form_path)
        print(f"Saved {form_path}")

        frame.get_by_role("button", name="Generate Report").click()

        running_path = SCREENSHOT_DIR / "streamlit-generating.png"
        page.wait_for_timeout(4000)
        page.screenshot(path=str(running_path), full_page=True)
        saved.append(running_path)
        print(f"Saved {running_path}")

        try:
            frame.get_by_text("Report generated successfully", exact=False).wait_for(
                timeout=300_000
            )
            result_path = SCREENSHOT_DIR / "streamlit-report-result.png"
            page.screenshot(path=str(result_path), full_page=True)
            saved.append(result_path)
            print(f"Saved {result_path}")
        except PlaywrightTimeoutError:
            error_path = SCREENSHOT_DIR / "streamlit-error.png"
            page.screenshot(path=str(error_path), full_page=True)
            saved.append(error_path)
            print(f"Report generation timed out; saved {error_path}", file=sys.stderr)

        browser.close()

    return saved


def capture_cli_output_image(title: str, output_text: str, filename: str) -> Path:
    """Render terminal output as a PNG for README display."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    escaped = html.escape(output_text)
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #1e1e1e;
      font-family: Consolas, "Courier New", monospace;
    }}
    .window {{
      background: #0c0c0c;
      border-radius: 8px;
      border: 1px solid #333;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
      overflow: hidden;
    }}
    .titlebar {{
      background: #2d2d2d;
      color: #d4d4d4;
      padding: 10px 16px;
      font-size: 14px;
      border-bottom: 1px solid #444;
    }}
    pre {{
      margin: 0;
      padding: 20px;
      color: #cccccc;
      font-size: 13px;
      line-height: 1.45;
      white-space: pre-wrap;
      word-break: break-word;
    }}
  </style>
</head>
<body>
  <div class="window">
    <div class="titlebar">{html.escape(title)}</div>
    <pre>{escaped}</pre>
  </div>
</body>
</html>"""

    output_path = SCREENSHOT_DIR / filename
    html_path = SCREENSHOT_DIR / f"{Path(filename).stem}.html"
    html_path.write_text(html_content, encoding="utf-8")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.goto(html_path.as_uri())
        page.locator("pre").screenshot(path=str(output_path))
        browser.close()

    html_path.unlink(missing_ok=True)
    print(f"Saved {output_path}")
    return output_path


if __name__ == "__main__":
    capture_streamlit_screenshots()
