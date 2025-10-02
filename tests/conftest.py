"""
Pytest configuration and shared fixtures.
"""

import json
import pytest
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any

from bridge.core import RuleProcessor, HostExpander, PathConverter, RedirectRule


@pytest.fixture
def sample_rules() -> Dict[str, Any]:
    """Sample rules data for testing."""
    return {
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
            },
            {
                "path": "/users/\\d+",
                "destination": "https://users.example.com/profile/:id",
                "status": 302
            },
            {
                "path": "/legacy",
                "destination": "https://new.example.com/",
                "status": 301,
                "host": "any"
            },
            {
                "path": "/exact-match",
                "destination": "https://target.example.com/page",
                "status": 301,
                "host": {
                    "type": "exact",
                    "domain": "old.example.com"
                }
            }
        ]
    }


@pytest.fixture
def invalid_rules() -> Dict[str, Any]:
    """Invalid rules data for testing validation."""
    return {
        "rules": [
            {
                "path": "/missing-destination",
                "status": 301
            },
            {
                "destination": "https://example.com/missing-path",
                "status": 301
            },
            {
                "path": "/invalid-status",
                "destination": "https://example.com/",
                "status": 999
            }
        ]
    }


@pytest.fixture
def rules_file(tmp_path: Path, sample_rules: Dict[str, Any]) -> Path:
    """Create a temporary rules.json file."""
    rules_file = tmp_path / "rules.json"
    rules_file.write_text(json.dumps(sample_rules, indent=2))
    return rules_file


@pytest.fixture
def invalid_rules_file(tmp_path: Path, invalid_rules: Dict[str, Any]) -> Path:
    """Create a temporary invalid rules.json file."""
    rules_file = tmp_path / "invalid_rules.json"
    rules_file.write_text(json.dumps(invalid_rules, indent=2))
    return rules_file


@pytest.fixture
def empty_rules_file(tmp_path: Path) -> Path:
    """Create a temporary empty rules.json file."""
    rules_file = tmp_path / "empty_rules.json"
    rules_file.write_text('{"rules": []}')
    return rules_file


@pytest.fixture
def malformed_json_file(tmp_path: Path) -> Path:
    """Create a temporary malformed JSON file."""
    rules_file = tmp_path / "malformed.json"
    rules_file.write_text('{"rules": [invalid json}')
    return rules_file


@pytest.fixture
def rule_processor() -> RuleProcessor:
    """Create a RuleProcessor instance."""
    return RuleProcessor(base_domain="example.com")


@pytest.fixture
def host_expander() -> HostExpander:
    """Create a HostExpander instance."""
    return HostExpander(base_domain="example.com")


@pytest.fixture
def path_converter() -> PathConverter:
    """Create a PathConverter instance."""
    return PathConverter()


@pytest.fixture
def sample_redirect_rules() -> list[RedirectRule]:
    """Sample RedirectRule objects for testing."""
    return [
        RedirectRule(
            path="/api",
            destination="https://api.example.com/:splat",
            status_code=301,
            host="delivery.example.com"
        ),
        RedirectRule(
            path="/api/*",
            destination="https://api.example.com/:splat",
            status_code=301,
            host="delivery.example.com"
        ),
        RedirectRule(
            path="/users/:id",
            destination="https://users.example.com/profile/:id",
            status_code=302
        ),
        RedirectRule(
            path="/legacy",
            destination="https://new.example.com/",
            status_code=301
        )
    ]


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir