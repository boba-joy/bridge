"""
Command-line interface for Bridge URL.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .core import RuleProcessor


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="bridge",
        description="CLI tool for managing Netlify URL redirections",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bridge check --rules rules.json
  bridge build --rules rules.json --outdir output
  bridge build --rules rules.json --outdir output --artifacts redirects
  bridge build --rules rules.json --outdir output --artifacts toml
  bridge build --rules rules.json --outdir output --artifacts both
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Validate rules file without generating output"
    )
    check_parser.add_argument(
        "--rules",
        type=Path,
        required=True,
        help="Path to rules.json file",
    )

    # Build command
    build_parser = subparsers.add_parser(
        "build", help="Generate Netlify deployment artifacts"
    )
    build_parser.add_argument(
        "--rules",
        type=Path,
        required=True,
        help="Path to rules.json file",
    )
    build_parser.add_argument(
        "--outdir",
        type=Path,
        default="output",
        help="Output directory (default: output)",
    )
    build_parser.add_argument(
        "--artifacts",
        choices=["redirects", "toml", "both"],
        default="both",
        help="Which artifacts to generate (default: both)",
    )

    return parser


def cmd_check(rules_file: Path) -> int:
    """Handle the check command."""
    try:
        processor = RuleProcessor()
        rules = processor.load_rules(rules_file)
        errors = processor.validate_rules(rules)

        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  • {error}")
            return 1

        print("✅ Rules validation passed")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_build(
    rules_file: Path, outdir: Path, artifacts: str
) -> int:
    """Handle the build command."""
    try:
        processor = RuleProcessor()

        # Load and validate rules
        rules = processor.load_rules(rules_file)
        errors = processor.validate_rules(rules)

        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  • {error}")
            return 1

        # Process rules
        processed_rules = processor.process_rules(rules)

        # Create output directory
        outdir.mkdir(parents=True, exist_ok=True)

        # Generate artifacts
        if artifacts in ["redirects", "both"]:
            redirects_content = processor.generate_netlify_redirects(processed_rules)
            redirects_file = outdir / "_redirects"
            redirects_file.write_text(redirects_content, encoding="utf-8")
            print(f"✅ Generated {redirects_file}")

        if artifacts in ["toml", "both"]:
            toml_content = processor.generate_netlify_toml(processed_rules)
            toml_file = outdir / "netlify.toml"
            toml_file.write_text(toml_content, encoding="utf-8")
            print(f"✅ Generated {toml_file}")

        print(f"🎉 Build completed successfully! ({len(processed_rules)} rules)")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "check":
        return cmd_check(args.rules)

    elif args.command == "build":
        return cmd_build(args.rules, args.outdir, args.artifacts)

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())