# RAG Evaluation Summary

**Generated:** 2026-09-24T07:18:40.749431  
**Queries Evaluated:** 50  
**Sample Size:** All  
**Generation Model:** gpt-4o-mini  
**Embedding Model:** text-embedding-3-small

---

## Aggregate Scores

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Faithfulness | 0.929 | ≥ 0.70 | ✅ PASS |
| Answer Relevance | 0.978 | — | — |
| Context Precision | 0.720 | ≥ 0.60 | ✅ PASS |
| Correctness | 0.829 | — | — |

---

## Score Distribution

### By Category

| Category | Count | Avg Faith. | Avg Relev. | Avg Prec. | Avg Correct. |
|----------|-------|------------|------------|-----------|-------------|
| admin | 7 | 0.95 | 1.00 | 0.94 | 0.95 |
| api | 14 | 0.97 | 0.98 | 0.76 | 0.90 |
| billing | 8 | 0.97 | 1.00 | 0.69 | 0.92 |
| csm | 1 | 0.80 | 1.00 | 0.67 | 0.56 |
| data | 5 | 0.88 | 0.94 | 0.57 | 0.77 |
| incident-response | 3 | 1.00 | 1.00 | 0.67 | 0.61 |
| integrations | 3 | 0.89 | 1.00 | 0.82 | 0.72 |
| mobile | 2 | 1.00 | 1.00 | 0.75 | 0.75 |
| workflows | 7 | 0.79 | 0.93 | 0.55 | 0.71 |

### By Difficulty

| Difficulty | Count | Avg Faith. | Avg Relev. | Avg Prec. | Avg Correct. |
|------------|-------|------------|------------|-----------|-------------|
| easy | 20 | 0.92 | 0.97 | 0.75 | 0.95 |
| hard | 10 | 0.91 | 0.94 | 0.49 | 0.64 |
| medium | 20 | 0.95 | 1.00 | 0.81 | 0.80 |

---

## Per-Query Results

| ID | Query | Faith. | Relev. | Prec. | Correct. |
|----|-------|--------|--------|-------|----------|
| Q001 | What's the maximum number of steps ... | 0.33 | 0.50 | 0.00 | 0.00 |
| Q002 | How long can a workflow run before ... | 1.00 | 1.00 | 0.00 | 1.00 |
| Q003 | How much does the Pro plan cost? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q004 | What's the API rate limit on the Pr... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q005 | What HTTP status code does Helix re... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q006 | What's the base URL for the Helix A... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q007 | What signing algorithm does Helix u... | 1.00 | 1.00 | 0.50 | 1.00 |
| Q008 | Which header contains the webhook s... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q009 | How many user roles does Helix have... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q010 | Which plan includes SSO? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q011 | How long is the audit log retained? | 0.67 | 1.00 | 1.00 | 1.00 |
| Q012 | How long are run logs retained on t... | 1.00 | 1.00 | 0.83 | 1.00 |
| Q013 | How long is a download URL for an e... | 1.00 | 1.00 | 0.33 | 1.00 |
| Q014 | How many workflow versions does Hel... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q015 | Are scheduled workflows in UTC or m... | 0.75 | 1.00 | 1.00 | 1.00 |
| Q016 | What's the API key format? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q017 | What does HTTP 401 mean from the He... | 0.60 | 1.00 | 0.50 | 1.00 |
| Q018 | What integrations does Helix suppor... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q019 | What mobile platforms are supported... | 1.00 | 1.00 | 0.50 | 1.00 |
| Q020 | What's the support response SLA on ... | 1.00 | 1.00 | 0.25 | 1.00 |
| Q021 | If a workflow step fails, when does... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q022 | How do I verify the signature on in... | 1.00 | 1.00 | 1.00 | 0.67 |
| Q023 | What's the difference between Pro a... | 1.00 | 1.00 | 0.50 | 0.90 |
| Q024 | Which roles can manage billing? | 1.00 | 1.00 | 0.83 | 1.00 |
| Q025 | Why am I getting 429 errors when I'... | 1.00 | 1.00 | 1.00 | 0.83 |
| Q026 | How do I cancel my subscription? | 0.75 | 1.00 | 1.00 | 1.00 |
| Q027 | What happens when I downgrade from ... | 1.00 | 1.00 | 0.50 | 1.00 |
| Q028 | How do I export my data for complia... | 0.75 | 1.00 | 0.42 | 0.00 |
| Q029 | What's the GDPR deletion process? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q030 | How do I set up SCIM provisioning? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q031 | What happens if my payment fails? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q032 | Can I edit workflows from the mobil... | 1.00 | 1.00 | 1.00 | 0.50 |
| Q033 | How do I rotate an API key safely? | 1.00 | 1.00 | 1.00 | 1.00 |
| Q034 | What's idempotency and how do I use... | 1.00 | 1.00 | 0.50 | 1.00 |
| Q035 | What do I do if I'm locked out by I... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q036 | Why does my Salesforce connection k... | 1.00 | 1.00 | 0.47 | 0.67 |
| Q037 | How do I send a Helix webhook to a ... | 0.67 | 1.00 | 1.00 | 0.50 |
| Q038 | What's the most efficient way to pr... | 0.80 | 1.00 | 0.50 | 0.50 |
| Q039 | How is overage usage billed on the ... | 1.00 | 1.00 | 1.00 | 1.00 |
| Q040 | What does Helix do when a webhook d... | 1.00 | 1.00 | 0.50 | 0.50 |
| Q041 | Our team is migrating from Okta to ... | 1.00 | 1.00 | 0.75 | 0.67 |
| Q042 | I'm seeing my workflow run time slo... | 0.67 | 1.00 | 0.33 | 0.50 |
| Q043 | Our auditor is asking for 18 months... | 0.67 | 0.70 | 0.25 | 0.83 |
| Q044 | We're getting paged at 3am because ... | 1.00 | 0.70 | 0.12 | 0.83 |
| Q045 | Our customer just renewed but we're... | 0.80 | 1.00 | 0.67 | 0.56 |
| Q046 | Customer says they were charged for... | 1.00 | 1.00 | 0.25 | 0.43 |
| Q047 | We need to fail over to our Postgre... | 1.00 | 1.00 | 1.00 | 0.78 |
| Q048 | We've decided to roll back a bad de... | 1.00 | 1.00 | 0.50 | 0.67 |
| Q049 | Customer's webhooks aren't being de... | 1.00 | 1.00 | 0.50 | 0.75 |
| Q050 | A customer is escalating because th... | 1.00 | 1.00 | 0.50 | 0.38 |

---

## ⚠️ Low-Scoring Queries (any metric < 0.5)

### Q001: What's the maximum number of steps allowed in a single workflow?

**Generated Answer:** The maximum number of steps allowed in a single workflow is not explicitly stated in the provided documents. However, it is mentioned that the total workflow runtime is capped at 30 minutes regardless of the number of steps. For specific limits on the number of steps, further information would be ne...

**Ground Truth:** The maximum number of steps in a single Helix workflow is 100....

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 0.33 | The claim about the total workflow runtime being capped at 30 minutes is supported by the context. H |
| Context Precision | 0.00 | Matched: [] |
| Correctness | 0.00 | Missing: ['The maximum number of steps in a single Helix workflow is 100.'] |

---

### Q002: How long can a workflow run before it times out?

**Generated Answer:** A workflow can run for a maximum of 30 minutes before it times out....

**Ground Truth:** A workflow run is terminated after 30 minutes. This is a platform-wide hard limit....

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | The claim in the answer is directly supported by the context, which states that the 30-minute max wo |
| Context Precision | 0.00 | Matched: [] |
| Correctness | 1.00 | Missing: [] |

---

### Q013: How long is a download URL for an export valid?

**Generated Answer:** A download URL for an export is valid for 24 hours after generation....

**Ground Truth:** Export download URLs are valid for 24 hours after generation....

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | The claim made in the answer is directly supported by the context, which states that 'All export URL |
| Context Precision | 0.33 | Matched: ['product-docs/data/exporting-data.md'] |
| Correctness | 1.00 | Missing: [] |

---

### Q020: What's the support response SLA on Pro?

**Generated Answer:** The support response SLA on the Pro plan is 8 hours for email and chat support....

**Ground Truth:** On Pro, the support response SLA is 8 hours....

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | The claim made in the answer is directly supported by the context, which states that the Pro plan in |
| Context Precision | 0.25 | Matched: ['product-docs/billing/plans.md'] |
| Correctness | 1.00 | Missing: [] |

---

### Q028: How do I export my data for compliance?

**Generated Answer:** To export your data for compliance, you can initiate a Data Subject Access Request (DSAR) export for GDPR compliance. This involves following the privacy procedure and compiling the necessary data within 7 days, which includes profile data, workspace memberships, workflows authored, and audit log en...

**Ground Truth:** Initiate exports via Settings → Data → Export, choosing data type (workflows, runs, audit log, users), date range, and format (JSON or CSV). Exports are generated asynchronously and a signed download URL valid for 24 hours is emailed when ready. For very large exports, chunk by date range to paralle...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 0.75 | The first three claims about initiating a DSAR export, the procedure, and the data included are dire |
| Context Precision | 0.42 | Matched: ['tickets/ticket-1349-export-stuck.html', 'product-docs/data/exporting-data.md'] |
| Correctness | 0.00 | Missing: ['where to start', 'formats supported', '24-hour URL expiry'] |

---

### Q036: Why does my Salesforce connection keep expiring?

**Generated Answer:** Your Salesforce connection may keep expiring due to the refresh token policy set to 'expire on first use,' which invalidates the refresh token each time it is used. This means the connection works until the access token expires, after which it cannot be refreshed. Changing the refresh token policy t...

**Ground Truth:** The most common cause is the Salesforce Connected App's refresh token policy being set to 'expire on first use,' which invalidates the refresh token every time Helix rotates the access token. Change the policy to 'refresh until revoked' in Salesforce. As a long-term best practice, use a dedicated se...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | All claims made in the answer are directly supported by the context provided. The context explains t |
| Context Precision | 0.47 | Matched: ['tickets/ticket-1267-integration-disconnect.html', 'product-docs/integrations/salesforce.md'] |
| Correctness | 0.67 | Missing: ['use a dedicated service account for Helix instead of a personal admin account'] |

---

### Q042: I'm seeing my workflow run time slowly creep up over the last two weeks even though I haven't changed anything. What should I look at?

**Generated Answer:** You should examine the specific steps in your workflow to identify any that may be taking longer to execute, particularly focusing on any queries or data processing steps. It's also helpful to check if the size of the data being processed has increased, as this can significantly impact run times. If...

**Ground Truth:** Workflow runtime drift is rarely platform-side; it's usually upstream data growth. Check: (1) is the data volume your workflow processes growing day-over-day? (2) is one specific step disproportionately slowing — for example, a Salesforce SOQL query whose match set grew because of an upstream backfi...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 0.67 | The first two claims are supported by the context, which discusses the slowdown in workflow executio |
| Context Precision | 0.33 | Matched: ['tickets/ticket-1402-slow-execution.html'] |
| Correctness | 0.50 | Missing: ['Diagnosis focuses on customer-side data growth, not platform issues', 'Mention of SOQL backfill pattern'] |

---

### Q043: Our auditor is asking for 18 months of run history. How do we get that?

**Generated Answer:** To obtain 18 months of run history, you will need to upgrade to the Enterprise plan, which offers data retention for 365 days. Alternatively, you can regularly export your run data to your own storage to maintain a longer history. Currently, on the Pro plan, run logs are only retained for 90 days an...

**Ground Truth:** Out of the box this isn't possible — Pro retains run logs for 90 days and Enterprise for 365 days. After retention expires, data is hard-deleted including from backups within 35 days, and is unrecoverable. Two paths forward: (1) upgrade to Enterprise to extend retention to 365 days going forward, bu...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 0.67 | The first claim about needing to upgrade to the Enterprise plan for 18 months of run history is supp |
| Context Precision | 0.25 | Matched: ['tickets/ticket-1378-missing-data-in-export.html'] |
| Correctness | 0.83 | Missing: ['Data is hard-deleted after retention expires and is unrecoverable', 'Scheduled export job to push run data to your own storage is a solution', 'Retroactive recovery of already-deleted data is not possible'] |

---

### Q044: We're getting paged at 3am because production is failing on 401s but the API key wasn't rotated. What's the standard runbook?

**Generated Answer:** The standard runbook for handling 401 errors involves checking the audit log to see if the API key was deleted. If the key was deleted, the customer needs to generate a new key, as deleted keys cannot be restored. Additionally, it's recommended to set up scoped keys and restrict deletion permissions...

**Ground Truth:** If a key is returning 401 without rotation, check: (1) was the key deleted? Audit log shows deletions with timestamp and actor; deleted keys cannot be restored. (2) was the key's scopes narrowed? A scope reduction can cause 403 (not 401) but worth checking. (3) is auth-service itself degraded? Check...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | All claims made in the answer are directly supported by the context provided. The context discusses  |
| Context Precision | 0.12 | Matched: ['tickets/ticket-1189-401-with-valid-key.html'] |
| Correctness | 0.83 | Missing: ['check if the auth-service is degraded'] |

---

### Q046: Customer says they were charged for an overage but they're sure they were under their limit. How do we investigate?

**Generated Answer:** To investigate the overage charge, first check the customer's usage history to confirm the number of runs they executed during the billing period. Compare this with the included runs in their plan to determine if they exceeded the limit. Additionally, review any automated usage alerts that may have ...

**Ground Truth:** Pull their invoice and verify the line items: base $299/mo plus overage at $0.01 per run beyond 10,000. Check usage history in Settings → Billing → Usage to see actual run counts and identify the top contributing workflows. If the customer was indeed over, walk through which workflows drove it — com...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | All claims made in the answer are supported by the context. The context provides information about c |
| Context Precision | 0.25 | Matched: ['tickets/ticket-1301-unexpected-charge.html'] |
| Correctness | 0.43 | Missing: ['Verify the invoice and line items: base $299/mo plus overage at $0.01 per run beyond 10,000', 'Identify the top contributing workflows', 'Common pattern is duplicate webhook subscriptions causing one workflow to fire many times more than expected', 'Confirm they received the standard 80%/100%/125% usage alert emails', 'For first-time overages, a goodwill credit (typically 50%) can be offered after CSM judgment', "Document in the customer's record per refund policy"] |

---

### Q050: A customer is escalating because they hit a P0-level outage on our side but haven't seen any communication from us. What's our obligation?

**Generated Answer:** For a P0 incident lasting longer than 30 minutes, you are obligated to send an email update to all paying customers using a pre-approved template. Additionally, the status page must be updated every 15 minutes until the incident is resolved. Ensure that CS leadership approves the communication befor...

**Ground Truth:** For P0 incidents (>5% login failures, >10% workflow run failure rate, data loss, security breach, >5% API 5xx), Helix has explicit communication obligations. Within 5 minutes of declaration the incident commander pages on-call and creates an incident channel. Status page at https://status.helix.io i...

| Metric | Score | Details |
|--------|-------|--------|
| Faithfulness | 1.00 | All claims made in the answer are directly supported by the context provided. The context specifies  |
| Context Precision | 0.50 | Matched: ['runbooks/incident-response/p0-incident-response.pdf'] |
| Correctness | 0.38 | Missing: ['P0 incidents definition', '5 minutes obligation for incident commander to page on-call and create incident channel', '10 minutes obligation to update status page after declaration', '30 minutes threshold for email update to all paying customers', 'pre-approved template for email updates', 'SLA-tier customers may be owed breach credits', "document missing communication in customer's record"] |

---


---

## Future Improvements

**Answer Relevance:** Current implementation uses direct LLM judgment. Could be improved with RAGAS-style approach:
1. Generate hypothetical questions the answer would address
2. Compute semantic similarity between generated and original questions
3. Average similarity scores

This would make the metric more robust and less dependent on LLM judgment variability.
