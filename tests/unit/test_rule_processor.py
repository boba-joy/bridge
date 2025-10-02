"""
Unit tests for RuleProcessor class.
"""

from pathlib import Path

import pytest

from bridge.core import RedirectRule, RuleProcessor


class TestRuleProcessor:
    """Test RuleProcessor functionality."""

    def test_init_with_base_domain(self):
        """Test initialization with base domain."""
        processor = RuleProcessor("example.com")
        assert processor.host_expander.base_domain == "example.com"

    def test_init_without_base_domain(self):
        """Test initialization without base domain."""
        processor = RuleProcessor()
        assert processor.host_expander.base_domain is None

    def test_load_rules_success(self, rule_processor, rules_file):
        """Test successful loading of rules file."""
        rules = rule_processor.load_rules(rules_file)
        assert isinstance(rules, dict)
        assert "rules" in rules
        assert len(rules["rules"]) == 4

    def test_load_rules_file_not_found(self, rule_processor):
        """Test loading non-existent rules file."""
        with pytest.raises(ValueError, match="Error loading rules file"):
            rule_processor.load_rules(Path("nonexistent.json"))

    def test_load_rules_invalid_json(self, rule_processor, malformed_json_file):
        """Test loading malformed JSON file."""
        with pytest.raises(ValueError, match="Error loading rules file"):
            rule_processor.load_rules(malformed_json_file)

    def test_validate_rules_success(self, rule_processor, sample_rules):
        """Test successful rules validation."""
        errors = rule_processor.validate_rules(sample_rules)
        assert errors == []

    def test_validate_rules_not_dict(self, rule_processor):
        """Test validation with non-dict input."""
        errors = rule_processor.validate_rules("not a dict")
        assert "Rules must be a JSON object" in errors

    def test_validate_rules_no_rules_key(self, rule_processor):
        """Test validation without rules key."""
        errors = rule_processor.validate_rules({})
        assert "'rules' must be an array" in errors

    def test_validate_rules_invalid_rules_type(self, rule_processor):
        """Test validation with invalid rules type."""
        errors = rule_processor.validate_rules({"rules": "not an array"})
        assert "'rules' must be an array" in errors

    def test_validate_rules_missing_path(self, rule_processor):
        """Test validation with missing path."""
        rules = {"rules": [{"destination": "https://example.com"}]}
        errors = rule_processor.validate_rules(rules)
        assert "Rule 0: missing 'path' field" in errors

    def test_validate_rules_missing_destination(self, rule_processor):
        """Test validation with missing destination."""
        rules = {"rules": [{"path": "/test"}]}
        errors = rule_processor.validate_rules(rules)
        assert "Rule 0: missing 'destination' field" in errors

    def test_validate_rules_invalid_status(self, rule_processor):
        """Test validation with invalid status code."""
        rules = {
            "rules": [
                {"path": "/test", "destination": "https://example.com", "status": 999}
            ]
        }
        errors = rule_processor.validate_rules(rules)
        assert "Rule 0: invalid status code 999" in errors

    def test_validate_rules_multiple_errors(self, rule_processor, invalid_rules):
        """Test validation with multiple errors."""
        errors = rule_processor.validate_rules(invalid_rules)
        assert len(errors) == 3
        assert any("missing 'destination' field" in error for error in errors)
        assert any("missing 'path' field" in error for error in errors)
        assert any("invalid status code 999" in error for error in errors)

    def test_process_rules_simple(self, rule_processor):
        """Test processing simple rules without hosts."""
        rules = {
            "rules": [
                {
                    "path": "/test",
                    "destination": "https://example.com/test",
                    "status": 301,
                }
            ]
        }
        processed = rule_processor.process_rules(rules)
        assert len(processed) == 1
        assert processed[0].path == "/test"
        assert processed[0].destination == "https://example.com/test"
        assert processed[0].status_code == 301
        assert processed[0].host is None

    def test_process_rules_with_hosts(self, rule_processor):
        """Test processing rules with host expansion."""
        rules = {
            "rules": [
                {
                    "path": "/api",
                    "destination": "https://api.example.com/",
                    "status": 301,
                    "host": {"type": "exact", "domain": "old.example.com"},
                }
            ]
        }
        processed = rule_processor.process_rules(rules)
        assert len(processed) == 1
        assert processed[0].host == "old.example.com"

    def test_process_rules_with_path_expansion(self, rule_processor):
        """Test processing rules with path pattern expansion."""
        rules = {
            "rules": [
                {
                    "path": "/api/.*",
                    "destination": "https://api.example.com/:splat",
                    "status": 301,
                }
            ]
        }
        processed = rule_processor.process_rules(rules)
        assert len(processed) == 2  # "/api" and "/api/*"
        paths = [rule.path for rule in processed]
        assert "/api/" in paths
        assert "/api//*" in paths

    def test_process_rules_host_and_path_expansion(self, rule_processor):
        """Test processing rules with both host and path expansion."""
        rules = {
            "rules": [
                {
                    "path": "/api/.*",
                    "destination": "https://api.example.com/:splat",
                    "status": 301,
                    "host": {
                        "type": "bySubdomain",
                        "subdomain": "www",
                        "base": "test.com",
                    },
                }
            ]
        }
        processed = rule_processor.process_rules(rules)
        assert len(processed) == 2  # 2 paths x 1 host
        for rule in processed:
            assert rule.host == "www.test.com"
        paths = [rule.path for rule in processed]
        assert "/api/" in paths
        assert "/api//*" in paths

    def test_generate_netlify_redirects(self, rule_processor, sample_redirect_rules):
        """Test generating _redirects file content."""
        content = rule_processor.generate_netlify_redirects(sample_redirect_rules)
        lines = content.split("\\n")
        assert len(lines) == 4
        assert "/api https://api.example.com/:splat 301" in lines
        assert "/api/* https://api.example.com/:splat 301" in lines
        assert "/users/:id https://users.example.com/profile/:id 302" in lines
        assert "/legacy https://new.example.com/ 301" in lines

    def test_generate_netlify_toml(self, rule_processor, sample_redirect_rules):
        """Test generating netlify.toml file content."""
        content = rule_processor.generate_netlify_toml(sample_redirect_rules)
        assert "[[redirects]]" in content
        assert 'from = "/api"' in content
        assert 'to = "https://api.example.com/:splat"' in content
        assert "status = 301" in content
        assert 'Host = ["delivery.example.com"]' in content

    def test_generate_netlify_toml_no_host(self, rule_processor):
        """Test generating netlify.toml without host conditions."""
        rules = [
            RedirectRule(
                path="/test", destination="https://example.com/test", status_code=301
            )
        ]
        content = rule_processor.generate_netlify_toml(rules)
        assert "[[redirects]]" in content
        assert 'from = "/test"' in content
        assert "Host" not in content

    def test_empty_rules_list(self, rule_processor):
        """Test processing empty rules list."""
        rules = {"rules": []}
        processed = rule_processor.process_rules(rules)
        assert processed == []

        redirects = rule_processor.generate_netlify_redirects(processed)
        assert redirects == ""

        toml = rule_processor.generate_netlify_toml(processed)
        assert toml == ""
