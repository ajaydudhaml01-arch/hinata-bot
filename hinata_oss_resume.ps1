param(
  [switch]$NoCommit,
  [switch]$NoPush
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Say($text) {
  Write-Host "[Hinata OSS] $text" -ForegroundColor Cyan
}

Say "Resuming OSS upgrade from the point where the previous script stopped..."

if (-not (Test-Path ".git")) {
  throw "Run this from the root of your cloned hinata-bot repository."
}
if (-not (Test-Path "package.json")) {
  throw "package.json was not found."
}

$remote = (git remote get-url origin 2>$null)
if ($LASTEXITCODE -ne 0 -or $remote -notmatch "ajaydudhaml01-arch/hinata-bot") {
  throw "This does not look like ajaydudhaml01-arch/hinata-bot. Origin: $remote"
}

Say "Checking for obviously dangerous tracked secret filenames..."
$tracked = @(git ls-files)
$badTracked = @(
  $tracked | Where-Object {
    $_ -match '(^|/)(\.env|id_rsa|.*\.pem|.*\.p12|.*\.key)$' -and $_ -ne ".env.example"
  }
)

if ($badTracked.Count -gt 0) {
  Write-Host "WARNING: review these tracked files before pushing:" -ForegroundColor Red
  $badTracked | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
} else {
  Say "No obviously dangerous tracked secret filenames found."
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm was not found. Install Node.js/npm or run the remaining steps manually."
}

Say "Generating/updating package-lock.json..."
npm install --package-lock-only
if ($LASTEXITCODE -ne 0) {
  throw "npm could not generate package-lock.json."
}

Say "Running syntax check..."
npm run check
if ($LASTEXITCODE -ne 0) {
  throw "Syntax check failed. No commit was made."
}

Say "Running tests..."
npm test
if ($LASTEXITCODE -ne 0) {
  throw "Tests failed. No commit was made."
}

Say "Staging all OSS changes..."
git add -A

Write-Host ""
Write-Host "Changes ready to commit:" -ForegroundColor White
git status --short | Out-Host
Write-Host ""

if (-not $NoCommit) {
  $answer = Read-Host "Commit the OSS upgrade now? [Y/n]"
  if ([string]::IsNullOrWhiteSpace($answer) -or $answer -match '^[Yy]') {
    git commit -m "chore: prepare Hinata for open-source development"
    if ($LASTEXITCODE -ne 0) {
      throw "Git commit failed."
    }
    Say "Commit created."

    if (-not $NoPush) {
      $push = Read-Host "Push the commits to GitHub now? [Y/n]"
      if ([string]::IsNullOrWhiteSpace($push) -or $push -match '^[Yy]') {
        git push origin main
        if ($LASTEXITCODE -ne 0) {
          Write-Host "Push failed. Your commits are safe locally; push later from GitHub Desktop." -ForegroundColor Yellow
        } else {
          Say "Pushed to GitHub."
        }
      }
    }
  }
}

if (Get-Command gh -ErrorAction SilentlyContinue) {
  gh auth status *> $null
  if ($LASTEXITCODE -eq 0) {
    Say "Updating repository description/topics with GitHub CLI..."
    gh repo edit ajaydudhaml01-arch/hinata-bot `
      --description "Modular open-source Discord.js bot for moderation, tickets, leveling, dynamic voice channels, self-roles, and community utilities." `
      --add-topic discord-bot `
      --add-topic discord-js `
      --add-topic moderation `
      --add-topic tickets `
      --add-topic leveling `
      --add-topic self-hosted *> $null
  }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " Hinata OSS upgrade resume finished." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "If you used -NoPush, push afterward with:" -ForegroundColor White
Write-Host "  git push origin main" -ForegroundColor White
