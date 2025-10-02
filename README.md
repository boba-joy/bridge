# Bridge URL 🌉

CLI tool for managing Netlify URL redirections with rule-based JSON configuration.

## Features

- 📋 **Rule-based configuration** - Define redirects in JSON format
- 🔀 **Host expansion** - Support for `any`, `exact`, and `bySubdomain` patterns
- 🎯 **Path conversion** - Convert regex patterns to Netlify-compatible formats
- 📦 **Dual output** - Generate both `_redirects` and `netlify.toml` files
- ✅ **Validation** - Built-in rules validation with helpful error messages
- 🧪 **Well tested** - Comprehensive unit and integration test suite

## Quick Start

```bash
# Setup (choose one):
./setup.sh              # Bash script
# OR
make setup              # Makefile

# Activate environment
source .venv/bin/activate

# Demo with example rules
poe demo               # = poe check + poe build
# OR
make demo              # without poe

# Use your own rules
poe check-rules my-rules.json
poe build-rules my-rules.json
```

## Commands

### With Poe (after `source .venv/bin/activate`)
| Command | Description |
|---------|-------------|
| `poe check` | Validate example rules |
| `poe build` | Build artifacts from examples |
| `poe build-redirects` | Build only `_redirects` file |
| `poe build-toml` | Build only `netlify.toml` file |
| `poe check-rules <file>` | Validate custom rules file |
| `poe build-rules <file>` | Build from custom rules file |

### With Make (no venv activation needed)
| Command | Description |
|---------|-------------|
| `make setup` | Create venv and install dependencies |
| `make demo` | Validate + build examples |
| `make check` | Validate example rules |
| `make build` | Build artifacts from examples |
| `make test` | Run tests |
| `make style` | Format and fix code |
| `make clean` | Clean all generated files |

## Custom Rules

```bash
# Validate your rules
poe check-rules path/to/rules.json

# Build with custom options
poe build-rules rules.json --outdir dist --artifacts both
poe build-rules rules.json --outdir dist --artifacts redirects
poe build-rules rules.json --outdir dist --artifacts toml
```

## Development

```bash
# Setup development environment (first time)
./setup.sh              # Creates .venv + installs deps
# OR
make setup

# Activate environment
source .venv/bin/activate

# Code quality
poe quality             # ruff format + ruff check + mypy
poe style               # format and fix all issues
poe fix                 # auto-fix linting issues
poe format              # format code only

# Testing
poe test                # all tests
poe test-fast           # unit tests only (fast)
poe test-cov            # with coverage report
poe test-unit           # unit tests only
poe test-integration    # integration tests only

# Build & ship
poe ready               # quality + test + package
poe package             # build wheel
poe clean               # clean all generated files
```

## Rules Format

### Basic Structure

```json
{
  "rules": [
    {
      "path": "/api/.*",
      "destination": "https://api.example.com/:splat",
      "status": 301,
      "host": {
        "type": "bySubdomain",
        "subdomain": "delivery",
        "base": "example.com"
      }
    }
  ]
}
```

### Host Configuration

```json
// Match any host
"host": "any"

// Exact domain match
"host": {
  "type": "exact",
  "domain": "old.example.com"
}

// Subdomain pattern
"host": {
  "type": "bySubdomain",
  "subdomain": "api",
  "base": "example.com"
}
```

### Path Patterns

- **Exact**: `/api/users` → `/api/users`
- **Wildcard**: `/api/.*` → `/api` and `/api/*`
- **Digit**: `/users/\\d+` → `/users/:id`

### Output Examples

**_redirects format:**
```
/api https://api.example.com/:splat 301
/api/* https://api.example.com/:splat 301
/users/:id https://users.example.com/profile/:id 302
```

**netlify.toml format:**
```toml
[[redirects]]
  from = "/api"
  to = "https://api.example.com/:splat"
  status = 301
  [redirects.conditions]
    Host = ["delivery.example.com"]
```

## Deployment

### GitHub Actions + Netlify

Bridge URL includes a complete CI/CD pipeline for automated deployments to Netlify:

#### Setup

1. **Fork/clone this repository**
2. **Create a Netlify site** and get your Site ID
3. **Add GitHub secrets:**
   ```
   NETLIFY_AUTH_TOKEN=your_netlify_token
   NETLIFY_SITE_ID=your_site_id
   ```

#### Automatic Deployment

The workflow triggers on:
- **Push to main** → Production deployment
- **Pull requests** → Preview deployment
- **Manual dispatch** → Custom deployment

#### Configuration

1. **Create your rules:** Add `deploy/rules.json` with your redirect rules
2. **Commit and push:** GitHub Actions will automatically:
   - ✅ Run tests and validation
   - 🏗️ Generate `_redirects` and `netlify.toml`
   - 🚀 Deploy to Netlify
   - 💬 Comment on PRs with preview URL

#### Manual Deployment

```bash
# Trigger manual deployment with custom rules
gh workflow run deploy-netlify.yml \
  -f rules_file=my-custom-rules.json \
  -f deploy_env=production
```

#### Example Deploy Rules

See `deploy/rules.json` for production-ready examples:

```json
{
  "rules": [
    {
      "path": "/docs/.*",
      "destination": "https://bridge-url.readthedocs.io/:splat",
      "status": 301
    },
    {
      "path": "/api/v1/.*",
      "destination": "https://api.bridge-url.com/v1/:splat",
      "status": 301,
      "host": {
        "type": "bySubdomain",
        "subdomain": "app",
        "base": "bridge-url.com"
      }
    }
  ]
}
```

### Local Deployment Testing

```bash
# Generate and test locally
poe build-rules deploy/rules.json --outdir dist
netlify dev --dir dist  # Test with Netlify CLI
```

## Installation

### From Source
```bash
git clone https://github.com/arkady/bridge-url.git
cd bridge-url
./setup.sh
source .venv/bin/activate
```

### As Package
```bash
pip install bridge-url
bridge check --rules rules.json
bridge build --rules rules.json --outdir output
```

## Requirements

- Python 3.13+
- No runtime dependencies (uses only standard library)

## License

MIT License - see LICENSE file for details.

---

See `examples/rules.json` for development examples and `deploy/rules.json` for production examples.
