"""
Sherlock wrapper — username search across 400+ platforms.
"""

from typing import Dict, Any, List
import asyncio
import json
import os


class SherlockWrapper:
    """Wrapper for Sherlock username search tool."""

    name = "Sherlock"
    description = "Username search across 400+ social platforms"

    # Sherlock CLI path
    SHERLOCK_PATH = "sherlock"

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["username"]

    async def run(self, target: str, target_type: str) -> Dict[str, Any]:
        """Search for username across platforms."""
        cmd = [
            self.SHERLOCK_PATH, target,
            "--output", "/tmp/sherlock_results.json",
            "--timeout", "30",
            "--print-found"
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=180
        )

        # Read results if they exist
        findings = []
        results_file = "/tmp/sherlock_results.json"
        if os.path.exists(results_file):
            try:
                with open(results_file) as f:
                    raw = json.load(f)
                for site, data in raw.items():
                    if data.get("status") == "claimed":
                        findings.append({
                            "platform": site,
                            "url": data.get("url_user", ""),
                            "status": "claimed",
                        })
            except (json.JSONDecodeError, KeyError):
                pass

        return {
            "tool": self.name,
            "status": "complete",
            "target": target,
            "findings_count": len(findings),
            "findings": findings,
        }
