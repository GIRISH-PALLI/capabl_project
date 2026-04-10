#!/usr/bin/env python3
"""
CAPABL Track B - Quick Start Demo Runner
Run this to generate and display demo scenarios
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from DEMO_SCENARIOS import DemoScenarios, demo


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def print_demo_script():
    """Print full demo script"""
    print_header("CAPABL FINANCIAL AI - TRACK B DEMO SCRIPT")
    print(demo.get_demo_script())


def print_scenario(scenario_num: int):
    """Print specific scenario"""
    scenarios = demo.get_all_scenarios()
    if scenario_num < 1 or scenario_num > len(scenarios):
        print(f"Invalid scenario number. Available: 1-{len(scenarios)}")
        return
    
    scenario = scenarios[scenario_num - 1]
    print_header(f"SCENARIO {scenario_num}: {scenario['name']} ({scenario['duration_minutes']} min)")
    
    print(f"Duration: {scenario['duration_minutes']} minutes\n")
    
    for step in scenario.get('steps', []):
        print(f"Step {step['step']}: {step['action']}")
        print(f"  {step['description']}\n")
    
    print(f"Success Criteria: {scenario.get('success_criteria', 'N/A')}\n")


def print_all_scenarios():
    """Print all scenarios overview"""
    scenarios = demo.get_all_scenarios()
    print_header("ALL DEMO SCENARIOS AVAILABLE")
    
    total_time = 0
    for i, scenario in enumerate(scenarios, 1):
        duration = scenario['duration_minutes']
        total_time += duration
        print(f"{i}. {scenario['name']}")
        print(f"   Duration: {duration} minutes")
        print(f"   Steps: {len(scenario.get('steps', []))}\n")
    
    print(f"Total Demo Time: {total_time} minutes")
    print("\nTo view a specific scenario, run:")
    print("  python run_demo.py --scenario 1")
    print("\nTo see the full demo script, run:")
    print("  python run_demo.py --script")


def print_environment_check():
    """Check and print environment readiness"""
    print_header("ENVIRONMENT READINESS CHECK")
    
    checks = {
        "Python 3.8+": sys.version_info >= (3, 8),
        "Project root found": PROJECT_ROOT.exists(),
        "Backend services exist": (PROJECT_ROOT / "backend").exists(),
        "Frontend directory exists": (PROJECT_ROOT / "frontend").exists(),
        "Docker Compose config": (PROJECT_ROOT / "docker-compose.yml").exists(),
        "API Documentation": (PROJECT_ROOT / "API_DOCUMENTATION.md").exists(),
        "Deployment Guide": (PROJECT_ROOT / "DEPLOYMENT_GUIDE.md").exists(),
        "Demo Scenarios": (PROJECT_ROOT / "DEMO_SCENARIOS.py").exists(),
    }
    
    for check, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {check}")
    
    print("\n📋 Next Steps:")
    print("1. View demo script:        python run_demo.py --script")
    print("2. View specific scenario:  python run_demo.py --scenario 1")
    print("3. Start services:          docker-compose up -d")
    print("4. Check health:            curl http://localhost:8000/health")
    print("5. View API docs:           http://localhost:8000/docs")


def print_infrastructure_overview():
    """Print infrastructure architecture"""
    print_header("INFRASTRUCTURE ARCHITECTURE")
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                     CAPABL ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Frontend (React/Next.js)                    │  │
│  │                 Port 3000                            │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                   │
│  ┌──────────────────────────▼──────────────────────────────┐  │
│  │          API Gateway (FastAPI)                         │  │
│  │  Authentication • Rate Limiting • Routing              │  │
│  │                 Port 8000                              │  │
│  └─┬──────────────┬──────────────┬──────────────┬─────────┘  │
│    │              │              │              │             │
│ ┌──▼──────────┐ ┌─▼────────────┐ ┌─▼──────────┐ ┌┴────────┐  │
│ │ Market Data │ │ Portfolio    │ │ Analytics  │ │Monitoring
│ │ Service     │ │ Service      │ │ Service    │ │Service  │  │
│ │ Port 8001   │ │ Port 8002    │ │ Port 8003  │ │Port 8004│  │
│ └────────────┘ └──────────────┘ └────────────┘ └─────────┘  │
│       │              │              │              │           │
│  ┌────▼──────────────▼──────────────▼──────────────▼────┐    │
│  │ PostgreSQL Database (Persistence Layer)             │    │
│  │ - Instruments, Market Ticks, Fundamentals          │    │
│  │ - Portfolios, Positions, Watchlists                │    │
│  │ - Alerts, Audit Logs                               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Services Breakdown:

🔐 API Gateway (8000)
   ├─ JWT Authentication
   ├─ Rate Limiting (100 req/min)
   ├─ Request Routing
   ├─ Health Monitoring
   └─ CORS Configuration

📈 Market Data Service (8001)
   ├─ Real-time Quotes
   ├─ Price History (1d → 5y)
   ├─ Technical Indicators (SMA, RSI, MACD, BB)
   ├─ Multi-ticker Comparison
   └─ Intelligent Caching (60-300s)

💼 Portfolio Service (8002)
   ├─ Position Tracking
   ├─ Real-time P&L
   ├─ Performance Attribution
   ├─ Top Gainers/Losers
   └─ Multi-user Support

📊 Analytics Service (8003)
   ├─ Technical Comparison
   ├─ Sentiment Analysis
   ├─ Portfolio Optimization (MPT)
   ├─ Sector Benchmarking
   └─ Options Pricing (Black-Scholes)

📉 Monitoring Service (8004)
   ├─ Service Metrics
   ├─ Financial Dashboard
   ├─ User Analytics
   ├─ Alert Management
   └─ System Health

Database: PostgreSQL
├─ 10+ Normalized Tables
├─ Advanced Indexing
├─ JSONB Support
└─ Audit Logging""")


def main():
    """Main CLI interface"""
    
    if len(sys.argv) < 2:
        print_environment_check()
        return
    
    command = sys.argv[1].lower()
    
    if command == "--help" or command == "-h":
        print("""
CAPABL Track B Demo Runner

Usage: python run_demo.py [command]

Commands:
  --script              Display full demo script (8-10 minutes)
  --scenario <1-5>      Display specific scenario (1=Portfolio, 5=Trading)
  --all                 Show all scenarios overview
  --architecture        Display system architecture
  --check               Environment readiness check
  --help                Show this help message

Examples:
  python run_demo.py --script
  python run_demo.py --scenario 1
  python run_demo.py --architecture
        """)
    
    elif command == "--script":
        print_demo_script()
    
    elif command == "--scenario":
        if len(sys.argv) < 3:
            print("Usage: python run_demo.py --scenario <1-5>")
            sys.exit(1)
        try:
            scenario_num = int(sys.argv[2])
            print_scenario(scenario_num)
        except ValueError:
            print("Invalid scenario number. Expected 1-5.")
            sys.exit(1)
    
    elif command == "--all":
        print_all_scenarios()
    
    elif command == "--architecture":
        print_infrastructure_overview()
    
    elif command == "--check":
        print_environment_check()
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python run_demo.py --help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
