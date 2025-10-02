"""
Core functionality for Bridge URL processing.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RedirectRule:
    """Represents a single redirect rule."""

    path: str
    destination: str
    status_code: int = 301
    host: str | None = None
    conditions: dict[str, Any] | None = None


class HostExpander:
    """Handles host expansion logic for different host types."""

    def __init__(self, base_domain: str | None = None):
        self.base_domain = base_domain

    def expand_hosts(self, host_config: str | dict[str, Any]) -> list[str]:
        """
        Expand host configuration to list of actual hosts.

        Supports:
        - "any": matches any host
        - "exact": uses specified domain
        - "bySubdomain": creates delivery.<base> pattern
        """
        if isinstance(host_config, str):
            if host_config == "any":
                return []  # No host restriction
            return [host_config]

        if isinstance(host_config, dict):
            host_type = host_config.get("type")

            if host_type == "any":
                return []

            elif host_type == "exact":
                domain = host_config.get("domain")
                if domain:
                    return [domain]

            elif host_type == "bySubdomain":
                subdomain = host_config.get("subdomain", "delivery")
                base = host_config.get("base") or self.base_domain
                if base:
                    return [f"{subdomain}.{base}"]

        return []


class PathConverter:
    """Converts regex paths to Netlify redirect patterns."""

    @staticmethod
    def convert_regex_to_netlify(path_pattern: str) -> list[str]:
        """
        Convert regex path patterns to Netlify redirect patterns.

        Examples:
        - "/api/.*" -> ["/api", "/api/*"]
        - "/users/\\d+" -> ["/users/:id"]
        - "/exact" -> ["/exact"]
        """
        patterns = []

        # Handle exact matches
        if not any(char in path_pattern for char in ".*+?[]{}()\\"):
            patterns.append(path_pattern)
            return patterns

        # Handle wildcard patterns
        if path_pattern.endswith(".*"):
            base_path = path_pattern[:-2]  # Remove .*
            patterns.append(base_path)
            patterns.append(f"{base_path}/*")
            return patterns

        # Handle digit patterns (convert to Netlify placeholder)
        if "\\d+" in path_pattern:
            # Handle both single and double escaped versions
            converted = re.sub(r"\\\\?d\+", ":id", path_pattern)
            patterns.append(converted)
            return patterns

        # Default: try to use as-is
        patterns.append(path_pattern)
        return patterns


class RuleProcessor:
    """Main processor for handling rule files and generating output."""

    def __init__(self, base_domain: str | None = None):
        self.host_expander = HostExpander(base_domain)
        self.path_converter = PathConverter()

    def load_rules(self, rules_file: Path) -> dict[str, Any]:
        """Load and parse rules from JSON file."""
        try:
            with open(rules_file, encoding="utf-8") as f:
                rules: dict[str, Any] = json.load(f)
            return rules
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading rules file: {e}") from e

    def validate_rules(self, rules: Any) -> list[str]:
        """Validate rules and return list of errors."""
        errors = []

        if not isinstance(rules, dict):
            errors.append("Rules must be a JSON object")
            return errors

        if "rules" not in rules:
            errors.append("'rules' must be an array")
            return errors

        rules_list = rules["rules"]
        if not isinstance(rules_list, list):
            errors.append("'rules' must be an array")
            return errors

        for i, rule in enumerate(rules_list):
            if not isinstance(rule, dict):
                errors.append(f"Rule {i}: must be an object")
                continue

            if "path" not in rule:
                errors.append(f"Rule {i}: missing 'path' field")

            if "destination" not in rule:
                errors.append(f"Rule {i}: missing 'destination' field")

            status = rule.get("status", 301)
            if not isinstance(status, int) or status not in [301, 302, 307, 308]:
                errors.append(f"Rule {i}: invalid status code {status}")

        return errors

    def process_rules(self, rules: dict[str, Any]) -> list[RedirectRule]:
        """Process rules into internal format."""
        processed_rules = []
        rules_list = rules.get("rules", [])

        for rule_config in rules_list:
            # Expand hosts
            hosts = []
            if "host" in rule_config:
                hosts = self.host_expander.expand_hosts(rule_config["host"])

            # Convert path patterns
            path_patterns = self.path_converter.convert_regex_to_netlify(
                rule_config["path"]
            )

            # Create rules for each combination
            for path_pattern in path_patterns:
                if hosts:
                    for host in hosts:
                        rule = RedirectRule(
                            path=path_pattern,
                            destination=rule_config["destination"],
                            status_code=rule_config.get("status", 301),
                            host=host,
                        )
                        processed_rules.append(rule)
                else:
                    rule = RedirectRule(
                        path=path_pattern,
                        destination=rule_config["destination"],
                        status_code=rule_config.get("status", 301),
                    )
                    processed_rules.append(rule)

        return processed_rules

    def generate_netlify_redirects(self, rules: list[RedirectRule]) -> str:
        """Generate _redirects file content."""
        lines = []

        for rule in rules:
            line = f"{rule.path} {rule.destination} {rule.status_code}"
            lines.append(line)

        return "\\n".join(lines)

    def generate_netlify_toml(self, rules: list[RedirectRule]) -> str:
        """Generate netlify.toml file content."""
        toml_lines = []

        for rule in rules:
            toml_lines.append("[[redirects]]")
            toml_lines.append(f'  from = "{rule.path}"')
            toml_lines.append(f'  to = "{rule.destination}"')
            toml_lines.append(f"  status = {rule.status_code}")

            if rule.host:
                toml_lines.append("  [redirects.conditions]")
                toml_lines.append(f'    Host = ["{rule.host}"]')

            toml_lines.append("")  # Empty line between rules

        return "\\n".join(toml_lines)
