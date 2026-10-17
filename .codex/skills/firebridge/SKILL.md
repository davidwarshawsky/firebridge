---
name: firebridge
description: Scrape, search, crawl, and map web pages using the remote Firecrawl MCP service. Use when you need to extract clean markdown from a URL, search the web with scraping, crawl a site for docs, or map domain URLs.
---

# Firecrawl Remote MCP CLI (`firebridge`)

`firebridge` is a lightweight, token-efficient command-line interface to the official remote Firecrawl MCP service (`https://mcp.firecrawl.dev/v2/mcp`).

Rather than configuring local Node.js MCP servers or dumping full tool schemas into agent context up front, query `firebridge` dynamically to discover tools, scrape clean markdown, search the web, crawl documentation, and map websites.

## Pre-requisite / Installation Check

1. Verify `FIRECRAWL_API_KEY` is set in the environment:
```bash
echo "${FIRECRAWL_API_KEY:?FIRECRAWL_API_KEY is not set. Run: export FIRECRAWL_API_KEY='your-key'}"
```

2. Check if the CLI is available in the environment:
```bash
which firebridge || command -v firebridge || Get-Command firebridge
```

**If `firebridge` is not installed**, refer to [INSTALL.md](INSTALL.md) or install it immediately:
- **Fastest via `uv`:** `uv tool install git+https://github.com/davidwarshawsky/firebridge`
- **On-the-fly execution via `uvx`:** prefix commands with `uvx --from git+https://github.com/davidwarshawsky/firebridge firebridge ...`
- **Via `pipx` or `pip`:** `pipx install git+https://github.com/davidwarshawsky/firebridge.git` or `pip install git+https://github.com/davidwarshawsky/firebridge.git`

## When to Use

Use `firebridge` whenever you need:
- Extracting clean Markdown or HTML from a specific URL without browser overhead
- Stripping headers, footers, and sidebars (`--only-main`)
- Searching the web and optionally scraping all resulting pages (`--scrape`)
- Mapping all URLs across an entire domain or documentation section
- Recursively crawling documentation sites

## Workflow & Commands

### 1. Discover Available Capabilities
Fetch available tools directly from the remote Firecrawl MCP endpoint:
```bash
firebridge --help
```

### 2. Inspect Tool Instructions On-Demand (Token Saver)
Retrieve the exact description, schema, and parameter guidance for a specific tool:
```bash
firebridge --tool firecrawl_scrape description
firebridge --tool firecrawl_search description
firebridge --tool firecrawl_crawl description
firebridge --tool firecrawl_map description
```

### 3. Scrape Webpage to Markdown
Convert any webpage into clean Markdown:
```bash
firebridge scrape "https://example.com/article"
```

Extract only the main content:
```bash
firebridge scrape "https://example.com/article" --only-main
```

### 4. Search the Web
Search and retrieve snippets:
```bash
firebridge search "Python uv tool tutorial" -n 5
```

Search and scrape full Markdown for each result:
```bash
firebridge search "AWS Bedrock Converse API Python" -n 3 --scrape
```

### 5. Map Website URLs
Discover links on a site:
```bash
firebridge map "https://docs.python.org" -n 50
firebridge map "https://docs.python.org" --search "library"
```

### 6. Crawl Documentation
Crawl a site or sub-tree:
```bash
firebridge crawl "https://example.com/docs" -n 10
```

### 7. Call Any Tool Directly
Execute raw JSON tool calls against the Firecrawl MCP server:
```bash
firebridge call firecrawl_credit_usage '{}'
```
