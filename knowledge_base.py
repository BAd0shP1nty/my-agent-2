"""Telecom ITSM Knowledge Base: 3-Page Synthetic Dataset.

Domain: Telecommunications
Sub-domain: IT Service Management (ITSM), Incident Triage, and Problem Post-Mortems
"""

PAGE_1_TITLE = "Page 1: Architecture, Service Topology & ITSM Operational Framework"
PAGE_1_CONTENT = """================================================================================
PAGE 1: ARCHITECTURE, SERVICE TOPOLOGY & ITSM OPERATIONAL FRAMEWORK
Telecom Core & Digital BSS/OSS Operations | Service Management Standard
================================================================================

1. DOMAIN & SUBSYSTEM OVERVIEW
This knowledge base covers mission-critical telecommunications systems supporting 45+ million mobile prepaid and postpaid subscribers across domestic and international partner roaming routes.

Key Architectures and Subsystems:
* Passive Mediation & CDR Ingestion:
  - Responsible for harvesting raw Call Detail Records (CDRs), Data Usage Records (EDRs), and IP Flow Records from Mobile Switching Centers (MSC-SOUTH, MSC-NORTH), SGSN, and GGSN/PGW.
  - Ingestion collectors use SFTP, FTPS, and streaming Kafka pipelines (topics: telecom.cdr.raw, telecom.cdr.enriched).
  - Validation steps include column schema enforcement, duplicate detection (hashing IMSI + sequence + timestamp), and tax/circle code enrichment.
* Online Charging System (OCS) & Diameter Gy:
  - Real-time rating and credit control for prepaid voice, SMS, and data.
  - Interfaces via Diameter Gy/Ro interfaces (RFC 4006 / 3GPP TS 32.299), handling CCR-I (Initial), CCR-U (Update), and CCR-T (Termination) credit-control requests.
  - Utilizes low-latency in-memory cache clusters for balance reservations and an Oracle RAC persistence tier for financial ledgers.
* Core Network Signaling & Policy:
  - SS7/SIGTRAN network utilizing STP (Signaling Transfer Points) and SCCP (Signaling Connection Control Part) with Global Title Translation (GTT) tables.
  - PCRF (Policy and Charging Rules Function) / PCEF for dynamic bandwidth throttling, APN profile allocation, and QoS marking.
* Messaging & Voice Interconnect:
  - High-throughput Short Message Service Centers (SMSC) connected via SMPP v3.4 transceivers for OTP and campaign delivery.
  - Primary and secondary Session Border Controllers (SBC) terminating enterprise SIP trunks and international carrier interconnects.

2. ITSM INCIDENT PRIORITY MATRIX & SLA TARGETS
All incidents reported by NOC, automated telemetry, or partner escalations must be classified strictly according to this priority framework:

* P1 - Critical Incident:
  - Definition: Catastrophic disruption to revenue-generating services, complete failure of real-time OCS charging, loss of core signaling (SS7/Diameter), or network partition affecting >50,000 subscribers.
  - Target Response Time: 5 minutes.
  - Target Restoration SLA: Less than 2 hours.
  - Governance: Mandatory Major Incident Bridge, executive notification every 30 minutes, dedicated communications lead.
* P2 - High Priority:
  - Definition: Material service degradation, loss of platform redundancy (e.g., active-standby failover failure, degraded secondary routes), severe queue backlog in mediation (>30 min delay), or elevated API error rate (>5%).
  - Target Response Time: 15 minutes.
  - Target Restoration SLA: Less than 4 hours.
  - Governance: Technical resolver bridge, incident timeline logging, 60-minute stakeholder updates.
* P3 - Medium Priority:
  - Definition: Localized operational impact, non-service affecting reporting delays (e.g., daily reconciliation batch late), minor administrative tool access issues, or minor configuration variances with approved workarounds.
  - Target Response Time: 60 minutes.
  - Target Restoration SLA: Within 24 hours.
  - Governance: Handled by L2 support queue with standard ticket updates.

3. TRIAGE & ESCALATION PROTOCOL
- Phase 1: Alarm Detection & Correlation (0-10 min): NOC correlates synthetic transaction probes, Prometheus/Grafana metric alerts, and carrier notifications against CMDB Configuration Items (CIs).
- Phase 2: Boundary Scoping & Blast Radius Isolation (10-30 min): Verify route health, consumer lag, and failover status.
- Phase 3: Rollback & Recovery Execution: Prioritize restoring traffic over root cause analysis; execute certified runbooks.
- Phase 4: Post-Incident Review (PIR): Mandatory within 5 business days for P1/P2 incidents. Must yield concrete preventive actions and Known Error Database (KEDB) updates.
"""

PAGE_2_TITLE = "Page 2: Standard Incident Records & Causal Post-Mortems (TEL-INC-2026 Series)"
PAGE_2_CONTENT = """================================================================================
PAGE 2: STANDARD INCIDENT RECORDS & CAUSAL POST-MORTEMS
Synthetic Production Post-Mortem Records (2026 Telecommunication Incidents)
================================================================================

INCIDENT RECORD: TEL-INC-2026-0001
- Title: CDR files from MSC-SOUTH not picked up by mediation collector for 42 minutes.
- Priority: P2 - High | Status: Resolved | Service: Mediation
- Component: File ingestion / SFTP | Resolver Group: Mediation L2 / Data Operations
- Business Impact: Delayed CDR processing for two mobile switching sites; downstream billing feeds were at risk, with no confirmed data loss.
- Root Cause: The SFTP partner service account password expired, causing repeated authentication failures during scheduled polling cycles.
- Contributing Process Gap: Credential expiry was omitted from the service account rotation calendar. The collector retried in a silent loop without emitting an actionable authentication alert.
- Resolution & Recovery: Renewed the service credentials, replayed missed file batches, and reconciled source and target record counts.
- Preventive Action: Added credential-expiry monitoring with automated 30-day rotation reminders; configured explicit alerts on consecutive SFTP auth failures.
- Search Tags: sftp, cdr, ingestion, credentials, mediation

INCIDENT RECORD: TEL-INC-2026-0002
- Title: Destination-code table mapped international prefixes to domestic zone.
- Priority: P1 - Critical | Status: Resolved | Service: Mediation / Rating
- Component: Reference data / rating | Resolver Group: Mediation L2 / Data Operations
- Business Impact: Incorrect rating attributes generated for international CDRs. Billing accuracy was compromised across three major regional operating centers.
- Root Cause: A reference-data update package contained an erroneous prefix range due to manual spreadsheet editing.
- Contributing Process Gap: Pre-production validation only checked row counts rather than verifying prefix-range semantics or testing sample rating outcomes.
- Resolution & Recovery: Rolled back the reference-data package, reprocessed 184,000 affected CDRs, and completed sample rating reconciliations with billing.
- Preventive Action: Implemented strict schema and semantic validation rules, mandatory dual-engineer approval for reference tables, and automated golden-record test suites.
- Search Tags: reference-data, rating, cdr, data-quality, p1

INCIDENT RECORD: TEL-INC-2026-0003
- Title: Diameter credit-control requests intermittently timed out between OCS edge and partner gateway.
- Priority: P1 - Critical | Status: Resolved | Service: Online Charging
- Component: Diameter / Gy interface | Resolver Group: Charging L2 / OCS Operations
- Business Impact: Prepaid top-ups and session establishment were delayed or rejected for roaming subscribers on two partner networks.
- Root Cause: A recent firewall security policy update constricted the permitted ephemeral port range, creating intermittent TCP connection exhaustion under peak load.
- Contributing Process Gap: Change validation verified basic ICMP ping reachability but failed to execute sustained concurrent Diameter session load tests.
- Resolution & Recovery: Restored the approved ephemeral port allocation, drained stale TCP connections, and validated CCR/CCA success rates under simulated load.
- Preventive Action: Added protocol-level synthetic tests to firewall change validation checklists and enabled real-time connection-pool utilization telemetry.
- Search Tags: ocs, diameter, gy, firewall, timeout, p1

INCIDENT RECORD: TEL-INC-2026-0004
- Title: Prepaid subscribers received low-balance announcements immediately after successful recharge.
- Priority: P2 - High | Status: Closed | Service: Online Charging
- Component: Balance management | Resolver Group: Charging L2 / OCS Operations
- Business Impact: Customer experience degraded for approximately 1,800 subscribers; rating continued using stale balance snapshots.
- Root Cause: A cache invalidation event was dropped after the asynchronous recharge confirmation transaction committed to the database.
- Contributing Process Gap: The recharge workflow and balance cache relied on disconnected event consumers without an end-to-end distributed consistency checker.
- Resolution & Recovery: Replayed recharge event streams, invalidated affected Redis cache keys, and verified customer account balances against the ledger.
- Preventive Action: Implemented idempotent cache-invalidation retries, event-consumer lag alarms, and automated hourly ledger-to-cache reconciliation scripts.
- Search Tags: ocs, prepaid, balance, cache, recharge

INCIDENT RECORD: TEL-INC-2026-0005
- Title: SCCP translation failures increased sharply on the western signalling route.
- Priority: P1 - Critical | Status: Resolved | Service: Network Core
- Component: Core signalling / SS7 | Resolver Group: Core Network Operations
- Business Impact: USSD transactions and supplementary-service requests failed for subscribers homed on the western STP nodes.
- Root Cause: A routing table update contained a deprecated and obsolete Global Title Translation (GTT) entry.
- Contributing Process Gap: The change review process omitted route-by-route diff comparisons against the authoritative signaling plan.
- Resolution & Recovery: Restored the previous known-good translation table and confirmed transaction success across both redundant routing legs.
- Preventive Action: Automated routing-table diff checks and mandated two-person verification for any changes to global title translation tables.
- Search Tags: ss7, sccp, stp, routing, gtt, p1

INCIDENT RECORD: TEL-INC-2026-0012
- Title: CDR enrichment Kafka consumer group stopped committing offsets and lag grew rapidly.
- Priority: P1 - Critical | Status: Closed | Service: Integration
- Component: Kafka / event streaming | Resolver Group: Integration Support
- Business Impact: Enriched CDRs were delayed from reaching downstream billing and fraud analytics systems by over 85 minutes.
- Root Cause: A malformed event payload from a new network gateway version failed JSON deserialization, causing the consumer to block on partition 4.
- Contributing Process Gap: Dead-letter queue (DLQ) routing was accidentally disabled during the recent v2.4 schema upgrade, allowing poison pills to stall consumption.
- Resolution & Recovery: Quarantined the malformed poison pill message to an isolated topic, enabled the compatible deserializer, and resumed partition offset commits.
- Preventive Action: Mandated strict Avro schema registry checks, enforced active Dead-Letter Queues for all consumers, and enabled poison-message alerting.
- Search Tags: kafka, cdr, consumer-lag, schema, poison-pill, dlq, p1

INCIDENT RECORD: TEL-INC-2026-0030
- Title: Promotional data bundle consumed standard balance instead of promotional allowance.
- Priority: P1 - Critical | Status: Resolved | Service: Online Charging
- Component: Rating / tariff engine | Resolver Group: Charging L2 / OCS Operations
- Business Impact: Widespread customer overbilling complaints; standard monetary balances were drained before free data allowances.
- Root Cause: The newly deployed promotional offer priority was configured with an integer value lower than the default account bucket in the tariff chain.
- Contributing Process Gap: The offer regression test suite tested single buckets in isolation and failed to test overlapping bucket priority precedence.
- Resolution & Recovery: Corrected the tariff precedence hierarchy, refunded 14,200 affected subscriber sessions, and re-rated sampled usage records.
- Preventive Action: Maintained an exhaustive tariff precedence regression suite and required mandatory Product Owner sign-off on all charging rule configurations.
- Search Tags: ocs, rating, tariff, bundle, prepaid, precedence, p1
"""

PAGE_3_TITLE = "Page 3: Operational Runbooks, Preventive Guardrails & Change Governance"
PAGE_3_CONTENT = """================================================================================
PAGE 3: OPERATIONAL RUNBOOKS, PREVENTIVE GUARDRAILS & CHANGE GOVERNANCE
Standard Operating Procedures (SOPs) & Preventative Best Practices
================================================================================

RUNBOOK RB-ITSM-01: SERVICE ACCOUNT CREDENTIAL ROTATION & MONITORING
- Applicable Systems: Mediation SFTP gateways, database service accounts, Kafka SASL credentials, and partner REST API keys.
- Procedure:
  1. All production service accounts must be cataloged in the Enterprise Secret Manager (HashiCorp Vault / AWS Secrets Manager).
  2. Maximum credential lifespan is 90 days. Automated rotation warnings trigger at 30 days, 15 days, and 3 days before expiration.
  3. Secret updates must support a 48-hour overlap window where both old and new credentials remain valid to prevent operational lockouts.
  4. Workload pods must reload secrets dynamically or undergo an automated zero-downtime rolling restart upon secret version rotation.
- Enforcement: Audited weekly by Security Operations; unmanaged credentials result in immediate CI/CD deployment blocks.

RUNBOOK RB-ITSM-02: DIAMETER & SIGNALING FIREWALL CHANGE VALIDATION
- Applicable Systems: OCS Gy/Ro firewalls, SBC interconnects, and STP core routing firewalls.
- Verification Gates:
  1. Layer 4 Ephemeral Port Checks: Minimum ephemeral port range allocation must be 32,768 to 60,999 for Diameter edge nodes.
  2. Sustained Concurrency Test: Every firewall policy deployment must undergo a 15-minute synthetic test sustaining at least 12,000 concurrent Diameter connections.
  3. MTU & Fragmentation Verification: The path MTU must be locked to 1,500 bytes with Don't Fragment (DF) flags verified across all peering routes.
- Rollback Criteria: If connection acquisition timeouts exceed 0.2% during post-change observation, immediate automated rollback is triggered within 5 minutes.

RUNBOOK RB-ITSM-03: KAFKA CONSUMER LAG & POISON-PILL REMEDIATION
- Applicable Systems: Mediation event pipeline, CDR enrichment, and fraud stream analytics.
- Incident Response Steps:
  1. Step 1 (Detection): If consumer lag exceeds 50,000 messages or partition commit stall exceeds 120 seconds, trigger P2 alert to Integration Support.
  2. Step 2 (Isolation): Inspect consumer logs for SerializationException or DeserializationException.
  3. Step 3 (Quarantine): Ensure the consumer redirects the unparseable offset to the Dead-Letter Queue (DLQ topic: <topic_name>.DLQ) and increments the dlq_drop metric counter.
  4. Step 4 (Offset Seek): If the consumer remains stuck, manually seek the consumer group offset past the corrupted record:
     `kafka-consumer-groups --bootstrap-server <host>:9092 --group <group_id> --reset-offsets --to-offset <offset+1> --execute`
  5. Step 5 (Verification): Verify lag drains to zero and downstream billing totals match source mediation batches.

RUNBOOK RB-ITSM-04: TARIFF RULE RELEASE & RATING PRECEDENCE PROTOCOL
- Purpose: Prevent overbilling and incorrect wallet depletion during marketing campaigns and tariff plan updates.
- Mandatory Guardrails:
  1. Priority Ordering Rules:
     - Priority 10 (Highest): Special event / promo promotional data allowances (free buckets).
     - Priority 20: Add-on purchased bundle packs.
     - Priority 50: Plan standard monthly quota.
     - Priority 99 (Lowest): Main monetary balance (pay-as-you-go rating).
  2. Pre-Release Sandbox Validation: Run 5,000 synthetic rating CDRs simulating multi-bucket subscribers before committing changes to production OCS.
  3. Rollback Artifacts: Every change request must include pre-compiled SQL/API rollback scripts tested in staging.

RUNBOOK RB-ITSM-05: PROBLEM MANAGEMENT & KNOWN ERROR DATABASE (KEDB) LINKAGE
- Policy: Whenever an identical alert or symptom pattern recurs within 14 days, the incident analyst must link the ticket to a known Problem Record (PRB).
- Quality Standard: Workarounds documented in the KEDB must be applied within 20 minutes to preserve SLA clocks, while root cause engineering proceeds under the associated PRB ticket.
"""

# Bundle of all 3 pages
PAGES = [
    {"page": 1, "title": PAGE_1_TITLE, "content": PAGE_1_CONTENT},
    {"page": 2, "title": PAGE_2_TITLE, "content": PAGE_2_CONTENT},
    {"page": 3, "title": PAGE_3_TITLE, "content": PAGE_3_CONTENT},
]


def get_full_document_text() -> str:
    """Return the complete 3-page document text."""
    return "\n\n".join(p["content"] for p in PAGES)


def get_chunks() -> list[dict]:
    """Break the 3-page document into structured semantic chunks for RAG indexing.
    
    Each chunk contains clean text and rich metadata (page, section, incident_id, tags).
    """
    chunks = []

    # Page 1 Chunks
    chunks.append({
        "id": "p1-subsystems",
        "page": 1,
        "title": "Telecom Core & Digital BSS/OSS Subsystems Overview",
        "category": "Architecture",
        "tags": ["architecture", "mediation", "ocs", "diameter", "ss7", "smsc", "sbc"],
        "text": """Page 1 - Telecom Core & Digital BSS/OSS Subsystems Overview:
Passive Mediation & CDR Ingestion: Ingests raw Call Detail Records (CDRs) and data usage records from MSC-SOUTH, MSC-NORTH, and GGSN using SFTP, FTPS, and streaming Kafka (telecom.cdr.raw, telecom.cdr.enriched). Performs schema validation, duplicate detection (IMSI + sequence + timestamp), and tax/circle code enrichment.
Online Charging System (OCS) & Diameter Gy: Real-time rating and credit control for prepaid voice, SMS, and data. Uses Diameter Gy/Ro interfaces (RFC 4006 / 3GPP TS 32.299), handling CCR-I, CCR-U, and CCR-T requests. Relies on in-memory cache clusters and Oracle RAC persistence.
Core Network Signaling & Policy: SS7/SIGTRAN network using STP and SCCP with Global Title Translation (GTT) tables. PCRF/PCEF allocates dynamic bandwidth throttling and APN profiles.
Messaging & Voice: SMSC using SMPP v3.4 transceivers for OTP/campaigns; Session Border Controllers (SBC) for SIP trunks."""
    })

    chunks.append({
        "id": "p1-priority-matrix",
        "page": 1,
        "title": "ITSM Incident Priority Matrix & SLA Targets (P1, P2, P3)",
        "category": "Governance",
        "tags": ["itsm", "sla", "priority", "p1", "p2", "p3", "matrix"],
        "text": """Page 1 - ITSM Incident Priority Matrix and SLA Targets:
- P1 (Critical Incident): Catastrophic disruption to revenue-generating services, complete OCS charging failure, loss of core signaling (SS7/Diameter), or network partition affecting >50,000 subscribers. Target response time: 5 minutes. Target restoration SLA: < 2 hours. Mandatory Major Incident Bridge, executive notifications every 30 minutes, dedicated communications lead.
- P2 (High Priority): Material service degradation, loss of platform redundancy, queue backlog in mediation (>30 min delay), or elevated API error rate (>5%). Target response time: 15 minutes. Target restoration SLA: < 4 hours. Technical resolver bridge, 60-minute updates.
- P3 (Medium Priority): Localized operational impact, non-service affecting reporting delays (e.g. daily reconciliation batch late), minor admin tool issues. Target response time: 60 minutes. Restoration SLA: < 24 hours."""
    })

    chunks.append({
        "id": "p1-triage-protocol",
        "page": 1,
        "title": "Incident Triage, Blast Radius & Post-Incident Review Protocol",
        "category": "Processes",
        "tags": ["triage", "pir", "kedb", "blast-radius", "escalation"],
        "text": """Page 1 - Incident Triage & Escalation Protocol:
Phase 1: Alarm Detection & Correlation (0-10 min): NOC correlates synthetic transaction probes, Prometheus/Grafana metric alerts, and carrier notifications against CMDB Configuration Items (CIs).
Phase 2: Boundary Scoping & Blast Radius Isolation (10-30 min): Verify route health, consumer lag, and failover status.
Phase 3: Rollback & Recovery Execution: Prioritize restoring service traffic over root cause analysis using certified runbooks.
Phase 4: Post-Incident Review (PIR): Mandatory within 5 business days for all P1/P2 incidents. Must yield concrete preventive actions and Known Error Database (KEDB) updates."""
    })

    # Page 2 Chunks - Individual Incident Records
    chunks.append({
        "id": "tel-inc-2026-0001",
        "page": 2,
        "title": "TEL-INC-2026-0001: Mediation SFTP Collector CDR Delay (MSC-SOUTH)",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0001", "sftp", "cdr", "ingestion", "credentials", "mediation", "p2"],
        "text": """Incident Record TEL-INC-2026-0001:
Title: CDR files from MSC-SOUTH were not picked up by the mediation collector for 42 minutes.
Priority: P2 - High | Status: Resolved | Service: Mediation | Component: File ingestion / SFTP | Resolver Group: Mediation L2 / Data Operations.
Business Impact: Delayed CDR processing for two mobile switching sites; downstream billing feeds were at risk, with no confirmed data loss.
Root Cause: The SFTP partner service account password expired, causing repeated authentication failures during scheduled polling cycles.
Contributing Process Gap: Credential expiry was not included in the service account rotation calendar. The collector retried without raising an actionable alert.
Resolution / Recovery: Renewed the service credential, replayed missed file batches, and reconciled source and target record counts.
Preventive Action: Add credential-expiry monitoring and 30-day rotation reminders; alert on repeated SFTP authentication failures."""
    })

    chunks.append({
        "id": "tel-inc-2026-0002",
        "page": 2,
        "title": "TEL-INC-2026-0002: Destination-Code Rating Table Mapping Error",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0002", "reference-data", "rating", "cdr", "data-quality", "p1"],
        "text": """Incident Record TEL-INC-2026-0002:
Title: A newly deployed destination-code table mapped a group of international prefixes to the domestic zone.
Priority: P1 - Critical | Status: Resolved | Service: Mediation / Rating | Component: Reference data / rating | Resolver Group: Mediation L2 / Data Operations.
Business Impact: Incorrect rating attributes were generated for a subset of international CDRs. Billing accuracy was at risk across three regions.
Root Cause: A reference-data package contained an incorrect prefix range due to a manual spreadsheet edit.
Contributing Process Gap: Pre-production validation compared row counts but did not validate prefix-range semantics or sample rating outcomes.
Resolution / Recovery: Rolled back the reference-data package, reprocessed 184,000 affected CDRs, and completed sample rating reconciliation with billing.
Preventive Action: Introduce schema and semantic validation, peer approval for high-impact reference changes, and golden-record tests."""
    })

    chunks.append({
        "id": "tel-inc-2026-0003",
        "page": 2,
        "title": "TEL-INC-2026-0003: OCS Diameter Gy Credit-Control Timeout (Firewall Port Exhaustion)",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0003", "ocs", "diameter", "gy", "firewall", "timeout", "p1"],
        "text": """Incident Record TEL-INC-2026-0003:
Title: Diameter credit-control requests intermittently timed out between the OCS edge and a partner gateway.
Priority: P1 - Critical | Status: Resolved | Service: Online Charging | Component: Diameter / Gy interface | Resolver Group: Charging L2 / OCS Operations.
Business Impact: Prepaid top-ups and session establishment were delayed for subscribers on two partner networks.
Root Cause: A firewall policy update reduced the permitted ephemeral port range, creating intermittent TCP connection exhaustion under load.
Contributing Process Gap: The change validation checked basic reachability (ICMP) but did not exercise sustained concurrent Diameter sessions.
Resolution / Recovery: Restored approved port range, drained stale connections, and validated CCR/CCA success rates under load.
Preventive Action: Add protocol-level synthetic tests to firewall change validation and monitor connection-pool utilization."""
    })

    chunks.append({
        "id": "tel-inc-2026-0004",
        "page": 2,
        "title": "TEL-INC-2026-0004: Prepaid Balance Cache Invalidation Drop",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0004", "ocs", "prepaid", "balance", "cache", "recharge", "p2"],
        "text": """Incident Record TEL-INC-2026-0004:
Title: A subset of prepaid subscribers received low-balance announcements immediately after successful recharge.
Priority: P2 - High | Status: Closed | Service: Online Charging | Component: Balance management | Resolver Group: Charging L2 / OCS Operations.
Business Impact: Customer experience degraded for approximately 1,800 subscribers; charging continued using stale balance snapshots.
Root Cause: A cache invalidation event was missed after the asynchronous recharge confirmation was committed.
Contributing Process Gap: The recharge workflow and balance cache used separate event consumers without an end-to-end consistency check.
Resolution / Recovery: Replayed recharge events, invalidated affected cache keys, and verified account balances against the ledger.
Preventive Action: Add idempotent cache-invalidation retries, event-lag alarms, and ledger-to-cache reconciliation."""
    })

    chunks.append({
        "id": "tel-inc-2026-0005",
        "page": 2,
        "title": "TEL-INC-2026-0005: Core Signalling SS7 SCCP Translation Failures (Obsolete GTT)",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0005", "ss7", "sccp", "stp", "routing", "gtt", "p1"],
        "text": """Incident Record TEL-INC-2026-0005:
Title: SCCP translation failures increased sharply on the western signalling route.
Priority: P1 - Critical | Status: Resolved | Service: Network Core | Component: Core signalling / SS7 | Resolver Group: Core Network Operations.
Business Impact: USSD and selected supplementary-service transactions failed for subscribers served by the affected STPs.
Root Cause: A routing table update referenced an obsolete Global Title Translation (GTT) entry.
Contributing Process Gap: The peer review did not include a route-by-route comparison against the approved signalling plan.
Resolution / Recovery: Restored the previous translation table and confirmed transaction success across both redundant routes.
Preventive Action: Automate routing-table diff checks and require second-person validation for global title changes."""
    })

    chunks.append({
        "id": "tel-inc-2026-0012",
        "page": 2,
        "title": "TEL-INC-2026-0012: Kafka Consumer Lag & Poison-Pill Deserialization Failure",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0012", "kafka", "cdr", "consumer-lag", "schema", "poison-pill", "dlq", "p1"],
        "text": """Incident Record TEL-INC-2026-0012:
Title: The CDR enrichment consumer group stopped committing offsets and lag grew rapidly.
Priority: P1 - Critical | Status: Closed | Service: Integration | Component: Kafka / event streaming | Resolver Group: Integration Support.
Business Impact: Enriched CDRs were delayed from reaching downstream billing and fraud analytics by >85 minutes.
Root Cause: A malformed event repeatedly failed deserialisation and blocked partition 4.
Contributing Process Gap: Dead-letter handling was disabled for the new schema version, allowing one poison message to stall progress.
Resolution / Recovery: Quarantined the malformed event, enabled the compatible deserialiser, and resumed consumers from the last valid offset.
Preventive Action: Add schema compatibility checks, dead-letter queues (DLQ), and poison-message alarms."""
    })

    chunks.append({
        "id": "tel-inc-2026-0030",
        "page": 2,
        "title": "TEL-INC-2026-0030: Promotional Bundle Tariff Precedence Inversion",
        "category": "Incident Record",
        "tags": ["tel-inc-2026-0030", "ocs", "rating", "tariff", "bundle", "prepaid", "precedence", "p1"],
        "text": """Incident Record TEL-INC-2026-0030:
Title: A promotional data bundle consumed the standard balance instead of the promotional allowance.
Priority: P1 - Critical | Status: Resolved | Service: Online Charging | Component: Rating / tariff | Resolver Group: Charging L2 / OCS Operations.
Business Impact: Customer complaints increased and incorrect balance deductions were identified for a limited offer cohort.
Root Cause: The offer priority was lower than the default data bucket in the charging rule chain.
Contributing Process Gap: The offer regression suite did not test overlapping buckets and priority precedence.
Resolution / Recovery: Corrected bucket priority, refunded verified affected sessions, and re-rated sampled usage records.
Preventive Action: Maintain tariff precedence test cases and require product-owner approval for offer rule changes."""
    })

    # Page 3 Chunks - Standard Operating Procedures & Runbooks
    chunks.append({
        "id": "rb-itsm-01-credentials",
        "page": 3,
        "title": "Runbook RB-ITSM-01: Service Account Credential Rotation & Monitoring",
        "category": "Runbook",
        "tags": ["runbook", "credentials", "secrets", "rotation", "sftp", "vault"],
        "text": """Page 3 - Runbook RB-ITSM-01: Service Account Credential Rotation & Monitoring:
- Scope: Mediation SFTP gateways, database accounts, Kafka SASL credentials, partner REST API keys.
- Policies:
  1. All production service accounts must be cataloged in Enterprise Secret Manager.
  2. Maximum credential lifespan is 90 days. Automated rotation warnings trigger at 30 days, 15 days, and 3 days.
  3. Secret updates require a 48-hour overlap window where old and new credentials remain valid to prevent operational lockouts.
  4. Workload pods must reload secrets dynamically or undergo rolling restart upon secret version change.
- Enforcement: Weekly audit by Security Operations; unmanaged credentials block CI/CD deployments."""
    })

    chunks.append({
        "id": "rb-itsm-02-diameter-firewall",
        "page": 3,
        "title": "Runbook RB-ITSM-02: Diameter & Signaling Firewall Change Validation",
        "category": "Runbook",
        "tags": ["runbook", "diameter", "firewall", "ephemeral-ports", "mtu", "signaling"],
        "text": """Page 3 - Runbook RB-ITSM-02: Diameter & Signaling Firewall Change Validation:
- Scope: OCS Gy/Ro firewalls, SBC interconnects, and STP core routing firewalls.
- Verification Gates:
  1. Ephemeral Port Checks: Minimum ephemeral port range must be 32,768 to 60,999 for Diameter edge nodes.
  2. Sustained Concurrency Test: Every firewall policy deployment must undergo a 15-minute synthetic test sustaining at least 12,000 concurrent Diameter connections.
  3. MTU & Fragmentation: Path MTU must be locked to 1,500 bytes with Don't Fragment (DF) flags verified across all peering routes.
- Rollback Criteria: If connection acquisition timeouts exceed 0.2% during post-change observation, trigger immediate automated rollback within 5 minutes."""
    })

    chunks.append({
        "id": "rb-itsm-03-kafka-poison-pill",
        "page": 3,
        "title": "Runbook RB-ITSM-03: Kafka Consumer Lag & Poison-Pill Remediation",
        "category": "Runbook",
        "tags": ["runbook", "kafka", "poison-pill", "dlq", "consumer-lag"],
        "text": """Page 3 - Runbook RB-ITSM-03: Kafka Consumer Lag & Poison-Pill Remediation:
- Scope: Mediation event pipeline, CDR enrichment, and fraud stream analytics.
- Procedure:
  1. Detection: If consumer lag > 50,000 messages or commit stall > 120s, trigger P2 alert to Integration Support.
  2. Isolation: Inspect logs for SerializationException or DeserializationException.
  3. Quarantine: Ensure consumer redirects unparseable offset to Dead-Letter Queue (<topic_name>.DLQ) and increments dlq_drop metric counter.
  4. Offset Seek: If consumer remains stuck, manually seek consumer group offset past corrupted record using `kafka-consumer-groups --reset-offsets --to-offset <offset+1> --execute`.
  5. Verification: Verify lag drains to zero and downstream billing totals match source mediation batches."""
    })

    chunks.append({
        "id": "rb-itsm-04-tariff-precedence",
        "page": 3,
        "title": "Runbook RB-ITSM-04: Tariff Rule Release & Rating Precedence Protocol",
        "category": "Runbook",
        "tags": ["runbook", "tariff", "rating", "precedence", "ocs", "bundle"],
        "text": """Page 3 - Runbook RB-ITSM-04: Tariff Rule Release & Rating Precedence Protocol:
- Purpose: Prevent overbilling and incorrect wallet depletion during marketing campaigns and tariff plan updates.
- Mandatory Priority Ordering Hierarchy:
  * Priority 10 (Highest): Special event / promo promotional data allowances (free buckets).
  * Priority 20: Add-on purchased bundle packs.
  * Priority 50: Plan standard monthly quota.
  * Priority 99 (Lowest): Main monetary balance (pay-as-you-go rating).
- Pre-Release Sandbox Validation: Run 5,000 synthetic rating CDRs simulating multi-bucket subscribers before committing changes to production OCS.
- Rollback Artifacts: Every change request must include pre-compiled SQL/API rollback scripts tested in staging."""
    })

    chunks.append({
        "id": "rb-itsm-05-kedb",
        "page": 3,
        "title": "Runbook RB-ITSM-05: Problem Management & Known Error Database (KEDB) Linkage",
        "category": "Runbook",
        "tags": ["runbook", "kedb", "problem-management", "sla", "workaround"],
        "text": """Page 3 - Runbook RB-ITSM-05: Problem Management & Known Error Database (KEDB) Linkage:
- Policy: Whenever an identical alert or symptom pattern recurs within 14 days, the incident analyst must link the ticket to a known Problem Record (PRB).
- Quality Standard: Workarounds documented in the KEDB must be applied within 20 minutes to preserve SLA clocks, while root cause engineering proceeds under the associated PRB ticket.
- Review: Weekly repeat-incident trends must be reviewed by the Service Assurance board."""
    })

    return chunks
