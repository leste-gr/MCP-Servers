"""Seed script for TMF638 Service Inventory backend.

Usage:
    python scripts/seed_tmf638.py [--base-url http://localhost:8081]
"""
import argparse
import json
import urllib.request

BASE_URL = "http://localhost:8081"
ENDPOINT = "/tmf-api/serviceInventory/v5/service"

SERVICES = [
    # --- Mobile Voice ---
    {
        "name": "Mobile Voice – Subscriber 07700900001",
        "description": "4G/5G mobile voice service for consumer subscriber. Includes VoLTE, Wi-Fi calling, and international roaming on partner networks.",
        "serviceType": "MobileVoice",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Mobile Voice – Subscriber 07700900002",
        "description": "Mobile voice service provisioned on 5G NSA. VoLTE enabled. Roaming restricted to EU zone.",
        "serviceType": "MobileVoice",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Mobile Voice – Subscriber 07700900003",
        "description": "Prepaid mobile voice service, top-up balance active. International dialing disabled.",
        "serviceType": "MobileVoice",
        "state": "suspended",
        "operatingStatus": "stopped",
    },
    {
        "name": "Mobile Voice – Corporate Group ACME Corp",
        "description": "Corporate mobile voice bundle for ACME Corp – 250 SIM group plan with shared minutes pool and priority QoS.",
        "serviceType": "MobileVoice",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- Mobile Data ---
    {
        "name": "Mobile Data – Subscriber 07700900001",
        "description": "5G SA mobile data service, 100 GB/month fair-use policy. Uses dedicated network slice for consumer broadband.",
        "serviceType": "MobileData",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Mobile Data – IoT SIM Fleet Batch A",
        "description": "NB-IoT data service for smart meter fleet – 500 SIM cards, 1 MB/month per SIM, static private APN.",
        "serviceType": "MobileData",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Mobile Data – Subscriber 07700900020 (throttled)",
        "description": "Mobile data throttled to 1 Mbps after fair-use threshold exceeded. Subscriber notified via SMS.",
        "serviceType": "MobileData",
        "state": "active",
        "operatingStatus": "limited",
    },
    {
        "name": "Mobile Data – Enterprise APN Corp-NET-01",
        "description": "Dedicated enterprise APN for secure remote worker mobile data. MPLS breakout at enterprise HQ. 10 Gbps aggregate capacity.",
        "serviceType": "MobileData",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- Fixed Broadband (FTTH) ---
    {
        "name": "FTTH 1 Gbps – Residential Customer 100234",
        "description": "Fiber-to-the-home 1 Gbps symmetrical broadband. GPON OLT port 3/1/4. ONT serial: HWTC-A1234567. PPPoE session active.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "FTTH 500 Mbps – Residential Customer 100456",
        "description": "Fiber-to-the-home 500/100 Mbps broadband. Includes residential VoIP line. ONT provisioned with dual GEM port.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "FTTH 250 Mbps – Customer 100789 (fault active)",
        "description": "Broadband service degraded. ONT upstream signal intermittent. Field engineer visit scheduled.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "degraded",
    },
    {
        "name": "FTTB 10 Gbps – Business Park PARKWAY-01",
        "description": "Fiber-to-the-building aggregated uplink for PARKWAY-01 business park. Dedicated OLT chassis port, SLA 99.99%.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "VDSL2 80 Mbps – Residential Customer 200011",
        "description": "VDSL2 broadband via copper loop 850 m. DSLAM port: DSLAM-SUBURB-04/6/12. SNR margin: 8 dB.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "ADSL2+ 24 Mbps – Customer 200099 (legacy)",
        "description": "Legacy ADSL2+ service pending migration to FTTH. No upgrade consent from subscriber yet.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "FTTH 1 Gbps – New Order Customer 300012 (reserved)",
        "description": "Service ordered, OLT port reserved, ONT shipping. Activation pending customer installation appointment.",
        "serviceType": "FixedBroadband",
        "state": "reserved",
        "operatingStatus": "pending",
    },
    # --- Business VPN / MPLS ---
    {
        "name": "MPLS L3VPN – Enterprise Customer GLOBAL FINANCE LTD",
        "description": "Layer 3 MPLS VPN interconnecting 12 branch sites. BGP PE-CE routing, bandwidth 1 Gbps per site, QoS 5-class model.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "MPLS L3VPN – Enterprise Customer MEDTECH GROUP",
        "description": "Dedicated MPLS VPN for medical data transfer. HIPAA-compliant network segmentation. 4 hospital sites, 100 Mbps CIR each.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "SD-WAN Managed Service – RETAIL CHAIN CO",
        "description": "SD-WAN overlay for 45 retail branches. Active/active DIA + LTE failover. Centralized policy from vManage controller.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "VPLS Metro Ethernet – LOGISTICS CORP ring",
        "description": "VPLS service across 6-node metro Ethernet ring for LOGISTICS CORP. 10 Gbps ring capacity, per-VLAN QoS.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "IPSec VPN – Remote Office BRANCH-EAST-07",
        "description": "Site-to-site IPSec VPN for BRANCH-EAST-07 back to HQ. IKEv2, AES-256-GCM. Failover to 4G backup tunnel.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "MPLS L3VPN – Customer ALPHA TRADING (degraded)",
        "description": "One PE–CE link at ALPHA TRADING site 3 down. Traffic rerouted via backup LSP at reduced bandwidth.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "degraded",
    },
    # --- VoIP / Unified Communications ---
    {
        "name": "SIP Trunking – Enterprise CORP-TELCO-00145",
        "description": "SIP trunk with 50 concurrent channels for CORP-TELCO-00145. Direct inward dialing range 0207-000-0000 to 0207-000-0499.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Hosted PBX – SME Customer STARTUP CO",
        "description": "Cloud-hosted PBX with 20 extensions, auto-attendant, voicemail-to-email. SIP endpoints registered to IMS core.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Carrier-grade Wholesale VoIP – Partner BETA-TEL",
        "description": "Wholesale international VoIP termination agreement with BETA-TEL. 5,000 CPS capacity, codec G.711/G.729.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Emergency Call Service – IMS E911 Zone East",
        "description": "PSAP emergency routing service for IMS subscribers in eastern zone. Location database integration via HELD protocol.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "SIP Trunking – Customer BIG RETAIL (fault)",
        "description": "SIP trunk experiencing call drops. Correlated with INC-VOIP-001. Temporary channel increase requested.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "failed",
    },
    # --- IPTV ---
    {
        "name": "IPTV Standard Package – Residential Customer 100234",
        "description": "300-channel IPTV linear service delivered over managed FTTH access. IGMP v3 multicast, STB provisioned with subscriber profile.",
        "serviceType": "IPTVService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "IPTV Premium Package – Residential Customer 100456",
        "description": "Premium IPTV including sports and movie packages. 4K UHD streams, Catch-Up TV 30-day recording, nPVR 200 h.",
        "serviceType": "IPTVService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "IPTV Service – Customer 100502 (EPG error)",
        "description": "Electronic programme guide data missing for channels 100-120. EPG mediation feed delayed – ticket raised.",
        "serviceType": "IPTVService",
        "state": "active",
        "operatingStatus": "degraded",
    },
    {
        "name": "OTT TV Platform – Streaming Service STREAMCO",
        "description": "Managed CDN-delivered OTT TV service for STREAMCO. 50 Gbps committed bandwidth, anycast PoP delivery.",
        "serviceType": "IPTVService",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- IoT / M2M ---
    {
        "name": "Smart Meter Connectivity – ENERGY-CO Fleet Zone A",
        "description": "NB-IoT M2M service for 12,000 electricity smart meters. Private APN, dedicated HLR profile, low-power PSM/eDRX enabled.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Connected Vehicle Telemetry – AUTO-OEM Fleet",
        "description": "LTE-M connected car telemetry for 3,000 vehicles. Real-time GPS, OBD-II diagnostics, over-the-air update channel.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Industrial IoT Gateway – FACTORY-01",
        "description": "Private 5G campus network slice for FACTORY-01. Ultra-low latency URLLC slice for robot arm control and AR glasses.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Smart City Sensors – METRO CONTRACT",
        "description": "LoRaWAN-to-4G backhaul for 5,000 environmental monitoring sensors across metro area. MVNO profile on shared RAN.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "M2M SIM – Vending Machine Fleet VENDO-UK",
        "description": "2G/4G M2M service for 800 vending machines. Remote diagnostics, cashless payment transaction channel.",
        "serviceType": "IoTConnectivity",
        "state": "inactive",
        "operatingStatus": "stopped",
    },
    # --- Cloud Interconnect ---
    {
        "name": "Cloud Connect – AWS Direct Connect 10 Gbps",
        "description": "Dedicated 10 Gbps interconnect to AWS us-east-1 region via carrier PoP. BGP ASN 64512, private VIF for VPC peering.",
        "serviceType": "CloudConnect",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Cloud Connect – Azure ExpressRoute 1 Gbps",
        "description": "ExpressRoute circuit 1 Gbps to Azure West Europe. Private peering for VM workloads, Microsoft peering for O365.",
        "serviceType": "CloudConnect",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Cloud Connect – Google Cloud Interconnect 10 Gbps",
        "description": "Dedicated interconnect to GCP europe-west1. Partner interconnect, VLAN attachment, single redundant pair.",
        "serviceType": "CloudConnect",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Multi-Cloud Hub – Enterprise FINANCE-CORP",
        "description": "Managed multi-cloud on-ramp for FINANCE-CORP connecting AWS, Azure, and on-prem DC. SD-WAN integrated, 40 Gbps aggregate.",
        "serviceType": "CloudConnect",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Cloud Connect – AWS Direct Connect (failover circuit)",
        "description": "Secondary 1 Gbps Direct Connect for redundancy. Normally in standby; activated on primary failure.",
        "serviceType": "CloudConnect",
        "state": "reserved",
        "operatingStatus": "configured",
    },
    # --- Wholesale / Carrier ---
    {
        "name": "International Private Leased Circuit – JAPAN-LINK-01",
        "description": "10 Gbps IPLC between London PoP and Tokyo PoP. SDH STM-64 bearer. 30 ms one-way latency SLA.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Wholesale Ethernet – Partner ISP-BETA 100 Gbps",
        "description": "100 Gbps Ethernet Wholesale NNI for ISP-BETA traffic aggregate. LAG of 4×25G, LACP active.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "MVNO Host Service – Virtual Operator CHEAP-MOBILE",
        "description": "Full MVNO hosting for CHEAP-MOBILE on national RAN. Separate HLR partition, virtual SMSC, MVNO billing mediation.",
        "serviceType": "MVNOHost",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "IP Transit 10 Gbps – Customer ISP-GAMMA",
        "description": "Upstream IP transit service for ISP-GAMMA. Full BGP routing table, AS12345. DDoS scrubbing included.",
        "serviceType": "IPTransit",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- Security / Managed Services ---
    {
        "name": "DDoS Protection – Enterprise BANK-CO",
        "description": "Always-on DDoS mitigation for BANK-CO public IP range /24. Scrubbing centre capacity 400 Gbps. < 30 s mitigation time SLA.",
        "serviceType": "ManagedSecurity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Managed Firewall – SME Customer ACCOUNTANTS-INC",
        "description": "Next-gen firewall as a service (FWaaS) for ACCOUNTANTS-INC. IPS/IDS, URL filtering, remote admin via portal.",
        "serviceType": "ManagedSecurity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Secure Internet Gateway – Enterprise HEALTHCARE-GROUP",
        "description": "Cloud-secure web gateway for 2,000 healthcare employees. SSL inspection, CASB, zero-trust access proxy.",
        "serviceType": "ManagedSecurity",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- Infrastructure / Platform ---
    {
        "name": "Virtual Network Function – vEPC cluster CORE-EPC-01",
        "description": "Virtualised EPC (MME, SGW, PGW) cluster deployed on NFV infrastructure. 4G/5G NSA subscriber anchor, 10 M subscriber capacity.",
        "serviceType": "VNFInstance",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Slice – eMBB Consumer 5G SA",
        "description": "5G SA enhanced mobile broadband slice. SST=1, SD=000001. 20 Gbps aggregate DL throughput, PRB reservation 40%.",
        "serviceType": "NetworkSlice",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Slice – URLLC Industrial 5G SA",
        "description": "Ultra-reliable low-latency 5G slice for private campus deployments. SST=2, < 1 ms RTT, 99.9999% availability target.",
        "serviceType": "NetworkSlice",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Slice – mMTC IoT 5G SA",
        "description": "Massive IoT 5G slice for smart-city and smart-meter mass connectivity. SST=3, up to 1 M devices/km².",
        "serviceType": "NetworkSlice",
        "state": "designed",
        "operatingStatus": "configured",
    },
    {
        "name": "CDN Node – PoP LONDON-EAST-01",
        "description": "Content delivery network PoP in London East DC. 2 Tbps caching capacity, 40 Gbps transit uplinks, HTTP/2 + QUIC.",
        "serviceType": "CDNService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "CDN Node – PoP MANCHESTER-01",
        "description": "CDN PoP in Manchester tier-2 DC. 500 Gbps cache, 10 Gbps uplinks. Origin shield for South UK region.",
        "serviceType": "CDNService",
        "state": "active",
        "operatingStatus": "running",
    },
    # --- Terminated / Historical ---
    {
        "name": "ISDN BRI – Legacy Customer 400012 (terminated)",
        "description": "ISDN BRI service terminated on customer request 2024-01-15. Circuit decommissioned, copper loop released.",
        "serviceType": "FixedVoice",
        "state": "terminated",
        "operatingStatus": "stopped",
    },
    {
        "name": "ATM PVC – Legacy Enterprise OLDBANK-PLC (terminated)",
        "description": "ATM permanent virtual circuit decommissioned after migration to MPLS VPN. All PVCs released.",
        "serviceType": "WholesaleLeased",
        "state": "terminated",
        "operatingStatus": "stopped",
    },
    {
        "name": "PSTN POTS Line – Customer 400099 (terminated)",
        "description": "Plain old telephone service terminated. Customer migrated to VoIP. Number ported to new provider.",
        "serviceType": "FixedVoice",
        "state": "terminated",
        "operatingStatus": "stopped",
    },
    # --- In Design / Feasibility ---
    {
        "name": "FTTH 10 Gbps – New Build Estate GREENFIELD-A",
        "description": "Service design for 500-home new-build FTTH deployment. Full fibre passive infrastructure planned. Awaiting planning approval.",
        "serviceType": "FixedBroadband",
        "state": "feasibilityChecked",
        "operatingStatus": "pending",
    },
    {
        "name": "Private 5G Campus – AIRPORT-TERMINAL-3",
        "description": "Feasibility completed for private 5G campus network at AIRPORT-TERMINAL-3. 3.5 GHz spectrum, 64T64R massive MIMO, design in progress.",
        "serviceType": "NetworkSlice",
        "state": "designed",
        "operatingStatus": "pending",
    },
    {
        "name": "Wholesale Dark Fibre – New Route CITY-A to CITY-B",
        "description": "Dark fibre pair on new 120 km buried route. Civil works awarded. Estimated go-live Q3 2026.",
        "serviceType": "WholesaleLeased",
        "state": "feasibilityChecked",
        "operatingStatus": "pending",
    },
    # --- Additional varied ---
    {
        "name": "LTE-M Asset Tracker – LOGISTICS CORP vehicle fleet",
        "description": "Real-time GPS + shock/temperature telemetry for 500 refrigerated trucks. 15-second reporting interval.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Satellite Backhaul – Remote Site NORTH-SCOTLAND-01",
        "description": "Ka-band VSAT satellite backhaul for remote community not reachable by terrestrial fibre. 100/20 Mbps.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Mobile Broadband – Emergency Services LTE MVNO",
        "description": "Priority LTE data SIM cards for 200 emergency response vehicles. Dedicated bearer with QCI 7, preemption capability.",
        "serviceType": "MobileData",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Time Protocol Service – Stratum-1 NTP Cluster",
        "description": "Managed NTP stratum-1 service for enterprise customers requiring traceable timing. GPS-disciplined oscillators, redundant nodes.",
        "serviceType": "ManagedNetworkService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "OSS/BSS Integration Bus – Internal Platform",
        "description": "Internal enterprise service bus connecting OSS (NMS, EMS) to BSS (CRM, billing). Kafka-based event streaming, 50k msg/s.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Analytics Platform – NOC Real-Time Visibility",
        "description": "Streaming telemetry ingestion (gNMI, IPFIX) feeding real-time anomaly detection and capacity planning dashboards.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Number Portability Platform – LNP Database Service",
        "description": "Local Number Portability database query service. 10k TPS, 99.999% availability, geo-redundant active-active.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Roaming Hub – GRX/IPX Peering Service",
        "description": "GRX/IPX roaming hub connecting 180 partner MNOs for data roaming. Diameter proxy, AA-Answer handling.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "DIAMETER Routing Agent – Core EPC Signalling",
        "description": "DRA cluster providing Diameter routing and load balancing between HSS, PCRF, and OCS nodes. 200k TPS peak.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "SMS Centre – SMSC Cluster National",
        "description": "National SMSC handling 15 M SMS/day. SS7 MAP interface to MSCs, REST API for enterprise A2P messaging.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "PCRF Policy Control – LTE Core",
        "description": "Policy and Charging Rules Function for LTE subscribers. Gx/Gy/Sd interface integration, dynamic QoS enforcement.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Online Charging System – OCS Prepaid/Postpaid",
        "description": "Convergent OCS supporting prepaid balance management and postpaid credit control. Gy interface to PCEF.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Carrier Ethernet – Metro Ring CITY-CENTRE-RING",
        "description": "10 GE metro ring serving 28 aggregation nodes in city centre. G.8032 Ethernet ring protection, < 50 ms failover.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Submarine Cable Landing Station – CABLE-SOUTH",
        "description": "Submarine cable landing station CABLE-SOUTH. Wet plant interface to 400 Gbps coherent DWDM terrestrial extension.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Residential VoIP – POTS Replacement Customer 100234",
        "description": "VoIP line bundled with FTTH broadband replacing legacy POTS. SIP registration to IMS core, CLIP/CLIR, voicemail.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "5G FWA – Fixed Wireless Access Customer RURAL-001",
        "description": "5G fixed wireless access CPE providing 300 Mbps download to rural premise. Outdoor CPE unit, 3.5 GHz.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "SD-WAN – Healthcare Trust NHS-TRUST-07",
        "description": "SD-WAN managed service for NHS-TRUST-07 with 18 clinic sites. FHIR API traffic prioritised, clinical imaging QoS.",
        "serviceType": "BusinessVPN",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Data Centre Interconnect – DC-NORTH to DC-SOUTH 400G",
        "description": "400 Gbps coherent DWDM DCI between DC-NORTH and DC-SOUTH. OTN ODU4 mapped Ethernet, 40 km span.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "GPON Aggregation Node – AGG-NODE-ZONE2",
        "description": "GPON aggregation service for Zone 2 covering 1,200 ONTs across 6 distribution points. Upstream 10GE uplinks.",
        "serviceType": "FixedBroadband",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Diameter Home Subscriber Server – HSS Cluster A",
        "description": "HSS cluster A holding subscriber profiles for 5M LTE/IMS users. Cx/Sh interface, Diameter S6a to MME.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "VOIP Wholesale Termination – International Route ASIA-PAC",
        "description": "International wholesale voice termination to the Asia-Pacific region. 2,000 CPS, G.711, LCR routing via STP.",
        "serviceType": "VoIPService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Enterprise Wi-Fi – Managed Service OFFICE-CAMPUS-01",
        "description": "Managed enterprise Wi-Fi across 40,000 sqm office campus. 802.11ax (Wi-Fi 6E), 500 APs, cloud WLAN controller.",
        "serviceType": "ManagedNetworkService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Network Slicing Orchestrator – NSO Platform",
        "description": "5G network slice orchestration platform managing 12 active slices across 3 regions. ETSI MANO compliant.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Passive Optical WDM – ROADM LONDON-RING",
        "description": "ROADM-based WDM ring through central London street cabinets. 96-channel C-band, CDC-F capable.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "LTE Band 28 700 MHz Overlay – Rural Coverage",
        "description": "LTE 700 MHz spectrum rollout for rural coverage improvement. 200 new small cells, 50+ km rural radius improvement.",
        "serviceType": "MobileData",
        "state": "designed",
        "operatingStatus": "pending",
    },
    {
        "name": "VNF Auto-Scaling – vSGW cluster SCALE-GRP-01",
        "description": "Auto-scaling virtual SGW cluster responding to EPC traffic demand. Min 2, Max 8 VNF instances, MANO-driven.",
        "serviceType": "VNFInstance",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Zero-Touch Provisioning Platform – ZTP Service",
        "description": "ZTP service for automated network device bootstrap. DHCP option 66/67, Netconf/RESTCONF push, YANG data models.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "BSS Mediation Engine – CDR Collection Platform",
        "description": "OSS/BSS mediation platform collecting CDRs from SGSN, GGSN, PGW, OCS. Normalisation and billing feed delivery 5 min SLA.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Enterprise Leased Line – Dark Fibre DATACORP HQ",
        "description": "20 km dark fibre pair from DATACORP HQ to carrier PoP. CWDM-capable, customer-managed endpoints.",
        "serviceType": "WholesaleLeased",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "5G Private Network – Seaport PORTCO TERMINAL-1",
        "description": "On-premise 5G private network for PORTCO TERMINAL-1 crane automation and logistics tracking. 3.8 GHz band, MEC deployed.",
        "serviceType": "NetworkSlice",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "Smart Grid Communication – DSO ENERGY-NET Zone B",
        "description": "LTE dedicated network slice for distribution system operator ENERGY-NET grid control traffic. GOOSE/SV protection relay comms.",
        "serviceType": "IoTConnectivity",
        "state": "active",
        "operatingStatus": "running",
    },
    {
        "name": "IMS P-CSCF Cluster – Proxy CSCF HA Pair",
        "description": "Active-standby P-CSCF HA pair serving consumer IMS endpoints. SIP ALG, IPSec/SDES media security, Gm/Mw interface.",
        "serviceType": "PlatformService",
        "state": "active",
        "operatingStatus": "running",
    },
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
    created = 0

    for i, svc in enumerate(SERVICES):
        payload = {
            "@type": "Service",
            "name": svc["name"],
            "description": svc["description"],
            "serviceType": svc["serviceType"],
            "state": svc["state"],
            "operatingStatus": svc["operatingStatus"],
        }
        result = _post(base_url, payload)
        print(f"[{i+1:03d}] Created {result['id']} – {svc['name'][:65]}")
        created += 1

    print(f"\nDone. {created} services inserted.")


if __name__ == "__main__":
    main()
