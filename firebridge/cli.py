#!/usr/bin/env python3
"""firebridge - CLI for the Firecrawl Remote MCP Server.

Provides AI agents and developers with dynamic, token-efficient access to
Firecrawl web scraping, searching, crawling, mapping, and research via
https://mcp.firecrawl.dev/v2/mcp.

Zero third-party dependencies — runs on standard library Python 3.
Requires FIRECRAWL_API_KEY environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Any

MCP_URL = "https://mcp.firecrawl.dev/v2/mcp"
USER_AGENT = "Mozilla/5.0 (compatible; firebridge/0.1.0; +https://github.com/davidwarshawsky/firebridge)"


def ssl_context() -> ssl.SSLContext:
    """Build a verified TLS context using optional CA environment overrides."""
    return ssl.create_default_context(
        cafile=os.environ.get("SSL_CERT_FILE") or None,
        capath=os.environ.get("SSL_CERT_DIR") or None,
    )


def get_api_key() -> str:
    """Retrieve FIRECRAWL_API_KEY from environment or exit with error."""
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not key:
        sys.stderr.write(
            "Error: FIRECRAWL_API_KEY environment variable is not set.\n"
            "Please set it with: export FIRECRAWL_API_KEY=\"your-key-here\"\n"
        )
        sys.exit(1)
    return key


def rpc_request(method: str, params: dict[str, Any] | None = None, api_key: str | None = None) -> dict[str, Any]:
    """Execute a JSON-RPC 2.0 request against the Firecrawl MCP Server."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {},
    }
    data = json.dumps(payload).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": USER_AGENT,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(
        MCP_URL,
        data=data,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(req, timeout=120, context=ssl_context()) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(body)
            msg = err_json.get("error", {}).get("message") or err_json.get("detail") or body
        except Exception:
            msg = body
        sys.stderr.write(f"HTTP Error {exc.code} calling Firecrawl MCP Server: {msg}\n")
        sys.exit(1)
    except urllib.error.URLError as exc:
        message = str(exc.reason)
        if "CERTIFICATE_VERIFY_FAILED" in message:
            message += " Set SSL_CERT_FILE or SSL_CERT_DIR to a trusted CA bundle."
        sys.stderr.write(f"Network error connecting to Firecrawl MCP Server: {message}\n")
        sys.exit(1)
    except Exception as exc:
        sys.stderr.write(f"Unexpected error: {exc}\n")
        sys.exit(1)

    cleaned = raw.strip()
    if "data:" in cleaned:
        for line in cleaned.splitlines():
            line_stripped = line.strip()
            if line_stripped.startswith("data:"):
                json_part = line_stripped[len("data:"):].strip()
                try:
                    return json.loads(json_part)
                except Exception:
                    continue

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"Failed to decode response from Firecrawl MCP: {exc}\nRaw response:\n{raw}\n")
        sys.exit(1)


def list_tools(api_key: str | None = None) -> list[dict[str, Any]]:
    """List all available tools from the Firecrawl MCP server."""
    res = rpc_request("tools/list", api_key=api_key)
    if "error" in res:
        sys.stderr.write(f"RPC Error listing tools: {res['error']}\n")
        sys.exit(1)
    return res.get("result", {}).get("tools", [])


def print_tool_description(tool_name: str, tools: list[dict[str, Any]]) -> None:
    """Print the documentation and parameter schema for a specific tool."""
    target = tool_name.strip()
    match = None
    for t in tools:
        name = t.get("name", "")
        if name == target or name.removeprefix("firecrawl_") == target:
            match = t
            break

    if not match:
        available = [t.get("name") for t in tools]
        sys.stderr.write(f"Tool '{tool_name}' not found. Available tools: {', '.join(available)}\n")
        sys.exit(1)

    print(f"Tool: {match.get('name')} ({match.get('title', '')})")
    print(f"\nDescription:\n{match.get('description', '').strip()}\n")
    print("Input Schema:")
    print(json.dumps(match.get("inputSchema", {}), indent=2))


def format_output(content_list: list[dict[str, Any]]) -> None:
    """Format and print tool output nicely."""
    for item in content_list:
        if isinstance(item, dict):
            text = item.get("text", "")
            if text:
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict) and "markdown" in parsed:
                        print(parsed["markdown"])
                    else:
                        print(json.dumps(parsed, indent=2))
                except Exception:
                    print(text)
            else:
                print(json.dumps(item, indent=2))
        else:
            print(str(item))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="firebridge",
        description=(
            "firebridge - Token-efficient CLI for the Firecrawl Remote MCP Server.\n\n"
            "Scrape web pages to Markdown, crawl sites, search the web, and map URLs on demand\n"
            "without polluting agent context upfront. Requires FIRECRAWL_API_KEY environment variable.\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--tool",
        dest="tool_inspect",
        metavar="TOOL_NAME",
        help="Target tool name to inspect or run with an action (e.g. --tool firecrawl_scrape description)",
    )
    parser.add_argument(
        "action",
        nargs="?",
        help="Action: 'description' (when used with --tool), 'call' (generic tool caller), 'scrape', 'search', 'crawl', or 'map'",
    )
    parser.add_argument(
        "args",
        nargs="*",
        help="Arguments for action (e.g., URL, search query, or JSON parameter string)",
    )

    parsed, unknown = parser.parse_known_args()

    # 1. Handle tool inspection: firebridge --tool <name> description
    if parsed.tool_inspect:
        action = (parsed.action or "").lower()
        if action == "description":
            api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip() or None
            tools = list_tools(api_key=api_key)
            print_tool_description(parsed.tool_inspect, tools)
            return
        elif action == "call":
            tool_name = parsed.tool_inspect
            if not tool_name.startswith("firecrawl_"):
                tool_name = f"firecrawl_{tool_name}"
            api_key = get_api_key()
            args_str = " ".join(parsed.args) if parsed.args else "{}"
            try:
                call_args = json.loads(args_str) if args_str else {}
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"Invalid JSON arguments: {exc}\n")
                sys.exit(1)

            res = rpc_request("tools/call", {"name": tool_name, "arguments": call_args}, api_key=api_key)
            if "error" in res:
                sys.stderr.write(f"RPC Error calling {tool_name}: {json.dumps(res['error'], indent=2)}\n")
                sys.exit(1)
            content = res.get("result", {}).get("content", [])
            format_output(content)
            return
        else:
            sys.stderr.write(f"Unknown action '{action}' for --tool {parsed.tool_inspect}. Use 'description' or 'call'.\n")
            sys.exit(1)

    # 2. No action or help requested -> List all available tools dynamically
    if not parsed.action or parsed.action in ("--help", "-h", "help"):
        api_key = os.environ.get("FIRECRAWL_API_KEY", "").strip() or None
        tools = list_tools(api_key=api_key)
        print("Available tools from Firecrawl MCP Server (https://mcp.firecrawl.dev/v2/mcp):\n")
        for t in tools:
            name = t.get("name", "unknown")
            desc = t.get("description", "").strip().split("\n")[0]
            print(f"  • {name:28} - {desc}")
        print("\nCommands & Workflows:")
        print("  1. Inspect tool schema:       firebridge --tool <tool_name> description")
        print("  2. Scrape webpage to markdown: firebridge scrape <url> [--only-main]")
        print("  3. Search the web:            firebridge search \"<query>\" [-n 5] [--scrape]")
        print("  4. Map website URLs:          firebridge map <url> [-n 50]")
        print("  5. Crawl website:             firebridge crawl <url> [-n 10]")
        print("  6. Call any MCP tool raw:     firebridge call <tool_name> '{\"arg\": \"val\"}'")
        print("\nEnvironment:")
        print("  FIRECRAWL_API_KEY             Required for 'scrape', 'search', 'crawl', 'map', and 'call'")
        return

    action_lower = parsed.action.lower()

    # 3. Direct tool caller: firebridge call <tool_name> '{"key": "value"}'
    if action_lower == "call":
        if not parsed.args:
            sys.stderr.write("Usage: firebridge call <tool_name> [json_arguments]\n")
            sys.exit(1)
        tool_name = parsed.args[0]
        if not tool_name.startswith("firecrawl_"):
            tool_name = f"firecrawl_{tool_name}"

        api_key = get_api_key()
        raw_args = " ".join(parsed.args[1:]) if len(parsed.args) > 1 else "{}"
        try:
            call_args = json.loads(raw_args) if raw_args.strip() else {}
        except json.JSONDecodeError as exc:
            sys.stderr.write(f"Invalid JSON arguments: {exc}\n")
            sys.exit(1)

        res = rpc_request("tools/call", {"name": tool_name, "arguments": call_args}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"RPC Error calling {tool_name}: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        content = res.get("result", {}).get("content", [])
        format_output(content)
        return

    # 4. Scrape command: firebridge scrape <url> [--only-main] [--json]
    if action_lower == "scrape":
        scrape_parser = argparse.ArgumentParser(prog="firebridge scrape", description="Scrape a webpage and convert to clean markdown")
        scrape_parser.add_argument("url", help="Target URL to scrape")
        scrape_parser.add_argument("--only-main", action="store_true", help="Only return main body content, stripping nav and footer")
        scrape_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        s_args = scrape_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        params: dict[str, Any] = {"url": s_args.url}
        if s_args.only_main:
            params["onlyMainContent"] = True

        res = rpc_request("tools/call", {"name": "firecrawl_scrape", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Scrape error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if s_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_output(content)
        return

    # 5. Search command: firebridge search "query" [-n 5] [--scrape] [--json]
    if action_lower == "search":
        search_parser = argparse.ArgumentParser(prog="firebridge search", description="Search the web with Firecrawl")
        search_parser.add_argument("query", help="Search query")
        search_parser.add_argument("-n", "--limit", type=int, default=5, help="Max results to return (default: 5)")
        search_parser.add_argument("--scrape", action="store_true", help="Also scrape and return full markdown content of results")
        search_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        s_args = search_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        params = {
            "query": s_args.query,
            "limit": s_args.limit,
        }
        if s_args.scrape:
            params["scrapeOptions"] = {"formats": ["markdown"]}

        res = rpc_request("tools/call", {"name": "firecrawl_search", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Search error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if s_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_output(content)
        return

    # 6. Map command: firebridge map <url> [-n 50] [--search "subpath"] [--json]
    if action_lower == "map":
        map_parser = argparse.ArgumentParser(prog="firebridge map", description="Map all URLs of a website")
        map_parser.add_argument("url", help="Base URL of website to map")
        map_parser.add_argument("-n", "--limit", type=int, default=50, help="Max URLs to discover (default: 50)")
        map_parser.add_argument("--search", help="Search/filter subpath in discovered URLs")
        map_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        m_args = map_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        params = {"url": m_args.url, "limit": m_args.limit}
        if m_args.search:
            params["search"] = m_args.search

        res = rpc_request("tools/call", {"name": "firecrawl_map", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Map error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if m_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_output(content)
        return

    # 7. Crawl command: firebridge crawl <url> [-n 10] [--json]
    if action_lower == "crawl":
        crawl_parser = argparse.ArgumentParser(prog="firebridge crawl", description="Crawl a website and extract markdown for pages")
        crawl_parser.add_argument("url", help="Base URL to crawl")
        crawl_parser.add_argument("-n", "--limit", type=int, default=10, help="Max pages to crawl (default: 10)")
        crawl_parser.add_argument("--json", action="store_true", help="Output raw JSON response")

        c_args = crawl_parser.parse_args(parsed.args + unknown)
        api_key = get_api_key()

        params = {"url": c_args.url, "limit": c_args.limit}

        res = rpc_request("tools/call", {"name": "firecrawl_crawl", "arguments": params}, api_key=api_key)
        if "error" in res:
            sys.stderr.write(f"Crawl error: {json.dumps(res['error'], indent=2)}\n")
            sys.exit(1)

        if c_args.json:
            print(json.dumps(res.get("result", {}), indent=2))
        else:
            content = res.get("result", {}).get("content", [])
            format_output(content)
        return

    sys.stderr.write(
        f"Unknown command: '{parsed.action}'.\n"
        "Run 'firebridge' or 'firebridge --help' to see available tools and commands.\n"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
