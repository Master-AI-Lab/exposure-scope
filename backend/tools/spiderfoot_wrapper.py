"""
SpiderFoot wrapper — automated OSINT data collection.
Runs SpiderFoot scans against targets and returns structured findings.
"""

from typing import Dict, Any, List, Optional
import asyncio
import json
import os
import tempfile


class SpiderFootWrapper:
    """Wrapper for SpiderFoot OSINT automation tool."""

    name = "SpiderFoot"
    description = "Automated OSINT — IPs, domains, emails, social media"

    # SpiderFoot runs as a standalone python script
    SF_PATH = "/root/.hermes/tools/spiderfoot/sf.py"

    def can_handle(self, target_type: str) -> bool:
        return target_type in ["email", "username", "domain", "ip"]

    async def run(self, target: str, target_type: str) -> Dict[str, Any]:
        """
        Execute SpiderFoot scan against target.

        Runs passive scan (no direct interaction with target systems).
        Returns structured findings.
        """
        if not os.path.exists(self.SF_PATH):
            return {
                "tool": self.name,
                "status": "not_installed",
                "findings": [],
                "error": "SpiderFoot not installed at " + self.SF_PATH
            }

        # Map target types to SpiderFoot scan types
        sf_type_map = {
            "email": "EMAIL_ADDRESS",
            "username": "USERNAME",
            "domain": "INTERNET_NAME",
            "ip": "IP_ADDRESS",
        }
        sf_type = sf_type_map.get(target_type, "HUMAN_NAME")

        # Run SpiderFoot in passive mode
        cmd = [
            "python3", self.SF_PATH,
            "-s", target,
            "-t", sf_type,
            "-o", "json",
            "-q"
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=30
            )

            if process.returncode != 0:
                return {
                    "tool": self.name,
                    "status": "error",
                    "findings": [],
                    "error": stderr.decode()[:500]
                }

            findings = self._parse_findings(stdout.decode())
        except asyncio.TimeoutError:
            return {
                "tool": self.name,
                "status": "timeout",
                "findings": [],
                "error": "SpiderFoot timed out (30s)"
            }
        except Exception as e:
            return {
                "tool": self.name,
                "status": "error",
                "findings": [],
                "error": str(e)
            }

        return {
            "tool": self.name,
            "status": "complete",
            "target": target,
            "findings_count": len(findings),
            "findings": findings,
        }

    def _parse_findings(self, raw_output: str) -> List[Dict[str, Any]]:
        """Parse SpiderFoot JSON output into structured findings."""
        findings = []
        for line in raw_output.strip().split("\n"):
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                findings.append({
                    "type": entry.get("type", "unknown"),
                    "data": entry.get("data", ""),
                    "source": entry.get("source", ""),
                    "confidence": entry.get("confidence", 0),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return findings
