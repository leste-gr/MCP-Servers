"""Seed script for TMF637 Product Inventory backend.

Usage:
    python scripts/seed_tmf637.py [--base-url http://localhost:8082]
"""

import argparse
import json
import urllib.request

BASE_URL = "http://localhost:8082"
ENDPOINT = "/tmf-api/productInventory/v5/product"


def related_customer(customer_id: str, customer_name: str) -> dict:
    """Create TMF637-compliant relatedParty item for a customer."""
    return {
        "role": "Customer",
        "partyOrPartyRole": {
            "id": customer_id,
            "href": f"https://host:port/partyManagement/v5/individual/{customer_id}",
            "name": customer_name,
            "@type": "PartyRoleRef",
            "@referredType": "Customer",
        },
        "@type": "RelatedPartyOrPartyRole",
    }


PRODUCTS = [
    {
        "name": "FTTH Residential 300M - Athens Center",
        "description": "Fixed-line FTTH 300 Mbps with home voice over SIP.",
        "status": "active",
        "productOffering": {
            "id": "PO-FTTH-300-RES",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-FTTH-300-RES",
            "name": "FTTH 300M Residential",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-10001", "Elena Papadopoulou")],
    },
    {
        "name": "FTTH Residential 500M - Thessaloniki East",
        "description": "Fixed-line FTTH 500 Mbps with dynamic IPv4 and voice bundle.",
        "status": "active",
        "productOffering": {
            "id": "PO-FTTH-500-RES",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-FTTH-500-RES",
            "name": "FTTH 500M Residential",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-10002", "Ioannis Kouris")],
    },
    {
        "name": "FTTH Residential 1G - Patras",
        "description": "Fixed-line gigabit FTTH with premium Wi-Fi router and voice service.",
        "status": "provisioned",
        "productOffering": {
            "id": "PO-FTTH-1G-RES",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-FTTH-1G-RES",
            "name": "FTTH 1G Residential",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-10003", "Maria Nikolaou")],
    },
    {
        "name": "VDSL Residential 100M - Larissa",
        "description": "Fixed-line VDSL over copper with VoIP voice and managed CPE.",
        "status": "active",
        "productOffering": {
            "id": "PO-VDSL-100-RES",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-VDSL-100-RES",
            "name": "VDSL 100M Residential",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-10004", "Giorgos Manos")],
    },
    {
        "name": "VDSL Residential 50M - Volos",
        "description": "Fixed-line VDSL 50 Mbps package with SIP voice migration.",
        "status": "active",
        "productOffering": {
            "id": "PO-VDSL-50-RES",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-VDSL-50-RES",
            "name": "VDSL 50M Residential",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-10005", "Sofia Arvaniti")],
    },
    {
        "name": "Business Ethernet 1G - Retail Chain HQ",
        "description": "Fixed-line dedicated Ethernet with 99.95% SLA.",
        "status": "active",
        "productOffering": {
            "id": "PO-ETH-1G-BIZ",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-ETH-1G-BIZ",
            "name": "Business Ethernet 1G",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20001", "RetailOne S.A.")],
    },
    {
        "name": "Business Ethernet 10G - Data Center Interconnect",
        "description": "Fixed-line 10G DCI service between metro PoPs.",
        "status": "provisioned",
        "productOffering": {
            "id": "PO-ETH-10G-BIZ",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-ETH-10G-BIZ",
            "name": "Business Ethernet 10G",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20002", "CloudAxis Ltd.")],
    },
    {
        "name": "MPLS L3VPN 5 Sites - Banking Branches",
        "description": "Fixed-line MPLS VPN interconnecting 5 branch sites.",
        "status": "active",
        "productOffering": {
            "id": "PO-MPLS-5SITE-BIZ",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-MPLS-5SITE-BIZ",
            "name": "MPLS L3VPN 5 Sites",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20003", "Hellenic Trust Bank")],
    },
    {
        "name": "MPLS L3VPN 12 Sites - Logistics Network",
        "description": "Fixed-line MPLS with 12 locations and centralized breakout.",
        "status": "ordered",
        "productOffering": {
            "id": "PO-MPLS-12SITE-BIZ",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-MPLS-12SITE-BIZ",
            "name": "MPLS L3VPN 12 Sites",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20004", "Aegean Logistics S.A.")],
    },
    {
        "name": "SIP Trunk 30 Channels - Hotel Group",
        "description": "Fixed-line enterprise SIP trunk for PBX with 30 channels.",
        "status": "active",
        "productOffering": {
            "id": "PO-SIPTRUNK-30",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-SIPTRUNK-30",
            "name": "SIP Trunk 30 Channels",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20005", "Mediterranean Hotels Group")],
    },
    {
        "name": "P2P Leased Line 100M - Municipal Services",
        "description": "Fixed-line point-to-point leased line for municipal backhaul.",
        "status": "active",
        "productOffering": {
            "id": "PO-LL-100M",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-LL-100M",
            "name": "Leased Line 100M",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-20006", "City of Heraklion")],
    },
    {
        "name": "Wholesale Local Loop - ISP Partner",
        "description": "Fixed-line wholesale local loop access for partner ISP resale services.",
        "status": "suspended",
        "productOffering": {
            "id": "PO-WLL-WHOLESALE",
            "href": "https://host:port/productCatalogManagement/v5/productOffering/PO-WLL-WHOLESALE",
            "name": "Wholesale Local Loop",
            "@type": "ProductOfferingRef",
            "@referredType": "ProductOffering",
        },
        "relatedParty": [related_customer("45hj-30001", "OpenNet ISP")],
    },
]


def post_product(base_url: str, product: dict) -> str | None:
    """POST a single product and return the created product id."""
    payload = {
        "@type": "Product",
        **product,
    }

    req = urllib.request.Request(
        f"{base_url}{ENDPOINT}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("id")
    except Exception as error:
        print(f"  ✗ Error creating product: {error}")
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed TMF637 Product Inventory.")
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL of the backend (default: http://localhost:8082)",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    print(f"Seeding {len(PRODUCTS)} fixed-line products to {base_url}{ENDPOINT}...\n")

    created_ids: list[str] = []
    for index, product in enumerate(PRODUCTS, 1):
        product_id = post_product(base_url, product)
        if product_id:
            created_ids.append(product_id)
            print(f"{index:3d}. ✓ {product['name'][:52]:52} → {product_id}")
        else:
            print(f"{index:3d}. ✗ {product['name'][:52]:52}")

    print(f"\n✓ Created {len(created_ids)} products successfully.")


if __name__ == "__main__":
    main()
