"""
Integration tests for end-to-end workflows.
"""

import json
import subprocess
import sys


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""

    def test_check_valid_rules(self, rules_file):
        """Test check command with valid rules file."""
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "check", "--rules", str(rules_file)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "✅ Rules validation passed" in result.stdout

    def test_check_invalid_rules(self, invalid_rules_file):
        """Test check command with invalid rules file."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "check",
                "--rules",
                str(invalid_rules_file),
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "❌ Validation failed:" in result.stdout
        assert "missing 'destination' field" in result.stdout
        assert "missing 'path' field" in result.stdout

    def test_check_nonexistent_file(self, tmp_path):
        """Test check command with nonexistent file."""
        nonexistent = tmp_path / "nonexistent.json"
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "check", "--rules", str(nonexistent)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "❌ Error:" in result.stdout

    def test_build_both_artifacts(self, rules_file, tmp_path):
        """Test build command generating both artifacts."""
        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
                "--artifacts",
                "both",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "🎉 Build completed successfully!" in result.stdout

        # Check files exist
        redirects_file = output_dir / "_redirects"
        toml_file = output_dir / "netlify.toml"
        assert redirects_file.exists()
        assert toml_file.exists()

        # Check file contents
        redirects_content = redirects_file.read_text()
        toml_content = toml_file.read_text()

        assert "/api/ https://api.example.com/:splat 301" in redirects_content
        assert "/api//* https://api.example.com/:splat 301" in redirects_content
        assert (
            "/users/:id https://users.example.com/profile/:id 302" in redirects_content
        )

        assert "[[redirects]]" in toml_content
        assert 'from = "/api/"' in toml_content
        assert 'Host = ["delivery.example.com"]' in toml_content

    def test_build_redirects_only(self, rules_file, tmp_path):
        """Test build command generating only _redirects file."""
        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
                "--artifacts",
                "redirects",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (output_dir / "_redirects").exists()
        assert not (output_dir / "netlify.toml").exists()

    def test_build_toml_only(self, rules_file, tmp_path):
        """Test build command generating only netlify.toml file."""
        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
                "--artifacts",
                "toml",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert not (output_dir / "_redirects").exists()
        assert (output_dir / "netlify.toml").exists()

    def test_build_creates_output_directory(self, rules_file, tmp_path):
        """Test build command creates output directory if it doesn't exist."""
        output_dir = tmp_path / "deep" / "nested" / "output"
        assert not output_dir.exists()

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_build_with_invalid_rules(self, invalid_rules_file, tmp_path):
        """Test build command with invalid rules fails validation."""
        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(invalid_rules_file),
                "--outdir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 1
        assert "❌ Validation failed:" in result.stdout
        assert not (output_dir / "_redirects").exists()
        assert not (output_dir / "netlify.toml").exists()

    def test_complex_rules_processing(self, tmp_path):
        """Test processing of complex rules with various host and path patterns."""
        complex_rules = {
            "rules": [
                {
                    "path": "/api/v1/.*",
                    "destination": "https://api-v1.example.com/:splat",
                    "status": 301,
                    "host": {
                        "type": "bySubdomain",
                        "subdomain": "api",
                        "base": "mysite.com",
                    },
                },
                {
                    "path": "/users/\\\\d+/profile",
                    "destination": "https://profiles.example.com/user/:id",
                    "status": 302,
                    "host": {"type": "exact", "domain": "old.mysite.com"},
                },
                {
                    "path": "/legacy/.*",
                    "destination": "https://new.example.com/:splat",
                    "status": 301,
                    "host": "any",
                },
            ]
        }

        rules_file = tmp_path / "complex_rules.json"
        rules_file.write_text(json.dumps(complex_rules, indent=2))
        output_dir = tmp_path / "output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Check _redirects content
        redirects_content = (output_dir / "_redirects").read_text()
        lines = redirects_content.strip().split("\\n")

        # Should have expanded paths for wildcard patterns
        assert any("/api/v1/ " in line for line in lines)
        assert any("/api/v1//* " in line for line in lines)
        assert any("/users/:id/profile " in line for line in lines)
        assert any("/legacy/ " in line for line in lines)
        assert any("/legacy//* " in line for line in lines)

        # Check netlify.toml content
        toml_content = (output_dir / "netlify.toml").read_text()
        assert 'Host = ["api.mysite.com"]' in toml_content
        assert 'Host = ["old.mysite.com"]' in toml_content
        # Rules with "any" host should not have Host conditions
        legacy_sections = toml_content.split("[[redirects]]")
        legacy_section = next((s for s in legacy_sections if "/legacy" in s), "")
        assert "Host" not in legacy_section or legacy_section.count("Host") == 0

    def test_help_command(self):
        """Test help command output."""
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "CLI tool for managing Netlify URL redirections" in result.stdout
        assert "check" in result.stdout
        assert "build" in result.stdout

    def test_subcommand_help(self):
        """Test subcommand help output."""
        result = subprocess.run(
            [sys.executable, "-m", "bridge", "build", "--help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "--rules" in result.stdout
        assert "--outdir" in result.stdout
        assert "--artifacts" in result.stdout

    def test_no_command(self):
        """Test running bridge without any command."""
        result = subprocess.run(
            [sys.executable, "-m", "bridge"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "usage:" in result.stdout.lower() or "help" in result.stdout.lower()


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_migration_scenario(self, tmp_path):
        """Test a typical website migration scenario."""
        migration_rules = {
            "rules": [
                # Redirect old blog posts
                {
                    "path": "/blog/.*",
                    "destination": "https://newblog.example.com/:splat",
                    "status": 301,
                },
                # Redirect old API endpoints
                {
                    "path": "/api/v1/.*",
                    "destination": "https://api.newsite.com/v2/:splat",
                    "status": 301,
                    "host": {"type": "exact", "domain": "oldapi.example.com"},
                },
                # Redirect user profiles
                {
                    "path": "/user/\\\\d+",
                    "destination": "https://profiles.newsite.com/:id",
                    "status": 301,
                },
                # Catch-all for remaining pages
                {
                    "path": "/.*",
                    "destination": "https://newsite.example.com/:splat",
                    "status": 301,
                },
            ]
        }

        rules_file = tmp_path / "migration_rules.json"
        rules_file.write_text(json.dumps(migration_rules, indent=2))
        output_dir = tmp_path / "migration_output"

        # First validate
        check_result = subprocess.run(
            [sys.executable, "-m", "bridge", "check", "--rules", str(rules_file)],
            capture_output=True,
            text=True,
        )

        assert check_result.returncode == 0

        # Then build
        build_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert build_result.returncode == 0
        assert (output_dir / "_redirects").exists()
        assert (output_dir / "netlify.toml").exists()

        # Verify content makes sense
        redirects_content = (output_dir / "_redirects").read_text()
        assert "/blog" in redirects_content
        assert "/blog//*" in redirects_content
        assert "/user/:id" in redirects_content
        assert "newsite.example.com" in redirects_content

    def test_microservices_scenario(self, tmp_path):
        """Test routing for microservices architecture."""
        microservices_rules = {
            "rules": [
                # User service
                {
                    "path": "/users/.*",
                    "destination": "https://user-service.internal/:splat",
                    "status": 301,
                    "host": {
                        "type": "bySubdomain",
                        "subdomain": "api",
                        "base": "myapp.com",
                    },
                },
                # Order service
                {
                    "path": "/orders/.*",
                    "destination": "https://order-service.internal/:splat",
                    "status": 301,
                    "host": {
                        "type": "bySubdomain",
                        "subdomain": "api",
                        "base": "myapp.com",
                    },
                },
                # Payment service
                {
                    "path": "/payments/.*",
                    "destination": "https://payment-service.internal/:splat",
                    "status": 301,
                    "host": {
                        "type": "bySubdomain",
                        "subdomain": "api",
                        "base": "myapp.com",
                    },
                },
            ]
        }

        rules_file = tmp_path / "microservices_rules.json"
        rules_file.write_text(json.dumps(microservices_rules, indent=2))
        output_dir = tmp_path / "microservices_output"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "bridge",
                "build",
                "--rules",
                str(rules_file),
                "--outdir",
                str(output_dir),
                "--artifacts",
                "toml",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        toml_content = (output_dir / "netlify.toml").read_text()

        # All rules should have the same host condition
        assert toml_content.count('Host = ["api.myapp.com"]') >= 3
        assert "user-service.internal" in toml_content
        assert "order-service.internal" in toml_content
        assert "payment-service.internal" in toml_content
