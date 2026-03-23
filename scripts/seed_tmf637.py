"""Seed script for TMF637 Product Inventory backend.

Usage:
    python scripts/seed_tmf637.py [--base-url http://localhost:8082]
"""
import argparse
import json
import random
import urllib.request
from datetime import datetime, timedelta, UTC

BASE_URL = "http://localhost:8082"
ENDPOINT = "/tmf-api/productInventory/v5/product"

STATUSES = ["pending", "ordered", "provisioned", "active", "suspended", "inactive", "terminated"]

PRODUCTS = [
    # --- Mobile Services ---
    {
        "name": "Postpaid Voice Plan – 1000 Minutes",
        "description": "Unlimited national calling + 1000 international minutes with unlimited SMS to 150+ countries.",
        "status": "active",
        "productOffering": {
            "id": "PO-VOICE-001",
            "name": "1000 Min International Plan"
        },
    },
    {
        "name": "5G Data Plan – 100GB",
        "description": "Ultra-fast 5G mobile broadband with 100GB monthly allowance, priority network access.",
        "status": "active",
        "productOffering": {
            "id": "PO-DATA-5G-001",
            "name": "5G 100GB Premium"
        },
    },
    {
        "name": "Business Mobile Bundle for Teams",
        "description": "10 lines with shared 500GB data pool, enterprise management portal, dedicated support.",
        "status": "provisioned",
        "productOffering": {
            "id": "PO-BUNDLE-BIZ-001",
            "name": "Enterprise 10-Line Bundle"
        },
    },
    {
        "name": "IoT Connectivity – Low Bandwidth",
        "description": "M2M/IoT sim cards with optimized SMS/data for sensors, GPS trackers, vending machines.",
        "status": "active",
        "productOffering": {
            "id": "PO-IOT-LB-001",
            "name": "IoT Low-BW SIM"
        },
    },
    {
        "name": "Roaming Plus – Global Coverage",
        "description": "Add-on: Worldwide roaming with local rates in 190+ countries, auto-detection.",
        "status": "active",
        "productOffering": {
            "id": "PO-ROAM-001",
            "name": "Global Roaming Add-On"
        },
    },

    # --- Fixed/Broadband Services ---
    {
        "name": "Fiber Broadband 500 Mbps",
        "description": "Home broadband: FTTH 500 Mbps download / 100 Mbps upload, no cap, WiFi 6 router included.",
        "status": "active",
        "productOffering": {
            "id": "PO-FIBER-500-001",
            "name": "Home Fiber 500M"
        },
    },
    {
        "name": "Business Ethernet – 10 Gbps",
        "description": "Dedicated business-grade Ethernet circuit, SLA 99.99%, 24/7 technical support.",
        "status": "provisioned",
        "productOffering": {
            "id": "PO-ETH-10G-001",
            "name": "Business 10G Ethernet"
        },
    },
    {
        "name": "MPLS VPN – Site-to-Site",
        "description": "Managed VPN connecting 5 remote locations via MPLS backbone, QoS prioritization.",
        "status": "active",
        "productOffering": {
            "id": "PO-MPLS-5SITE-001",
            "name": "MPLS VPN 5-Site"
        },
    },
    {
        "name": "DSL Internet Bundle + Phone Line",
        "description": "Legacy DSL 24 Mbps + analog phone service + caller ID/call waiting.",
        "status": "active",
        "productOffering": {
            "id": "PO-DSL-BUNDLE-001",
            "name": "DSL + Phone Bundle"
        },
    },

    # --- TV/Media Services ---
    {
        "name": "Premium TV – 400+ Channels",
        "description": "Full HD/4K channels: sports, movies, news, entertainment. Includes DVR box, 2 concurrent streams.",
        "status": "active",
        "productOffering": {
            "id": "PO-TV-PREM-001",
            "name": "Premium TV 400ch"
        },
    },
    {
        "name": "Streaming Video on Demand",
        "description": "Movie/series streaming: 10k+ titles in HD. Compatible with smart TV, tablets, phones.",
        "status": "active",
        "productOffering": {
            "id": "PO-VOD-001",
            "name": "Streaming VOD Service"
        },
    },
    {
        "name": "IPTV Basic – 150 Channels",
        "description": "IP-based TV service: 150 standard channels, HD quality, DVR 40 hours.",
        "status": "suspended",
        "productOffering": {
            "id": "PO-IPTV-BASIC-001",
            "name": "IPTV Basic 150ch"
        },
    },

    # --- Cloud/Enterprise ---
    {
        "name": "Cloud Backup – 1TB",
        "description": "Secure cloud backup service: automatic daily backup, 1TB storage, 5-year retention.",
        "status": "active",
        "productOffering": {
            "id": "PO-BACKUP-1TB-001",
            "name": "Cloud Backup 1TB"
        },
    },
    {
        "name": "Managed Firewall – Standard",
        "description": "Managed security: next-gen firewall, IPS/IDS, threat intel, managed updates.",
        "status": "active",
        "productOffering": {
            "id": "PO-FIREWALL-STD-001",
            "name": "Managed Firewall Std"
        },
    },
    {
        "name": "Private Cloud Hosting – 16 vCPU",
        "description": "Dedicated VM hosting: 16 vCPU, 64GB RAM, 500GB SSD, daily backup, monitoring.",
        "status": "provisioned",
        "productOffering": {
            "id": "PO-CLOUD-16VC-001",
            "name": "Private Cloud 16vCPU"
        },
    },
    {
        "name": "Email Security Gateway",
        "description": "Email protection: antispam, antivirus, DLP, encryption, archive 7-year retention.",
        "status": "active",
        "productOffering": {
            "id": "PO-EMAIL-SEC-001",
            "name": "Email Security Gateway"
        },
    },

    # --- Telephony ---
    {
        "name": "Hosted PBX – 50 Extensions",
        "description": "Cloud-based phone system: 50 extensions, IVR, call recording, mobile app, voicemail.",
        "status": "active",
        "productOffering": {
            "id": "PO-PBX-50EXT-001",
            "name": "Hosted PBX 50ext"
        },
    },
    {
        "name": "Conference Bridge – Unlimited",
        "description": "Audio/video conference: unlimited participants, recording, screen share, calendar integration.",
        "status": "active",
        "productOffering": {
            "id": "PO-CONF-UNLIM-001",
            "name": "Conference Unlimited"
        },
    },
    {
        "name": "International Trunk – E1 Primary",
        "description": "Primary E1 trunk for international calling: 30 channels, routing to 50+ countries.",
        "status": "ordered",
        "productOffering": {
            "id": "PO-TRUNK-E1-001",
            "name": "E1 International Trunk"
        },
    },

    # --- Additional Services ---
    {
        "name": "Static IP Address Block – /28",
        "description": "Fixed IPv4 block: 14 public IPs, suitable for small business web/mail hosting.",
        "status": "active",
        "productOffering": {
            "id": "PO-IP-BLOCK-28-001",
            "name": "IPv4 Block /28"
        },
    },
    {
        "name": "Network Monitoring & Analytics",
        "description": "Real-time network monitoring: bandwidth usage, anomaly detection, reports & alerts.",
        "status": "active",
        "productOffering": {
            "id": "PO-NET-MON-001",
            "name": "Network Monitoring"
        },
    },
    {
        "name": "Professional Installation Service",
        "description": "On-site installation & configuration for broadband/fiber connections & equipment.",
        "status": "pending",
        "productOffering": {
            "id": "PO-INSTALL-PROF-001",
            "name": "Professional Installation"
        },
    },
    {
        "name": "Extended Hardware Warranty – 3 Years",
        "description": "Equipment warranty extension: covers repairs, replacements, accidental damage.",
        "status": "active",
        "productOffering": {
            "id": "PO-WARRANTY-3YR-001",
            "name": "Hardware Warranty 3yr"
        },
    },
    {
        "name": "24/7 Premium Support Package",
        "description": "Priority support: phone/email/chat, <1 hour response time, dedicated account manager.",
        "status": "active",
        "productOffering": {
            "id": "PO-SUPPORT-PREM-001",
            "name": "Premium 24/7 Support"
        },
    },
]


def post_product(product: dict):
    """POST a single product."""
    payload = {
        "@type": "Product",
        **product,
    }
    req = urllib.request.Request(
        f"{BASE_URL}{ENDPOINT}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result.get("id")
    except Exception as e:
        print(f"  ✗ Error creating product: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Seed TMF637 Product Inventory.")
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL of the backend (default: http://localhost:8082)",
    )
    args = parser.parse_args()

    global BASE_URL
    BASE_URL = args.base_url

    print(f"Seeding {len(PRODUCTS)} products to {BASE_URL}{ENDPOINT}...\n")

    created_ids = []
    for i, product in enumerate(PRODUCTS, 1):
        product_id = post_product(product)
        if product_id:
            created_ids.append(product_id)
            print(f"{i:3d}. ✓ {product['name'][:40]:40} → {product_id}")
        else:
            print(f"{i:3d}. ✗ {product['name'][:40]:40}")

    print(f"\n✓ Created {len(created_ids)} products successfully.")


if __name__ == "__main__":
    main()
