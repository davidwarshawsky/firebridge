# firebridge: Firecrawl Remote MCP CLI Client

`firebridge` is a lightweight, token-efficient command-line interface for the official remote [Firecrawl MCP Server](https://mcp.firecrawl.dev/v2/mcp).

Rather than managing local Node.js daemon processes, editing complex JSON config files, or dumping hundreds of lines of MCP schemas into an agent's initial prompt, `firebridge` provides a fast CLI with on-demand tool discovery, inspection, scraping, crawling, searching, and mapping.

- **Zero third-party dependencies:** Pure standard-library Python 3 (`urllib.request`, `json`, `argparse`).
- **Cross-platform:** Runs on macOS, Linux, and Windows.
- **Token-saver architecture:** Agents query only the tool descriptions they need when they need them.
- **Dedicated subcommands:** High-level shortcuts for `scrape`, `search`, `crawl`, and `map`, plus a raw JSON `call` command for any current or future Firecrawl MCP tool.

---

## Prerequisites

`firebridge` requires a Firecrawl API key. Get one from [Firecrawl](https://firecrawl.dev/app/api-keys) and set it in your environment:

```bash
export FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

On Windows PowerShell:
```powershell
$env:FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

---

## Installation

### Option 1: Install with `uv` (Recommended)
```bash
uv tool install git+https://github.com/davidwarshawsky/firebridge
```

### Option 2: Run directly with `uvx` (No install required)
```bash
uvx --from git+https://github.com/davidwarshawsky/firebridge firebridge --help
```

### Option 3: Install with `pipx`
```bash
pipx install git+https://github.com/davidwarshawsky/firebridge.git
```

### Option 4: Install with `pip`
```bash
pip install git+https://github.com/davidwarshawsky/firebridge.git
```

### Option 5: Local Clone & Editable Install
```bash
git clone https://github.com/davidwarshawsky/firebridge.git
cd firebridge
pip install -e .
```

---

## Quick Verification

Check if `firebridge` is installed and ready:

```bash
which firebridge || command -v firebridge || Get-Command firebridge
```

Inspect tool list:
```bash
firebridge --help
```

---

## Usage

### 1. Discover Tools Dynamically
Query the remote Firecrawl MCP server for available tools:
```bash
firebridge
```

### 2. Inspect Tool Instructions (Token Saver)
Read the schema and guidance for a specific tool only when you need it:
```bash
firebridge --tool firecrawl_scrape description
firebridge --tool firecrawl_search description
firebridge --tool firecrawl_crawl description
firebridge --tool firecrawl_map description
```

### 3. Scrape Webpages to Clean Markdown
Scrape a single URL to Markdown:
```bash
firebridge scrape "https://example.com"
```

Extract only the main article content (strip navigation, header, and footer):
```bash
firebridge scrape "https://news.ycombinator.com" --only-main
```

Output raw JSON containing metadata and markdown:
```bash
firebridge scrape "https://example.com" --json
```

### 4. Search the Web
Search the web with Firecrawl:
```bash
firebridge search "Python packaging pyproject.toml hatchling" -n 5
```

Search and immediately scrape markdown content from all search results:
```bash
firebridge search "FastAPI tutorial" -n 3 --scrape
```

### 5. Map Website URLs
Discover all linked URLs on a domain:
```bash
firebridge map "https://docs.python.org" -n 50
```

Filter discovered URLs by subpath or keyword:
```bash
firebridge map "https://docs.python.org" --search "library/urllib"
```

### 6. Crawl Site
Recursively crawl a website:
```bash
firebridge crawl "https://example.com" -n 10
```

### 7. Generic MCP Tool Caller
Invoke any Firecrawl MCP tool directly using JSON arguments:
```bash
firebridge call firecrawl_credit_usage '{}'
```

---

## Agent Skills Support

Ready-to-use agent skills are included in this repository:
- **GitHub Copilot:** `.github/skills/firebridge/`
- **Claude Code:** `.claude/skills/firebridge/`
- **OpenAI Codex:** `.codex/skills/firebridge/`
- **Agents Standard:** `.agents/skills/firebridge/`

Each skill directory includes a self-contained `INSTALL.md` and pre-flight checks in `SKILL.md` so that AI agents can detect if `firebridge` is missing, install it automatically, and run scraping/crawling tasks without human intervention.

---

# TLS / Enterprise CA Certificates

`firebridge` always verifies HTTPS certificates. If your network uses an enterprise TLS inspection proxy, provide its trusted CA bundle through the standard Python environment variables:

```powershell
$env:SSL_CERT_FILE = 'C:\path\to\corporate-ca-bundle.pem'
# Or use a directory containing hashed CA certificates:
$env:SSL_CERT_DIR = 'C:\path\to\corporate-ca-directory'
```

Set these variables before running `firebridge`. Do not disable certificate verification. If validation fails, the CLI reports that `SSL_CERT_FILE` or `SSL_CERT_DIR` can be set.
## License

MIT
