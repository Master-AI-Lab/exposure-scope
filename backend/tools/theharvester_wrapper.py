"""
theHarvester wrapper — email, subdomain, and port enumeration.
"""

from typing import Dict, Any, List
import asyncio


class TheHarvesterWrapper:
    """Wrapper for theHarvester enumeration tool."""

    name = "theHarvester"
    description = "Email, subdomain, and port enumeration from public sources"

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["domain", "email"]

    async def run(self, target: str, target_type: str) -> Dict[str, Any]:
        """Enumerate target using theHarvester."""
        if target_type == "domain":
            cmd = ["theHarvester", "-d", target, "-b", "all", "-f", "/tmp/harvester_results.html"]
        else:
            cmd = ["theHarvester", "-d", target, "-b", "all", "-f", "/tmp/harvester_results.html"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=120
        )

        output = stdout.decode()
        findings = self._parse_output(output)

        return {
            "tool": self.name,
            "status": "complete",
            "target": target,
            "findings_count": len(findings),
            "findings": findings,
        }

    def _parse_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse theHarvester output."""
        findings = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Simple line-based parsing
            parts = line.split(": ", 1)
            if len(parts) == 2:
                findings.append({
                    "category": parts[0],
                    "value": parts[1],
                })
        return findings
