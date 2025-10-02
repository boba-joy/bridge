"""
Unit tests for PathConverter class.
"""


class TestPathConverter:
    """Test PathConverter functionality."""

    def test_exact_path_no_regex(self, path_converter):
        """Test converting exact path without regex."""
        result = path_converter.convert_regex_to_netlify("/api/users")
        assert result == ["/api/users"]

    def test_wildcard_pattern(self, path_converter):
        """Test converting wildcard pattern."""
        result = path_converter.convert_regex_to_netlify("/api/.*")
        assert result == ["/api", "/api/*"]

    def test_digit_pattern(self, path_converter):
        """Test converting digit pattern."""
        result = path_converter.convert_regex_to_netlify("/users/\\\\d+")
        assert result == ["/users/:id"]

    def test_multiple_digit_patterns(self, path_converter):
        """Test converting multiple digit patterns."""
        result = path_converter.convert_regex_to_netlify("/users/\\\\d+/posts/\\\\d+")
        assert result == ["/users/:id/posts/:id"]

    def test_complex_regex_fallback(self, path_converter):
        """Test complex regex falls back to as-is."""
        result = path_converter.convert_regex_to_netlify("/api/[a-z]+")
        assert result == ["/api/[a-z]+"]

    def test_root_wildcard(self, path_converter):
        """Test root wildcard pattern."""
        result = path_converter.convert_regex_to_netlify("/.*")
        assert result == ["/", "/*"]

    def test_nested_wildcard(self, path_converter):
        """Test nested wildcard pattern."""
        result = path_converter.convert_regex_to_netlify("/api/v1/.*")
        assert result == ["/api/v1", "/api/v1/*"]

    def test_pattern_with_special_chars(self, path_converter):
        """Test pattern with other regex special characters."""
        result = path_converter.convert_regex_to_netlify("/api/test+")
        assert result == ["/api/test+"]

    def test_empty_path(self, path_converter):
        """Test empty path."""
        result = path_converter.convert_regex_to_netlify("")
        assert result == [""]

    def test_root_path(self, path_converter):
        """Test root path."""
        result = path_converter.convert_regex_to_netlify("/")
        assert result == ["/"]

    def test_path_without_leading_slash(self, path_converter):
        """Test path without leading slash."""
        result = path_converter.convert_regex_to_netlify("api/.*")
        assert result == ["api", "api/*"]
