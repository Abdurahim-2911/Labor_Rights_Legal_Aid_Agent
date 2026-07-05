"""
NGO Lookup Tool

Queries the local ngo_contacts.json directory for relevant contacts.
The Routing Agent calls this tool first before falling back to Google Search.
"""

import json
import os


def lookup_ngo_contacts(issue_type: str, risk_level: str) -> list[dict]:
    """Look up NGO, embassy, and government contacts relevant to the case.

    Args:
        issue_type: The categorized issue (e.g., 'unpaid_wages', 'workplace_abuse').
        risk_level: The risk level (SAFE, CAUTION, or HIGH_RISK).

    Returns:
        A list of contact dicts with keys: name, type, phone, url, notes.
    """
    try:
        contacts_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "ngo_contacts.json"
        )
        with open(contacts_path, "r", encoding="utf-8") as f:
            all_contacts = json.load(f)

        # Filter contacts that match the issue type
        results = [
            c for c in all_contacts
            if issue_type in c.get("applicable_issue_types", [])
            or "other" in c.get("applicable_issue_types", [])
        ]

        # Sort: prioritize NGOs/police for HIGH_RISK, MOHRE for others
        if risk_level == "HIGH_RISK":
            results.sort(
                key=lambda x: 0
                if x.get("type") in ["ngo", "embassy"] or "Police" in x.get("name", "")
                else 1
            )
        else:
            results.sort(
                key=lambda x: 0
                if x.get("type") == "government" and "MOHRE" in x.get("name", "")
                else 1
            )

        return results

    except Exception as e:
        print(f"NGO lookup error: {e}")
        return []
