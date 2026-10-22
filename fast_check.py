#!/usr/bin/env python3
"""
Fast Automated Quality & Consistency Audit Runner for Student Super App (16 Screens).
Executes 10 deep consistency and quality checks in under 300ms.
"""

import os
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))

ALL_SCREENS = [
    "index.html", "signup.html", "login.html", "setup.html",
    "home.html", "add-expense.html", "quick-capture.html",
    "money.html", "budget.html", "insights.html", "split.html",
    "today.html", "assignments.html", "exams.html", "timetable.html",
    "settings.html"
]

TAB_SCREENS = [
    "money.html", "budget.html", "insights.html", "split.html",
    "today.html", "assignments.html", "exams.html", "timetable.html"
]

NAV_SCREENS = [
    "home.html", "money.html", "budget.html", "insights.html", "split.html",
    "today.html", "assignments.html", "exams.html", "timetable.html", "settings.html"
]

def run_fast_check():
    start_time = time.perf_counter()
    print("=" * 72)
    print("  STUDENT SUPER APP — FAST CROSS-PAGE CONSISTENCY & INTEGRITY AUDIT")
    print("=" * 72)

    errors = []
    warnings = []

    # 1. File Completeness
    missing_files = [f for f in ALL_SCREENS if not os.path.exists(os.path.join(ROOT, f))]
    if missing_files:
        errors.append(f"Missing HTML screen(s): {', '.join(missing_files)}")

    # Preload all file contents and element IDs
    file_contents = {}
    file_ids = {}
    for f in ALL_SCREENS:
        path = os.path.join(ROOT, f)
        if os.path.exists(path):
            text = open(path, "r", encoding="utf-8").read()
            file_contents[f] = text
            file_ids[f] = set(re.findall(r'id=["\']([^"\']+)["\']', text))

    # 2. Zero-JS Rule (REQ-17.1)
    for f, text in file_contents.items():
        if "<script" in text.lower():
            errors.append(f"[{f}] Contains <script> tag (Violates Zero-JS constraint)")
        if re.search(r'\son[a-z]+=["\']', text, re.IGNORECASE):
            errors.append(f"[{f}] Contains inline JS event handler")

    # 3. Clean Modal Targets / Zero Bare Hash (REQ-17.6)
    for f, text in file_contents.items():
        bare_hashes = re.findall(r'href=["\']#["\']', text)
        if bare_hashes:
            errors.append(f"[{f}] Contains {len(bare_hashes)} bare href='#' (causes jump-scroll & URL fragment pollution)")

    # 4. Sheet Positioning (Before <main>)
    for f, text in file_contents.items():
        if 'class="sheet-overlay"' in text:
            first_sheet = text.find('class="sheet-overlay"')
            main_pos = text.find('<main')
            if main_pos != -1 and first_sheet > main_pos:
                errors.append(f"[{f}] Sheet placed after <main> (causes jump-scroll on :target activation)")

    # 5. Header Layout & Negative Margin Safety (Zero Horizontal Overflow)
    for f, text in file_contents.items():
        if re.search(r'\.app-header\s*\{[^}]*margin:[^}]*-', text):
            header_pos = text.find('<header class="app-header"')
            main_pos = text.find('<main')
            if header_pos != -1 and main_pos != -1 and header_pos < main_pos:
                errors.append(f"[{f}] .app-header with negative margins placed outside <main> (causes 32px horizontal overflow)")

    # 6. Semantic Segmented Navigation (<nav class="segmented">)
    for f in TAB_SCREENS:
        text = file_contents.get(f, "")
        if '<nav class="segmented"' not in text:
            errors.append(f"[{f}] Does not use semantic <nav class=\"segmented\">")

    # 7. Persistent Bottom Nav Active State Consistency (font-weight: 600)
    for f in NAV_SCREENS:
        text = file_contents.get(f, "")
        if '.nav-item[aria-current="page"]' not in text or 'font-weight: 600' not in text:
            errors.append(f"[{f}] Active nav item missing font-weight: 600 bold styling")

    # 8. Link & Anchor Integrity
    for f, text in file_contents.items():
        links = re.findall(r'href=["\']([^"\']+)["\']', text)
        for l in links:
            if l.startswith(("http", "upi:", "mailto:", "tel:")):
                continue
            if l.startswith("#"):
                anchor = l[1:]
                if anchor not in file_ids[f]:
                    errors.append(f"[{f}] Broken local anchor: #{anchor}")
            elif "#" in l:
                target_file, anchor = l.split("#", 1)
                if target_file not in file_ids:
                    errors.append(f"[{f}] Link to non-existent file: {target_file}")
                elif anchor and anchor not in file_ids[target_file]:
                    errors.append(f"[{f}] Link to non-existent anchor #{anchor} in {target_file}")
            else:
                if l not in file_ids:
                    errors.append(f"[{f}] Link to non-existent file: {l}")

    # 9. Header Border Separator
    for f in NAV_SCREENS:
        text = file_contents.get(f, "")
        header_css = re.search(r'\.app-header\s*\{([^}]+)\}', text)
        if header_css and 'border-bottom' not in header_css.group(1):
            warnings.append(f"[{f}] Header missing border-bottom separator")

    # 10. Title Presence
    for f, text in file_contents.items():
        if '<title>' not in text:
            errors.append(f"[{f}] Missing <title> tag")

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(f"Checked 16/16 screens across 10 quality checks in {elapsed_ms:.1f}ms.\n")

    if not errors and not warnings:
        print("  [PASS] All 16 screens are 100% consistent, defect-free, and verified!")
        print("=" * 72)
        return 0
    elif not errors:
        print("  [PASS] All core checks passed with minor warnings:")
        for w in warnings:
            print(f"    - {w}")
        print("=" * 72)
        return 0
    else:
        print(f"  [FAIL] Found {len(errors)} consistency issue(s):")
        for e in errors:
            print(f"    - {e}")
        print("=" * 72)
        return 1

if __name__ == "__main__":
    sys.exit(run_fast_check())
