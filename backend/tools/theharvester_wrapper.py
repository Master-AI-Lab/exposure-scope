"""
theHarvester wrapper — email, subdomain, and port enumeration.
Limited to fast sources only to avoid timeouts.
"""

from typing import Dict, Any, List
import asyncio


class TheHarvesterWrapper:
    """Wrapper for theHarvester enumeration tool."""

    name = "theHarvester"
    description = "Email, subdomain, and port enumeration from public sources"

    # Fast sources only — avoid 'all' which hangs on many engines
    FAST_SOURCES = "hunter,tomba,hackertarget,certspotter,crtsh,otx,urlscan"

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["domain", "email"]

    async def run(self, target: str, target_type: str) -> Dict[str, Any]:
        """Enumerate target using theHarvester — fast sources only."""
        # Extract domain from email if needed
        search_domain = target.split("@")[-1] if "@" in target else target

        cmd = [
            "theHarvester", "-d", search_domain,
            "-b", self.FAST_SOURCES,
            "-l", "50",  # limit results
            "-f", "/tmp/harvester_results.html"
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=25
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
        except asyncio.TimeoutError:
            return {
                "tool": self.name,
                "status": "timeout",
                "target": target,
                "findings_count": 0,
                "findings": [],
                "error": "theHarvester timed out (25s)"
            }
        except Exception as e:
            return {
                "tool": self.name,
                "status": "error",
                "target": target,
                "findings_count": 0,
                "findings": [],
                "error": str(e)
            }

    def _parse_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse theHarvester output."""
        findings = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(": ", 1)
            if len(parts) == 2:
                findings.append({
                    "category": parts[0],
                    "value": parts[1],
                })
        return findings
