#!/usr/bin/env python3
"""
Comprehensive Test Runner for FastAPI Property Evaluation System

This script provides various testing options and generates comprehensive reports.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def install_dependencies():
    """Install project dependencies."""
    print("📦 Installing project dependencies...")
    
    # Install main dependencies
    if not run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      "Installing main dependencies"):
        return False
    
    # Install additional testing tools
    additional_tools = [
        "pytest-html",
        "pytest-json-report",
        "pytest-benchmark",
        "pytest-randomly"
    ]
    
    for tool in additional_tools:
        if not run_command([sys.executable, "-m", "pip", "install", tool], 
                          f"Installing {tool}"):
            print(f"⚠️  Warning: Failed to install {tool}, continuing...")
    
    return True

def run_unit_tests():
    """Run unit tests only."""
    print("\n🧪 Running Unit Tests...")
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "unit",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/unit",
        "--cov-report=xml:coverage/unit.xml"
    ]
    
    return run_command(command, "Running unit tests")

def run_integration_tests():
    """Run integration tests only."""
    print("\n🔗 Running Integration Tests...")
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "integration",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/integration",
        "--cov-report=xml:coverage/integration.xml"
    ]
    
    return run_command(command, "Running integration tests")

def run_all_tests():
    """Run all tests with comprehensive coverage."""
    print("\n🎯 Running All Tests...")
    
    # Create coverage directory
    os.makedirs("coverage", exist_ok=True)
    os.makedirs("htmlcov", exist_ok=True)
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/all",
        "--cov-report=xml:coverage/all.xml",
        "--cov-fail-under=80",
        "--junitxml=coverage/junit.xml",
        "--html=htmlcov/report.html",
        "--self-contained-html"
    ]
    
    return run_command(command, "Running all tests")

def run_specific_test_category(category):
    """Run tests for a specific category."""
    print(f"\n🎯 Running {category.title()} Tests...")
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", category,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=term-missing",
        f"--cov-report=html:htmlcov/{category}",
        f"--cov-report=xml:coverage/{category}.xml"
    ]
    
    return run_command(command, f"Running {category} tests")

def run_performance_tests():
    """Run performance/benchmark tests."""
    print("\n⚡ Running Performance Tests...")
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-min-rounds=10"
    ]
    
    return run_command(command, "Running performance tests")

def run_security_tests():
    """Run security-focused tests."""
    print("\n🛡️ Running Security Tests...")
    
    command = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-m", "security",
        "-v",
        "--tb=short"
    ]
    
    return run_command(command, "Running security tests")

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📊 Generating Test Report...")
    
    # Check if coverage reports exist
    if not os.path.exists("coverage") and not os.path.exists("htmlcov"):
        print("⚠️  No coverage reports found. Run tests first.")
        return False
    
    print("✅ Coverage reports generated:")
    
    if os.path.exists("htmlcov"):
        print("   📁 HTML reports: htmlcov/")
    
    if os.path.exists("coverage"):
        print("   📁 XML reports: coverage/")
    
    print("\n📈 To view HTML coverage report:")
    print("   open htmlcov/all/index.html")
    
    return True

def run_linting_and_formatting():
    """Run code quality checks."""
    print("\n🔍 Running Code Quality Checks...")
    
    # Install additional tools if needed
    tools = ["flake8", "black", "isort", "mypy"]
    
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"📦 Installing {tool}...")
            subprocess.run([sys.executable, "-m", "pip", "install", tool], check=True)
    
    # Run checks
    checks = [
        (["flake8", "app/", "tests/"], "Running flake8 linting"),
        (["black", "--check", "app/", "tests/"], "Checking code formatting with black"),
        (["isort", "--check-only", "app/", "tests/"], "Checking import sorting with isort"),
        (["mypy", "app/"], "Running type checking with mypy")
    ]
    
    all_passed = True
    for command, description in checks:
        if not run_command(command, description):
            all_passed = False
    
    return all_passed

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for FastAPI Property Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit                   # Run unit tests only
  python run_tests.py --integration            # Run integration tests only
  python run_tests.py --category auth          # Run auth tests only
  python run_tests.py --performance            # Run performance tests
  python run_tests.py --security               # Run security tests
  python run_tests.py --quality                # Run code quality checks
  python run_tests.py --install                # Install dependencies
  python run_tests.py --report                 # Generate test report
        """
    )
    
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--category", type=str, help="Run tests for specific category (auth, customer, service, api)")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--quality", action="store_true", help="Run code quality checks")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print("🚀 FastAPI Property Evaluation System - Test Runner")
    print("=" * 60)
    
    # Install dependencies if requested
    if args.install:
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Run requested tests
    success = True
    
    if args.unit:
        success &= run_unit_tests()
    
    if args.integration:
        success &= run_integration_tests()
    
    if args.category:
        success &= run_specific_test_category(args.category)
    
    if args.performance:
        success &= run_performance_tests()
    
    if args.security:
        success &= run_security_tests()
    
    if args.quality:
        success &= run_linting_and_formatting()
    
    if args.all:
        success &= run_all_tests()
    
    if args.report:
        success &= generate_test_report()
    
    # Final summary
    print("\n" + "=" * 60)
    if success:
        print("🎉 All requested operations completed successfully!")
        print("📊 Check the generated reports for detailed results.")
    else:
        print("❌ Some operations failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 