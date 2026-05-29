"""
AI Synthesis Layer — turns raw OSINT tool output into polished exposure reports.
Uses AgentMemory or LLM to create human-readable findings.
"""

from typing import Dict, Any, List
from datetime import datetime


class AISynthesis:
    """Takes raw tool outputs and generates structured, human-readable exposure reports."""

    name = "AI Synthesis"
    description = "Turns raw OSINT data into polished exposure reports"

    async def generate_report(
        self,
        raw_results: Dict[str, Any],
        target: str
    ) -> Dict[str, Any]:
        """
        Synthesize raw tool outputs into a comprehensive exposure report.

        Args:
            raw_results: Dict of tool_name -> tool output
            target: The target that was scanned

        Returns:
            Structured report with categorized findings
        """
        # Aggregate all findings
        all_findings = []
        for tool_name, result in raw_results.items():
            if result and "findings" in result:
                for finding in result["findings"]:
                    all_findings.append({
                        **finding,
                        "source_tool": tool_name,
                    })

        # Categorize findings by severity
        exposed_data = []
        exposed_social = []
        exposed_technical = []
        exposed_leaks = []

        for f in all_findings:
            # Categorization logic based on finding type
            finding_type = f.get("type", f.get("category", "unknown"))
            finding_str = str(f.get("data", f.get("value", f.get("service", ""))))

            entry = {
                "detail": finding_str,
                "severity": self._assess_severity(f),
                "remediation": self._get_remediation(f),
            }

            if any(k in finding_type.lower() for k in ["email", "phone", "address", "name", "dob"]):
                exposed_data.append(entry)
            elif any(k in finding_type.lower() for k in ["social", "account", "profile", "platform"]):
                exposed_social.append(entry)
            elif any(k in finding_type.lower() for k in ["domain", "ip", "subdomain", "port", "tech"]):
                exposed_technical.append(entry)
            elif any(k in finding_type.lower() for k in ["secret", "leak", "credential", "password"]):
                exposed_leaks.append(entry)
            else:
                exposed_social.append(entry)

        # Calculate exposure score
        severity_weights = {"critical": 10, "high": 5, "medium": 2, "low": 0.5}
        exposure_score = sum(
            severity_weights.get(f.get("severity", "low"), 0)
            for f in all_findings
        )

        # Determine exposure level
        if exposure_score >= 50:
            exposure_level = "CRITICAL"
        elif exposure_score >= 20:
            exposure_level = "HIGH"
        elif exposure_score >= 5:
            exposure_level = "MODERATE"
        else:
            exposure_level = "LOW"

        return {
            "target": target,
            "scan_timestamp": datetime.utcnow().isoformat(),
            "exposure_summary": {
                "score": round(exposure_score, 1),
                "level": exposure_level,
                "total_findings": len(all_findings),
            },
            "categories": {
                "personal_data": {
                    "count": len(exposed_data),
                    "findings": exposed_data,
                },
                "social_accounts": {
                    "count": len(exposed_social),
                    "findings": exposed_social,
                },
                "technical_exposure": {
                    "count": len(exposed_technical),
                    "findings": exposed_technical,
                },
                "leaks": {
                    "count": len(exposed_leaks),
                    "findings": exposed_leaks,
                },
            },
            "raw_results": raw_results,
        }

    def _assess_severity(self, finding: Dict) -> str:
        """Assess severity of a finding."""
        confidence = finding.get("confidence", 50)
        if confidence > 80:
            return "high"
        elif confidence > 50:
            return "medium"
        return "low"

    def _get_remediation(self, finding: Dict) -> str:
        """Get remediation suggestion based on finding type."""
        finding_type = str(finding.get("type", ""))
        if "email" in finding_type.lower():
            return "Use alias emails for different services. Check haveibeenpwned.com."
        if "phone" in finding_type.lower():
            return "Use a virtual number for non-essential signups."
        if "address" in finding_type.lower():
            return "Use a PO Box or virtual address for registrations."
        if "social" in finding_type.lower() or "profile" in finding_type.lower():
            return "Review privacy settings. Remove unused accounts."
        if "secret" in finding_type.lower() or "credential" in finding_type.lower():
            return "Rotate credentials immediately. Enable 2FA."
        return "Review the data exposure and assess risk."
