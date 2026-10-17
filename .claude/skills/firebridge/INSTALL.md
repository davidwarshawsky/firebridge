
## Enterprise TLS certificates

The CLI verifies HTTPS certificates. For networks that use TLS inspection, set a trusted enterprise CA bundle before running it:

```powershell
$env:SSL_CERT_FILE = 'C:\path\to\corporate-ca-bundle.pem'
# Or use a directory containing hashed CA certificates:
$env:SSL_CERT_DIR = 'C:\path\to\corporate-ca-directory'
firebridge --help
```

Keep certificate verification enabled. The variables are passed through automatically when `firebridge` is launched from an MCP host.
# Installing `firebridge`

The `firebridge` CLI provides agents and developers with dynamic, token-efficient access to the remote Firecrawl MCP Server (`https://mcp.firecrawl.dev/v2/mcp`).

It has **zero third-party dependencies** (uses only standard library Python 3) and runs seamlessly on Windows, macOS, and Linux.

---

## 1. Prerequisites: API Key

`firebridge` requires the `FIRECRAWL_API_KEY` environment variable:

```bash
export FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

On Windows PowerShell:
```powershell
$env:FIRECRAWL_API_KEY="your-firecrawl-api-key"
```

---

## 2. Quick Verification

Before installing, check if `firebridge` is already present in your PATH:

```bash
which firebridge || command -v firebridge || Get-Command firebridge
```

Or test invocation directly:
```bash
firebridge --help
```

---

## 3. Installation Options

### Option A: Install via `uv` (Recommended)
If `uv` is installed, install `firebridge` as a globally isolated tool:
```bash
uv tool install git+https://github.com/davidwarshawsky/firebridge
```

To update later:
```bash
uv tool upgrade firebridge
```

---

### Option B: Run on the fly with `uvx` (No installation needed)
If you don't want to install anything permanently, run `firebridge` on demand via `uvx`:
```bash
uvx --from git+https://github.com/davidwarshawsky/firebridge firebridge --help
```

---

### Option C: Install via `pipx`
If using `pipx`:
```bash
pipx install git+https://github.com/davidwarshawsky/firebridge.git
```

---

### Option D: Install via `pip`
```bash
pip install git+https://github.com/davidwarshawsky/firebridge.git
```

---

### Option E: Local Development / Clone
Clone the repository and install in editable mode:
```bash
git clone https://github.com/davidwarshawsky/firebridge.git
cd firebridge
pip install -e .
```
