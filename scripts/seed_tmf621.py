"""Seed script for TMF621 Trouble Ticket backend.

Usage:
    python scripts/seed_tmf621.py [--base-url http://localhost:8080]
"""

import argparse
import json
import urllib.request

BASE_URL = "http://localhost:8080"
ENDPOINT = "/tmf-api/troubleTicket/v5/troubleTicket"


SHARED_CUSTOMERS = {
    "45hj-10001": "Elena Papadopoulou",
    "45hj-10002": "Ioannis Kouris",
    "45hj-10003": "Maria Nikolaou",
    "45hj-10004": "Giorgos Manos",
    "45hj-10005": "Sofia Arvaniti",
    "45hj-20001": "RetailOne S.A.",
    "45hj-20002": "CloudAxis Ltd.",
    "45hj-20003": "Hellenic Trust Bank",
    "45hj-20004": "Aegean Logistics S.A.",
    "45hj-20005": "Mediterranean Hotels Group",
    "45hj-20006": "City of Heraklion",
    "45hj-30001": "OpenNet ISP",
}


def customer_related_party(customer_id: str, role: str = "customer") -> dict:
    """TMF621 RelatedPartyRefOrPartyRoleRef entry reusing TMF637 customer ids."""
    customer_name = SHARED_CUSTOMERS[customer_id]
    return {
        "@type": "RelatedPartyRefOrPartyRoleRef",
        "role": role,
        "partyOrPartyRole": {
            "id": customer_id,
            "href": f"https://host:port/partyManagement/v5/individual/{customer_id}",
            "name": customer_name,
            "@type": "PartyRoleRef",
            "@referredType": "Customer",
            "partyId": customer_id,
            "partyName": customer_name,
        },
    }


def noc_related_party() -> dict:
    """Issuer/originator party for tickets opened by NOC."""
    return {
        "@type": "RelatedPartyRefOrPartyRoleRef",
        "role": "originator",
        "partyOrPartyRole": {
            "id": "NOC-001",
            "href": "https://host:port/partyManagement/v5/organization/NOC-001",
            "name": "National Operations Center",
            "@type": "PartyRef",
            "@referredType": "Organization",
        },
    }


TICKETS = [
    {
        "externalId": "INC-FTTH-10001",
        "name": "FTTH intermittent packet loss - Athens Center",
        "description": "Customer reports intermittent packet loss during evening peak on FTTH 300M service.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-10001"), noc_related_party()],
    },
    {
        "externalId": "INC-VOICE-10002",
        "name": "VoIP outbound calls fail - Thessaloniki East",
        "description": "SIP registration succeeds but outbound PSTN calls fail with 503 on residential line.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-10002"), noc_related_party()],
    },
    {
        "externalId": "INC-CPE-10003",
        "name": "Router provisioning mismatch - Patras FTTH",
        "description": "Provisioned profile shows 1G but CPE receives 300M shaping profile after replacement.",
        "severity": "minor",
        "relatedParty": [customer_related_party("45hj-10003"), noc_related_party()],
    },
    {
        "externalId": "INC-VDSL-10004",
        "name": "VDSL sync drops every 15 minutes - Larissa",
        "description": "Frequent DSL retrains with SNR fluctuations. Copper pair quality suspected.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-10004"), noc_related_party()],
    },
    {
        "externalId": "INC-BILL-10005",
        "name": "Incorrect fixed-line charge on invoice - Volos",
        "description": "Customer billed for premium static IP add-on not present in active product configuration.",
        "severity": "minor",
        "relatedParty": [customer_related_party("45hj-10005"), noc_related_party()],
    },
    {
        "externalId": "INC-ETH-20001",
        "name": "Business Ethernet latency breach - RetailOne HQ",
        "description": "Latency exceeds SLA threshold during business hours on 1G Ethernet link.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-20001"), noc_related_party()],
    },
    {
        "externalId": "INC-DCI-20002",
        "name": "Data Center Interconnect BGP flapping - CloudAxis",
        "description": "10G DCI BGP session resets intermittently after maintenance window.",
        "severity": "critical",
        "relatedParty": [customer_related_party("45hj-20002"), noc_related_party()],
    },
    {
        "externalId": "INC-MPLS-20003",
        "name": "MPLS branch traffic blackhole - Hellenic Trust Bank",
        "description": "Two branch sites unreachable over L3VPN due to route target import issue.",
        "severity": "critical",
        "relatedParty": [customer_related_party("45hj-20003"), noc_related_party()],
    },
    {
        "externalId": "INC-MPLS-20004",
        "name": "QoS policy not applied on CE link - Aegean Logistics",
        "description": "Voice queue drops observed; CE-PE policy map missing after CPE replacement.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-20004"), noc_related_party()],
    },
    {
        "externalId": "INC-SIP-20005",
        "name": "SIP trunk inbound call failure - Hotel Group",
        "description": "Inbound calls rejected due to trunk auth profile mismatch in SBC cluster.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-20005"), noc_related_party()],
    },
    {
        "externalId": "INC-LL-20006",
        "name": "Leased line CRC errors - Municipal Services",
        "description": "Sustained CRC errors on P2P 100M circuit causing packet corruption.",
        "severity": "major",
        "relatedParty": [customer_related_party("45hj-20006"), noc_related_party()],
    },
    {
        "externalId": "INC-WLL-30001",
        "name": "Wholesale local loop activation delay - OpenNet ISP",
        "description": "New wholesale local loop orders stuck in pending activation state beyond SLA.",
        "severity": "minor",
        "relatedParty": [customer_related_party("45hj-30001"), noc_related_party()],
    },
]


def post_ticket(base_url: str, payload: dict) -> dict:
    """POST a single trouble ticket."""
    request = urllib.request.Request(
        f"{base_url}{ENDPOINT}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed TMF621 Trouble Ticket inventory.")
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL of the backend (default: http://localhost:8080)",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    print(f"Seeding {len(TICKETS)} TMF621 tickets to {base_url}{ENDPOINT}...\n")

    created_count = 0
    for index, ticket in enumerate(TICKETS, 1):
        payload = {
            "@type": "TroubleTicket",
            "externalId": ticket["externalId"],
            "name": ticket["name"],
            "description": ticket["description"],
            "severity": ticket["severity"],
            "relatedParty": ticket["relatedParty"],
        }

        try:
            result = post_ticket(base_url, payload)
            print(f"{index:03d}. ✓ {result['id']} - {ticket['name'][:64]}")
            created_count += 1
        except Exception as error:
            print(f"{index:03d}. ✗ {ticket['name'][:64]} ({error})")

    print(f"\nDone. {created_count}/{len(TICKETS)} trouble tickets inserted.")


if __name__ == "__main__":
    main()
