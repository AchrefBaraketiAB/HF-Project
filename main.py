"""Main entry point for trading framework - runs pytest tests."""
import sys
import subprocess
from pathlib import Path


def main():
    """Run pytest tests."""
    print("=" * 80)
    print("TRADING FRAMEWORK - RUNNING PYTEST TESTS")
    print("=" * 80)
    print()
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Run pytest with verbose output
    pytest_args = [
        'pytest',
        'tests/',
        '-v',  # Verbose - shows each test as it runs
        '--tb=short',  # Short traceback format
        '--color=yes',  # Colored output
        '-ra',  # Show extra test summary info
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        pytest_args.extend([
            '--cov=core',  # Coverage for core module
            '--cov=fetchers',  # Coverage for fetchers module
            '--cov=utils',  # Coverage for utils module
            '--cov-report=term-missing',  # Show missing lines in terminal
            '--cov-report=term',  # Show coverage percentage
        ])
    except ImportError:
        print("Note: pytest-cov not installed. Install with: pip install pytest-cov")
        print("Running tests without coverage...")
        print()
    
    # Check if user wants to skip network tests
    if '--skip-network' in sys.argv:
        pytest_args.extend(['-m', 'not network'])
        print("Skipping network tests (Binance/YFinance API tests)")
        print()
    
    # Check if user wants to run specific test
    if '--test' in sys.argv:
        idx = sys.argv.index('--test')
        if idx + 1 < len(sys.argv):
            test_name = sys.argv[idx + 1]
            pytest_args.append(f"tests/test_main.py::{test_name}")
            print(f"Running specific test: {test_name}")
            print()
    
    # Check for HTML coverage report
    if '--coverage-html' in sys.argv:
        pytest_args.append('--cov-report=html')
        print("Generating HTML coverage report")
        print()
    
    try:
        result = subprocess.run(pytest_args, cwd=project_root, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("ERROR: pytest is not installed!")
        print("Please install it with: pip install pytest")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(130)


if __name__ == '__main__':
    main()
