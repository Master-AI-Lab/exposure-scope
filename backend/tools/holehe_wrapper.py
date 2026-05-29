"""
holehe wrapper — email account discovery.
Checks which online services an email is registered on.
"""

from typing import Dict, Any, List
import asyncio
import re


class HoleheWrapper:
    """Wrapper for holehe email account discovery."""

    name = "holehe"
    description = "Email account discovery — finds which services an email is registered on"

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email"]

    async def run(self, target: str, target_type: str) -> Dict[str, Any]:
        """Check which services an email is registered on."""
        cmd = ["holehe", target]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=60
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
        """Parse holehe output into structured findings."""
        findings = []
        for line in output.split("\n"):
            line = line.strip()
            if "[+]" in line:
                # Account exists
                service = line.replace("[+]", "").strip()
                findings.append({
                    "service": service,
                    "registered": True,
                })
            elif "[-]" in line:
                # Account doesn't exist
                service = line.replace("[-]", "").strip()
                findings.append({
                    "service": service,
                    "registered": False,
                })
        return findings
