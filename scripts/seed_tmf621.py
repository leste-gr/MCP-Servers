"""Seed script for TMF621 Trouble Ticket backend.

Usage:
    python scripts/seed_tmf621.py [--base-url http://localhost:8080]
"""
import argparse
import json
import random
import urllib.request
from datetime import datetime, timedelta, UTC

BASE_URL = "http://localhost:8080"
ENDPOINT = "/tmf-api/troubleTicket/v5/troubleTicket"

SEVERITIES = ["critical", "major", "minor", "cleared"]

STATUSES = [
    "acknowledged", "inProgress", "pending",
    "held", "resolved", "closed", "cancelled",
]

TICKETS = [
    # --- Network / Infrastructure ---
    {
        "name": "Fiber cut – Main trunk ring segment 4",
        "description": "Physical fiber cut detected on main trunk ring segment 4 between POP-NORTH and POP-EAST. Traffic rerouted via backup path; capacity reduced by 40%.",
        "severity": "critical",
        "status": "inProgress",
        "externalId": "INC-NW-001",
    },
    {
        "name": "BGP session flapping – Peering router RTR-CORE-02",
        "description": "BGP session to upstream ASN 12345 is flapping every 90 seconds on RTR-CORE-02. Potential cause: transient hardware error on line-card slot 3.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-NW-002",
    },
    {
        "name": "DWDM amplifier failure – OA-WEST-07",
        "description": "Optical amplifier OA-WEST-07 reporting Rx power below threshold. Affected span: 120 km. Backup amplifier not available on-site.",
        "severity": "critical",
        "status": "acknowledged",
        "externalId": "INC-NW-003",
    },
    {
        "name": "MPLS label switch path degradation – LSP-BACKBONE-09",
        "description": "LSP-BACKBONE-09 experiencing packet loss of ~3%. Root cause under investigation; traffic engineering re-route in progress.",
        "severity": "major",
        "status": "pending",
        "externalId": "INC-NW-004",
    },
    {
        "name": "Core router memory utilization exceeds 90% – RTR-CORE-01",
        "description": "RTR-CORE-01 memory at 91%. Route table size growth following new customer BGP peering. Engineering reviewing route summarization options.",
        "severity": "major",
        "status": "held",
        "externalId": "INC-NW-005",
    },
    # --- Mobile / RAN ---
    {
        "name": "eNodeB out of service – SITE-4G-2247",
        "description": "LTE eNodeB at SITE-4G-2247 (downtown area) offline due to power failure. UPS battery depleted; generator not available. ~800 subscribers affected.",
        "severity": "critical",
        "status": "acknowledged",
        "externalId": "INC-MOB-001",
    },
    {
        "name": "Handover failures spike – Cluster 12 LTE",
        "description": "Handover failure rate increased from 0.2% to 8% in Cluster 12. Preliminary analysis points to X2 interface misconfiguration after last night's software upgrade.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-MOB-002",
    },
    {
        "name": "5G NR gNB antenna tilt misconfiguration – SITE-5G-0089",
        "description": "Remote electrical tilt on sector 2 of SITE-5G-0089 drifted to +12° causing coverage hole of approx 0.8 km². Network engineer dispatched.",
        "severity": "minor",
        "status": "resolved",
        "externalId": "INC-MOB-003",
    },
    {
        "name": "S1-MME interface down – MME cluster A",
        "description": "S1-MME interface between eNB cluster A and MME-01 is down. UEs unable to attach. Fallback to MME-02 partial; overload alarms raised.",
        "severity": "critical",
        "status": "inProgress",
        "externalId": "INC-MOB-004",
    },
    {
        "name": "High RACH failure rate – SITE-4G-1102",
        "description": "Random Access Channel failure rate at SITE-4G-1102 elevated to 15%. Root access unit (RAU) reboot scheduled during maintenance window.",
        "severity": "minor",
        "status": "pending",
        "externalId": "INC-MOB-005",
    },
    # --- Broadband / DSL / FTTH ---
    {
        "name": "DSLAM line card fault – DSLAM-SUBURB-04 slot 6",
        "description": "Line card in slot 6 of DSLAM-SUBURB-04 failed. 48 DSL subscribers offline. Replacement card en route; ETA 4 hours.",
        "severity": "major",
        "status": "acknowledged",
        "externalId": "INC-DSL-001",
    },
    {
        "name": "OLT port degradation – OLT-FTTH-ZONE3 port 2/1",
        "description": "Upstream burst noise on OLT port 2/1 causing packet loss for 32 FTTH subscribers. Optical splitter replacement planned.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-DSL-002",
    },
    {
        "name": "Mass DSL sync-loss after firmware push – Region West",
        "description": "Firmware v4.12.1 pushed to DSLAMs in Region West caused mass sync-loss for ~1,200 lines. Rollback to v4.11.9 in progress.",
        "severity": "critical",
        "status": "inProgress",
        "externalId": "INC-DSL-003",
    },
    {
        "name": "VLAN misconfiguration – FTTH distribution node FDN-22",
        "description": "Incorrect VLAN tag assignment on FDN-22 uplink port causes traffic interleaving between residential and business segments.",
        "severity": "major",
        "status": "resolved",
        "externalId": "INC-DSL-004",
    },
    {
        "name": "Intermittent broadband drops – BRAS-CENTRAL high load",
        "description": "BRAS-CENTRAL CPU at 95% during evening peak causing PPPoE session drops. Traffic offload to BRAS-SECONDARY underway.",
        "severity": "major",
        "status": "held",
        "externalId": "INC-DSL-005",
    },
    # --- VoIP / IMS ---
    {
        "name": "SIP trunk capacity exceeded – Enterprise customer ACME Corp",
        "description": "ACME Corp SIP trunk reached maximum concurrent call limit (200 channels). Calls failing with 503. Temporary capacity increase requested.",
        "severity": "major",
        "status": "acknowledged",
        "externalId": "INC-VOIP-001",
    },
    {
        "name": "One-way audio – IMS P-CSCF-02 media anchor issue",
        "description": "Subscribers terminating calls on P-CSCF-02 experiencing one-way audio. Media anchor IP address mismatch in SDP after maintenance.",
        "severity": "critical",
        "status": "resolved",
        "externalId": "INC-VOIP-002",
    },
    {
        "name": "High jitter on VoIP calls – Transport link TRK-VoIP-08",
        "description": "Jitter exceeding 40 ms on VoIP transport link TRK-VoIP-08. QoS DSCP marking incorrect after router config change. Fix applied; monitoring.",
        "severity": "minor",
        "status": "resolved",
        "externalId": "INC-VOIP-003",
    },
    {
        "name": "ENUM lookup failures – DNS resolver overload",
        "description": "ENUM DNS resolvers returning SERVFAIL for ~5% of queries due to cache exhaustion. Additional resolver instances being provisioned.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-VOIP-004",
    },
    {
        "name": "IMS HSS unreachable intermittently – Diameter link flap",
        "description": "Diameter Cx interface between S-CSCF and HSS flapping causing registration failures for IMS subscribers. HSS load balancer under investigation.",
        "severity": "major",
        "status": "pending",
        "externalId": "INC-VOIP-005",
    },
    # --- Billing / OSS/BSS ---
    {
        "name": "CDR mediation pipeline stalled – Billing feed gap",
        "description": "CDR mediation engine stopped processing files from SGSN cluster since 03:00 UTC. ~2M records queued. Billing feed to downstream system delayed.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-BSS-001",
    },
    {
        "name": "Provisioning order stuck – Auto-activation for broadband batch 2024-03-22",
        "description": "Automated provisioning workflow stuck at 'activate-line' step for 45 orders. SOAP call to NMS timing out. NMS API health check failing.",
        "severity": "major",
        "status": "acknowledged",
        "externalId": "INC-BSS-002",
    },
    {
        "name": "CRM integration error – Customer data sync failure",
        "description": "Nightly sync from CRM to OSS failed at 02:15 UTC. 300 customer profile updates not replicated. Manual reconciliation needed.",
        "severity": "minor",
        "status": "pending",
        "externalId": "INC-BSS-003",
    },
    {
        "name": "Rating engine incorrect tariff applied – Roaming zone 3",
        "description": "Customers in roaming zone 3 incorrectly billed at domestic data rate since tariff table update on 2024-03-20. ~500 accounts affected.",
        "severity": "major",
        "status": "held",
        "externalId": "INC-BSS-004",
    },
    {
        "name": "Self-care portal – Password reset emails not delivered",
        "description": "SMTP relay from self-care portal to email gateway timing out. Customers unable to reset passwords. IT investigating relay configuration.",
        "severity": "minor",
        "status": "resolved",
        "externalId": "INC-BSS-005",
    },
    # --- Security ---
    {
        "name": "DDoS attack detected – Public DNS resolvers",
        "description": "Volumetric DDoS targeting public DNS resolvers; 18 Gbps traffic spike. Scrubbing center activated; BGP blackhole routes applied for attacking subnets.",
        "severity": "critical",
        "status": "resolved",
        "externalId": "INC-SEC-001",
    },
    {
        "name": "Unauthorized access attempt – NMS web console",
        "description": "Multiple failed SSH login attempts to NMS web console from external IP range 198.51.100.0/24. IP blocked; security team notified.",
        "severity": "major",
        "status": "closed",
        "externalId": "INC-SEC-002",
    },
    {
        "name": "SSL certificate expiry warning – Customer portal",
        "description": "TLS certificate for customer.portal.example.com expires in 7 days. Renewal request submitted but pending approval from PKI team.",
        "severity": "minor",
        "status": "pending",
        "externalId": "INC-SEC-003",
    },
    # --- Data Center / Cloud ---
    {
        "name": "Cooling failure – DC-SOUTH rack row B",
        "description": "CRAC unit CR-04 in DC-SOUTH rack row B offline. Ambient temperature rising. Non-critical servers powered down proactively pending repair.",
        "severity": "critical",
        "status": "acknowledged",
        "externalId": "INC-DC-001",
    },
    {
        "name": "Storage array latency spike – SAN-PRIMARY",
        "description": "SAN-PRIMARY I/O latency increased 10× due to background rebuild following disk failure. Affected: OSS database servers. Read cache being extended.",
        "severity": "major",
        "status": "inProgress",
        "externalId": "INC-DC-002",
    },
    {
        "name": "Hypervisor host failure – ESXI-HOST-14",
        "description": "ESXI-HOST-14 crashed with PSOD. 12 VMs HA-restarted on peer hosts. Capacity headroom now at 72%. RCA pending vendor support.",
        "severity": "major",
        "status": "resolved",
        "externalId": "INC-DC-003",
    },
]

EXTRA_NAMES = [
    ("Packet loss on inter-DC link – DC-NORTH to DC-SOUTH", "minor", "resolved"),
    ("NTP stratum-1 server unreachable – network timing degraded", "minor", "closed"),
    ("RADIUS authentication latency exceeds 500 ms – AAA cluster", "major", "resolved"),
    ("Subscriber database replication lag – SUBS-DB secondary 2", "minor", "pending"),
    ("VPN concentrator throughput degradation – VPN-GW-03", "major", "inProgress"),
    ("Alarm storm after SNMP community string rotation", "minor", "acknowledged"),
    ("GTP tunnel leak – GGSN-01 after upgrade", "major", "resolved"),
    ("IPTV multicast routing failure – IGMP snooping misconfiguration", "minor", "inProgress"),
    ("SDH tributary failure – STM-64 ring east segment", "critical", "acknowledged"),
    ("SMS-C high latency – message delivery delayed > 60 s", "minor", "resolved"),
    ("Roaming steering – IMSI range update blocking home subscribers", "major", "pending"),
    ("Firewall rule misconfiguration – blocking GRE to partner VPN", "major", "resolved"),
    ("Monitoring blackout – Zabbix server disk full", "minor", "closed"),
    ("DHCP pool exhaustion – BRAS-EAST residential pool /22", "major", "inProgress"),
    ("ODF fiber misrouting discovered during audit – POP-CENTRAL", "minor", "held"),
    ("Lawful intercept mediation system out of sync – audit gap", "critical", "acknowledged"),
    ("Outbound international SMTP blocked by RBL mis-listing", "minor", "resolved"),
    ("Carrier Ethernet SLA breach – CE-WAN-0042 latency > 10 ms", "minor", "closed"),
    ("Power surge damage – outdoor cabinet CAB-0781", "major", "resolved"),
    ("PLC network connectivity loss – smart meter collectors Zone 5", "minor", "acknowledged"),
    ("Interconnect CDR discrepancy with carrier BETA-TEL", "minor", "pending"),
    ("BGP route leak – customer AS advertising full table", "critical", "resolved"),
    ("Overheating alarm – microwave link MW-LINK-0055", "minor", "acknowledged"),
    ("IMS Emergency call routing failure – PSAP unreachable", "critical", "inProgress"),
    ("Packet duplication on LAG – LAG-DIST-07 LACP misconfiguration", "major", "resolved"),
    ("Subscriber quota enforcement failure – PCRF rule mismatch", "minor", "inProgress"),
    ("DNS zone file corruption – zone telco.internal", "critical", "resolved"),
    ("Optical power degradation – OA-EAST-03 after connector clean", "minor", "closed"),
    ("High CPU on EPC PGW-02 – GTP-C message flood", "major", "held"),
    ("SLA reporting data gap – PM collection agent crash", "minor", "resolved"),
    ("Wi-Fi offload AAA auth failures post certificate rotation", "minor", "inProgress"),
    ("Interconnect voice quality below MOS 3 – PSTN gateway GW-08", "major", "resolved"),
    ("Core dump on PCRF-01 – memory corruption under load", "critical", "acknowledged"),
    ("Ethernet OAM link-trace failure – metro Ethernet ring ring-03", "minor", "resolved"),
    ("Number portability database timeout – LNP query failures", "major", "inProgress"),
    ("DNS DNSSEC validation failure after key rollover – zone mobile.", "major", "resolved"),
    ("Fiber theft – 200 m cable stolen, 60 subscribers offline", "critical", "acknowledged"),
    ("IMS P-ASSERTED-IDENTITY stripping bug – IBCF-01", "minor", "resolved"),
    ("CDN cache poisoning alert – security incident raised", "critical", "closed"),
    ("L2VPN service down – VPLS mesh core BGP EVPN route withdrawn", "major", "inProgress"),
    ("Mobile data throttling not applying – PCEF policy push failure", "minor", "pending"),
    ("Out-of-Band management OOB-SWITCH-03 unresponsive", "minor", "resolved"),
    ("PAP/CHAP authentication loop – legacy corporate PPP customer", "minor", "closed"),
    ("Microwave rain fade – MW-LINK-0031 east region heavy rainfall", "minor", "resolved"),
    ("PON node power supply unit failure – OLT-FTTH-ZONE7", "major", "acknowledged"),
    ("MSRP file transfer service outage – enterprise unified comms", "minor", "inProgress"),
    ("GRE tunnel MTU mismatch – IPSec VPN fragmentation issue", "minor", "resolved"),
    ("Carrier billing dispute – interconnect invoice discrepancy Q1", "minor", "pending"),
    ("ICMP redirect misconfiguration causing routing loop CORE", "major", "resolved"),
    ("Alarm deduplication failure – NOC FMS receiving duplicate events", "minor", "acknowledged"),
    ("NMS network discovery timeout – new 5G segment not auto-provisioned", "minor", "pending"),
    ("SIP OPTIONS keepalive failure – SBC-02 session border controller", "minor", "inProgress"),
    ("VAS platform disk I/O bottleneck – RBT content filtering", "minor", "resolved"),
    ("OSS/BSS API gateway rate-limit triggered by batch job", "minor", "held"),
    ("eNodeB synchronization drift – GPS antenna cable fault", "major", "resolved"),
    ("SGSN charging gateway interface (Ga) link bouncing", "major", "inProgress"),
    ("UMTS IUBP transport congestion – ATM QoS AAL2 misconfiguration", "minor", "resolved"),
    ("Lawful intercept – missing delivery confirmation for intercept ID 4412", "critical", "acknowledged"),
    ("IPFIX/NetFlow collector disk full – capacity 100% on COL-01", "minor", "resolved"),
    ("CDR loss – billing pipeline crash recovery incomplete", "critical", "held"),
    ("IPTV EPG metadata feed delayed – provider FTP transfer failure", "minor", "inProgress"),
    ("Enterprise customer MPLS CE–PE routing protocol mismatch", "minor", "resolved"),
    ("Public cloud interconnect – AWS Direct Connect BGP flap", "major", "resolved"),
    ("5G SA UPF session anchor failure – N4 interface PFCP timeout", "critical", "inProgress"),
    ("Mobile roaming – MSISDN prefix table outdated, calls misrouted", "major", "acknowledged"),
    ("IMS charging failure – Rf interface ACR message drops", "major", "resolved"),
]


def _post(base_url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base_url}{ENDPOINT}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    now = datetime.now(UTC)
    created = 0

    for i, t in enumerate(TICKETS):
        payload = {
            "@type": "TroubleTicket",
            "name": t["name"],
            "description": t["description"],
            "severity": t["severity"],
            "externalId": t.get("externalId"),
        }
        result = _post(base_url, payload)
        print(f"[{i+1:03d}] Created {result['id']} – {t['name'][:60]}")
        created += 1

    for i, (name, severity, _status) in enumerate(EXTRA_NAMES):
        payload = {
            "@type": "TroubleTicket",
            "name": name,
            "description": f"Automated incident raised by NOC monitoring system. Severity: {severity}. Ticket opened for tracking and escalation.",
            "severity": severity,
            "externalId": f"INC-AUTO-{i+1:03d}",
        }
        result = _post(base_url, payload)
        print(f"[{len(TICKETS)+i+1:03d}] Created {result['id']} – {name[:60]}")
        created += 1

    print(f"\nDone. {created} trouble tickets inserted.")


if __name__ == "__main__":
    main()
