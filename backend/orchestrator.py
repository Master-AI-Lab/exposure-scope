#!/usr/bin/env python3
"""
exposure-scope — HUNTER OSINT Engine
Digital exposure scanner. Finds where your data lives across the internet.

Architecture:
  Frontend: Vercel (landing page + results display)
  Backend: VPS (tool orchestration + AI synthesis)

Usage:
  python3 orchestrator.py --email user@example.com
  python3 orchestrator.py --username john_doe
  python3 orchestrator.py --name "John Doe"
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, Optional

from tools.spiderfoot_wrapper import SpiderFootWrapper
from tools.sherlock_wrapper import SherlockWrapper
from tools.holehe_wrapper import HoleheWrapper
from tools.theharvester_wrapper import TheHarvesterWrapper
from tools.trufflehog_wrapper import TruffleHogWrapper
from synthesis.ai_report import AISynthesis


class ExposureOrchestrator:
    """Fires all HUNTER tools in parallel, collects results, synthesizes report."""

    def __init__(self):
        self.tools = [
            SpiderFootWrapper(),
            SherlockWrapper(),
            HoleheWrapper(),
            TheHarvesterWrapper(),
            TruffleHogWrapper(),
        ]
        self.synthesis = AISynthesis()
        self.results: Dict[str, Any] = {}

    async def scan(self, target: str, target_type: str = "auto") -> Dict[str, Any]:
        """
        Run full exposure scan on target.

        Args:
            target: Email, username, name, or domain
            target_type: 'email', 'username', 'name', 'domain', or 'auto'

        Returns:
            Comprehensive exposure report
        """
        print(f"[HUNTER] Starting exposure scan on: {target}")
        start_time = time.time()

        # Detect target type if auto
        if target_type == "auto":
            target_type = self._detect_type(target)

        # Fire all tools in parallel
        tasks = []
        for tool in self.tools:
            if tool.can_handle(target_type):
                tasks.append(self._run_tool(tool, target, target_type))

        await asyncio.gather(*tasks)

        # AI synthesis
        report = await self.synthesis.generate_report(self.results, target)

        duration = time.time() - start_time
        report["scan_metadata"] = {
            "target": target,
            "target_type": target_type,
            "duration_seconds": round(duration, 2),
            "tools_executed": len([t for t in self.results if self.results[t]]),
        }

        return report

    async def _run_tool(self, tool, target: str, target_type: str):
        """Run a single tool and store results."""
        try:
            print(f"  🔍 Running {tool.name}...")
            result = await tool.run(target, target_type)
            self.results[tool.name] = result
            print(f"  ✅ {tool.name} complete — {len(result.get('findings', []))} findings")
        except Exception as e:
            self.results[tool.name] = {"error": str(e), "findings": []}
            print(f"  ❌ {tool.name} failed: {e}")

    def _detect_type(self, target: str) -> str:
        """Auto-detect target type."""
        if "@" in target and "." in target:
            return "email"
        if "." in target and " " not in target:
            return "domain"
        return "username"

    def export_json(self, report: Dict[str, Any], path: str = None) -> str:
        """Export report to JSON."""
        output = json.dumps(report, indent=2, default=str)
        if path:
            with open(path, "w") as f:
                f.write(output)
            print(f"[HUNTER] Report saved to {path}")
        return output


def main():
    import argparse
    parser = argparse.ArgumentParser(description="exposure-scope — HUNTER OSINT Engine")
    parser.add_argument("--email", help="Email address to scan")
    parser.add_argument("--username", help="Username to scan")
    parser.add_argument("--name", help="Full name to scan")
    parser.add_argument("--domain", help="Domain to scan")

    args = parser.parse_args()

    # Determine target
    target = None
    target_type = "auto"
    for arg_type in ["email", "username", "name", "domain"]:
        val = getattr(args, arg_type, None)
        if val:
            target = val
            target_type = arg_type
            break

    if not target:
        parser.print_help()
        sys.exit(1)

    orchestrator = ExposureOrchestrator()
    report = asyncio.run(orchestrator.scan(target, target_type))

    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
