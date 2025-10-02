"""
Unit tests for CLI module.
"""

from pathlib import Path
from unittest.mock import call, patch

from bridge.cli import (
    cmd_build,
    cmd_check,
    create_parser,
    main,
)


class TestCreateParser:
    """Test argument parser creation."""

    def test_parser_creation(self):
        """Test parser is created with correct configuration."""
        parser = create_parser()
        assert parser.prog == "bridge"
        assert "CLI tool for managing Netlify URL redirections" in parser.description

    def test_check_subcommand(self):
        """Test check subcommand parsing."""
        parser = create_parser()
        args = parser.parse_args(["check", "--rules", "rules.json"])
        assert args.command == "check"
        assert args.rules == Path("rules.json")

    def test_build_subcommand_minimal(self):
        """Test build subcommand with minimal arguments."""
        parser = create_parser()
        args = parser.parse_args(["build", "--rules", "rules.json"])
        assert args.command == "build"
        assert args.rules == Path("rules.json")
        assert args.outdir == Path("output")
        assert args.artifacts == "both"

    def test_build_subcommand_full(self):
        """Test build subcommand with all arguments."""
        parser = create_parser()
        args = parser.parse_args(
            [
                "build",
                "--rules",
                "rules.json",
                "--outdir",
                "custom_output",
                "--artifacts",
                "toml",
            ]
        )
        assert args.command == "build"
        assert args.rules == Path("rules.json")
        assert args.outdir == Path("custom_output")
        assert args.artifacts == "toml"

    def test_no_command(self):
        """Test parser with no command."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.command is None


class TestCmdCheck:
    """Test check command functionality."""

    def test_check_success(self, rules_file, mocker):
        """Test successful check command."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = []

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_check(rules_file)

        assert result == 0
        mock_processor.load_rules.assert_called_once_with(rules_file)
        mock_processor.validate_rules.assert_called_once()
        mock_print.assert_called_with("✅ Rules validation passed")

    def test_check_validation_errors(self, rules_file, mocker):
        """Test check command with validation errors."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = [
            "Rule 0: missing path",
            "Rule 1: missing destination",
        ]

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_check(rules_file)

        assert result == 1
        expected_calls = [
            call("❌ Validation failed:"),
            call("  • Rule 0: missing path"),
            call("  • Rule 1: missing destination"),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_check_file_not_found(self, mocker):
        """Test check command with missing file."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.side_effect = ValueError("File not found")

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_check(Path("nonexistent.json"))

        assert result == 1
        mock_print.assert_called_with("❌ Error: File not found")

    def test_check_unexpected_error(self, rules_file, mocker):
        """Test check command with unexpected error."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.side_effect = RuntimeError("Unexpected error")

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_check(rules_file)

        assert result == 1
        mock_print.assert_called_with("❌ Error: Unexpected error")


class TestCmdBuild:
    """Test build command functionality."""

    def test_build_success_both_artifacts(self, rules_file, output_dir, mocker):
        """Test successful build with both artifacts."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = []
        mock_processor.process_rules.return_value = [mocker.Mock()]
        mock_processor.generate_netlify_redirects.return_value = "redirect content"
        mock_processor.generate_netlify_toml.return_value = "toml content"

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_build(rules_file, output_dir, "both")

        assert result == 0
        assert (output_dir / "_redirects").exists()
        assert (output_dir / "netlify.toml").exists()
        assert (output_dir / "_redirects").read_text() == "redirect content"
        assert (output_dir / "netlify.toml").read_text() == "toml content"

        expected_calls = [
            call(f"✅ Generated {output_dir / '_redirects'}"),
            call(f"✅ Generated {output_dir / 'netlify.toml'}"),
            call("🎉 Build completed successfully! (1 rules)"),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_build_redirects_only(self, rules_file, output_dir, mocker):
        """Test build with redirects artifact only."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = []
        mock_processor.process_rules.return_value = []
        mock_processor.generate_netlify_redirects.return_value = "redirect content"

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print"),
        ):
            result = cmd_build(rules_file, output_dir, "redirects")

        assert result == 0
        assert (output_dir / "_redirects").exists()
        assert not (output_dir / "netlify.toml").exists()
        mock_processor.generate_netlify_toml.assert_not_called()

    def test_build_toml_only(self, rules_file, output_dir, mocker):
        """Test build with toml artifact only."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = []
        mock_processor.process_rules.return_value = []
        mock_processor.generate_netlify_toml.return_value = "toml content"

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print"),
        ):
            result = cmd_build(rules_file, output_dir, "toml")

        assert result == 0
        assert not (output_dir / "_redirects").exists()
        assert (output_dir / "netlify.toml").exists()
        mock_processor.generate_netlify_redirects.assert_not_called()

    def test_build_validation_errors(self, rules_file, output_dir, mocker):
        """Test build command with validation errors."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = ["Error 1", "Error 2"]

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_build(rules_file, output_dir, "both")

        assert result == 1
        expected_calls = [
            call("❌ Validation failed:"),
            call("  • Error 1"),
            call("  • Error 2"),
        ]
        mock_print.assert_has_calls(expected_calls)

    def test_build_creates_output_directory(self, rules_file, tmp_path, mocker):
        """Test build command creates output directory if it doesn't exist."""
        output_dir = tmp_path / "nonexistent" / "output"
        assert not output_dir.exists()

        mock_processor = mocker.Mock()
        mock_processor.load_rules.return_value = {"rules": []}
        mock_processor.validate_rules.return_value = []
        mock_processor.process_rules.return_value = []
        mock_processor.generate_netlify_redirects.return_value = "content"

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print"),
        ):
            result = cmd_build(rules_file, output_dir, "redirects")

        assert result == 0
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_build_error_handling(self, rules_file, output_dir, mocker):
        """Test build command error handling."""
        mock_processor = mocker.Mock()
        mock_processor.load_rules.side_effect = RuntimeError("Build error")

        with (
            patch("bridge.cli.RuleProcessor", return_value=mock_processor),
            patch("builtins.print") as mock_print,
        ):
            result = cmd_build(rules_file, output_dir, "both")

        assert result == 1
        mock_print.assert_called_with("❌ Error: Build error")


class TestMain:
    """Test main function."""

    def test_main_no_args(self, mocker):
        """Test main function with no arguments."""
        mock_parser = mocker.Mock()
        mock_args = mocker.Mock()
        mock_args.command = None
        mock_parser.parse_args.return_value = mock_args

        with patch("bridge.cli.create_parser", return_value=mock_parser):
            result = main([])

        assert result == 1
        mock_parser.print_help.assert_called_once()

    def test_main_check_command(self, mocker):
        """Test main function with check command."""
        with patch("bridge.cli.cmd_check", return_value=0) as mock_check:
            result = main(["check", "--rules", "rules.json"])

        assert result == 0
        mock_check.assert_called_once()

    def test_main_build_command(self, mocker):
        """Test main function with build command."""
        with patch("bridge.cli.cmd_build", return_value=0) as mock_build:
            result = main(["build", "--rules", "rules.json"])

        assert result == 0
        mock_build.assert_called_once()

    def test_main_unknown_command(self, mocker):
        """Test main function with unknown command."""
        mock_parser = mocker.Mock()
        mock_args = mocker.Mock()
        mock_args.command = "unknown"
        mock_parser.parse_args.return_value = mock_args

        with patch("bridge.cli.create_parser", return_value=mock_parser):
            result = main(["unknown"])

        assert result == 1
        mock_parser.print_help.assert_called_once()

    def test_main_uses_sys_argv_by_default(self, mocker):
        """Test main function uses sys.argv by default."""
        mock_parser = mocker.Mock()
        mock_args = mocker.Mock()
        mock_args.command = None
        mock_parser.parse_args.return_value = mock_args

        with (
            patch("bridge.cli.create_parser", return_value=mock_parser),
            patch("sys.argv", ["bridge"]),
        ):
            result = main()

        assert result == 1
        mock_parser.parse_args.assert_called_with(None)
