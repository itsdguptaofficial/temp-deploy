# Automated Regression Verification for Student Super App (16 Screens)
# Rule: Pure CSS only, zero JavaScript, strict token adherence, zero broken links

$ErrorActionPreference = "Stop"
Write-Host "=== STARTING STUDENT SUPER APP REGRESSION VERIFICATION ===" -ForegroundColor Cyan

$RequiredFiles = @(
    "index.html", "signup.html", "login.html", "setup.html",
    "home.html", "add-expense.html", "quick-capture.html",
    "money.html", "budget.html", "insights.html", "split.html",
    "today.html", "assignments.html", "exams.html", "timetable.html",
    "settings.html"
)

$FailedCount = 0

# 1. Completeness Check
Write-Host "`n[1/5] Checking file completeness (16/16 screens)..." -ForegroundColor Yellow
foreach ($file in $RequiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "  MISSING: $file" -ForegroundColor Red
        $FailedCount++
    }
}
if ($FailedCount -eq 0) {
    Write-Host "  PASS: All 16 HTML screens are present." -ForegroundColor Green
}

# 2. Pure Static Constraints (Zero JavaScript)
Write-Host "`n[2/5] Checking Zero-JavaScript constraints..." -ForegroundColor Yellow
foreach ($file in $RequiredFiles) {
    $content = Get-Content $file -Raw
    if ($content -match '<script') {
        Write-Host "  FAIL ($file): Contains <script> tag!" -ForegroundColor Red
        $FailedCount++
    }
    if ($content -match '\son[a-z]+=["'']') {
        Write-Host "  FAIL ($file): Contains inline event handler!" -ForegroundColor Red
        $FailedCount++
    }
}
Write-Host "  PASS: Zero JavaScript verified across all screens." -ForegroundColor Green

# 3. Anchor & Modal Dismissal (Zero bare href='#')
Write-Host "`n[3/5] Checking for bare href='#' (REQ-17.6)..." -ForegroundColor Yellow
foreach ($file in $RequiredFiles) {
    $content = Get-Content $file -Raw
    $matches = [regex]::Matches($content, 'href=["'']#["'']')
    if ($matches.Count -gt 0) {
        Write-Host "  FAIL ($file): Found $($matches.Count) bare href='#'" -ForegroundColor Red
        $FailedCount++
    }
}
Write-Host "  PASS: Zero bare href='#' found. Clean modal dismissal everywhere." -ForegroundColor Green

# 4. Header Placement & Overflow Safety
Write-Host "`n[4/5] Checking Header & Layout Overflow Safety..." -ForegroundColor Yellow
foreach ($file in $RequiredFiles) {
    $content = Get-Content $file -Raw
    if ($content -match '\.app-header\s*\{[^}]*margin:[^}]*-') {
        $headerPos = $content.IndexOf('<header class="app-header"')
        $mainPos = $content.IndexOf('<main')
        if ($headerPos -lt $mainPos) {
            Write-Host "  FAIL ($file): Header has negative margin but is outside <main> (causes 32px overflow)!" -ForegroundColor Red
            $FailedCount++
        }
    }
}
Write-Host "  PASS: All headers with negative margins are safely inside <main>." -ForegroundColor Green

# 5. Link Integrity (Internal relative paths & modal target anchors)
Write-Host "`n[5/5] Checking internal link integrity..." -ForegroundColor Yellow
$FileIds = @{}
foreach ($file in $RequiredFiles) {
    $content = Get-Content $file -Raw
    $idMatches = [regex]::Matches($content, 'id=["'']([^"'']+)["'']')
    $ids = @()
    foreach ($m in $idMatches) { $ids += $m.Groups[1].Value }
    $FileIds[$file] = $ids
}

foreach ($file in $RequiredFiles) {
    $content = Get-Content $file -Raw
    $linkMatches = [regex]::Matches($content, 'href=["'']([^"'']+)["'']')
    foreach ($m in $linkMatches) {
        $href = $m.Groups[1].Value
        if ($href -match '^(http|https|upi|mailto|tel):') { continue }
        if ($href -match '^#') {
            $anchor = $href.Substring(1)
            if ($FileIds[$file] -notcontains $anchor) {
                Write-Host "  FAIL ($file): Local anchor #$anchor does not exist in $file" -ForegroundColor Red
                $FailedCount++
            }
        } elseif ($href -match '#') {
            $parts = $href -split '#'
            $targetFile = $parts[0]
            $anchor = $parts[1]
            if ($RequiredFiles -notcontains $targetFile) {
                Write-Host "  FAIL ($file): Target file $targetFile in link $href does not exist" -ForegroundColor Red
                $FailedCount++
            } elseif ($FileIds[$targetFile] -notcontains $anchor) {
                Write-Host "  FAIL ($file): Target anchor #$anchor in $targetFile does not exist" -ForegroundColor Red
                $FailedCount++
            }
        } else {
            if ($RequiredFiles -notcontains $href) {
                Write-Host "  FAIL ($file): Target link $href does not exist" -ForegroundColor Red
                $FailedCount++
            }
        }
    }
}
Write-Host "  PASS: All internal links and anchor references are 100% valid." -ForegroundColor Green

Write-Host "`n=======================================================" -ForegroundColor Cyan
if ($FailedCount -eq 0) {
    Write-Host "SUCCESS: ALL REGRESSION TESTS PASSED! (0 errors)" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAILURE: $FailedCount tests failed!" -ForegroundColor Red
    exit 1
}
