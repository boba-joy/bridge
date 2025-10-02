"""
Unit tests for HostExpander class.
"""

import pytest
from bridge.core import HostExpander


class TestHostExpander:
    """Test HostExpander functionality."""

    def test_init_with_base_domain(self):
        """Test initialization with base domain."""
        expander = HostExpander("example.com")
        assert expander.base_domain == "example.com"

    def test_init_without_base_domain(self):
        """Test initialization without base domain."""
        expander = HostExpander()
        assert expander.base_domain is None

    def test_expand_hosts_any_string(self, host_expander):
        """Test expanding 'any' host type as string."""
        result = host_expander.expand_hosts("any")
        assert result == []

    def test_expand_hosts_exact_string(self, host_expander):
        """Test expanding exact domain as string."""
        result = host_expander.expand_hosts("example.com")
        assert result == ["example.com"]

    def test_expand_hosts_any_dict(self, host_expander):
        """Test expanding 'any' host type as dict."""
        host_config = {"type": "any"}
        result = host_expander.expand_hosts(host_config)
        assert result == []

    def test_expand_hosts_exact_dict(self, host_expander):
        """Test expanding exact host type as dict."""
        host_config = {"type": "exact", "domain": "test.example.com"}
        result = host_expander.expand_hosts(host_config)
        assert result == ["test.example.com"]

    def test_expand_hosts_exact_dict_no_domain(self, host_expander):
        """Test expanding exact host type without domain."""
        host_config = {"type": "exact"}
        result = host_expander.expand_hosts(host_config)
        assert result == []

    def test_expand_hosts_by_subdomain_default(self, host_expander):
        """Test expanding bySubdomain with default subdomain."""
        host_config = {"type": "bySubdomain", "base": "test.com"}
        result = host_expander.expand_hosts(host_config)
        assert result == ["delivery.test.com"]

    def test_expand_hosts_by_subdomain_custom(self, host_expander):
        """Test expanding bySubdomain with custom subdomain."""
        host_config = {
            "type": "bySubdomain",
            "subdomain": "api",
            "base": "test.com"
        }
        result = host_expander.expand_hosts(host_config)
        assert result == ["api.test.com"]

    def test_expand_hosts_by_subdomain_use_base_domain(self):
        """Test expanding bySubdomain using instance base domain."""
        expander = HostExpander("example.com")
        host_config = {"type": "bySubdomain", "subdomain": "www"}
        result = expander.expand_hosts(host_config)
        assert result == ["www.example.com"]

    def test_expand_hosts_by_subdomain_no_base(self, host_expander):
        """Test expanding bySubdomain without base domain."""
        host_config = {"type": "bySubdomain", "subdomain": "api"}
        result = host_expander.expand_hosts(host_config)
        assert result == []

    def test_expand_hosts_unknown_type(self, host_expander):
        """Test expanding unknown host type."""
        host_config = {"type": "unknown"}
        result = host_expander.expand_hosts(host_config)
        assert result == []

    def test_expand_hosts_invalid_input(self, host_expander):
        """Test expanding with invalid input type."""
        result = host_expander.expand_hosts(123)
        assert result == []