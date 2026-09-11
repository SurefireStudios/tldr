# SessionStart hook (PowerShell fallback): injects the full tldr ruleset when the
# user has opted in by creating $env:CLAUDE_CONFIG_DIR\.tldr-always
# (default ~\.claude\.tldr-always).
#
# The Node implementation in always-on.mjs is the primary path and works on all
# three platforms. This script exists for Windows environments without Node on PATH.
#
# Never blocks session start: always exits 0.

$ErrorActionPreference = 'SilentlyContinue'

# The skill body contains non-ASCII punctuation (em-dashes, curly quotes). Without
# this the console encoding mangles them and the three hook implementations stop
# agreeing byte for byte (see tests/test_always_on_hooks.py).
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    $configDir = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
    $flagPath = Join-Path $configDir '.tldr-always'

    if (-not (Test-Path -LiteralPath $flagPath)) { exit 0 }

    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $skillPath = Join-Path $scriptDir '..\skills\tldr\SKILL.md'

    if (-not (Test-Path -LiteralPath $skillPath)) { exit 0 }

    $depth = (Get-Content -LiteralPath $flagPath -Raw) -replace '\s', ''
    if ($depth -notin @('0', '1', '3', '5')) { $depth = '3' }

    # -Encoding UTF8 is required: Windows PowerShell 5.1 defaults to the system ANSI
    # codepage, which turns the skill's em-dashes into mojibake before they are
    # re-encoded on the way out.
    $content = Get-Content -LiteralPath $skillPath -Raw -Encoding UTF8
    # Strip a leading YAML frontmatter block (--- ... --- at the very top of file).
    $body = [regex]::Replace($content, '^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)', '')
    $body = $body -replace '(\r?\n)+$', ''

    $header = "TLDR MODE ACTIVE (always-on). The ruleset below applies to every response. " +
              "Depth dial is set to $depth. " +
              '"stop tldr" or "normal mode" turns it off for this session; ' +
              "delete $flagPath to turn always-on off for good."

    Write-Output "$header`n`n$body"
} catch {
    # Never block session start.
}

exit 0
