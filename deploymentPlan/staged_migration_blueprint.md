# EvalBot Staged Migration Blueprint

Date: 2026-03-30

## Scope
This blueprint defines a staged path from your current single-run synchronous setup to parallel multi-workflow execution, with exact cutover criteria and rollback checks.

Current baseline:
- Host: DigitalOcean droplet (500 MB RAM, 10 GB disk)
- Execution mode: single workflow run at a time (synchronous)
- Workload: CLI pipeline (`main.py generate`)

---

## Stage A — Single-Run Hardening (Now)

### Goal
Run one workflow reliably and cheaply, with guardrails for memory, disk, and recovery.

### Target architecture
- 1 VM only (current droplet)
- `systemd` service + timer for scheduled execution
- `flock` lockfile to enforce non-overlap
- local quota gate to enforce agent-call ceilings before each run
- Local SQLite + local output directory
- Daily log rotation + nightly backup archives

### Implementation checklist
1. Create service account (`evalbot`) and app paths under `/opt/evalbot`.
2. Add 1 GB swap file and set swappiness to 25.
3. Deploy code and Python venv.
4. Store runtime secrets in `/opt/evalbot/shared/.env` (`chmod 600`).
5. Use `run_generate.sh` with:
   - `set -euo pipefail`
   - sourced venv and `.env`
   - `flock -n /tmp/evalbot.lock` wrapper
6. Configure `evalbot-generate.service` (`Type=oneshot`).
7. Configure `evalbot-generate.timer` for back-to-back execution.
   - Use `OnUnitInactiveSec=10s` so the next run starts shortly after the previous run finishes.
   - Keep `Persistent=true` and `flock` lock protection.
8. Add a quota check step before execution in `run_generate.sh`:
   - hard limits: max 1000 agent calls per rolling 5 hours, and max 15000 agent calls per rolling 7 days
   - if either limit would be exceeded, skip execution and exit 0 (timer will retry on next cycle)
9. Persist quota events in a local lightweight ledger file (for example `/opt/evalbot/shared/agent_calls.log`) where each line contains:
   - unix_timestamp,agent_calls_for_run
10. Keep a small helper script (for example `quota_gate.py`) that:
   - prunes old ledger rows outside 7 days
   - computes rolling sums for last 5h and last 7d
   - decides whether the next run is allowed
   - appends the run's call count after success
11. Keep nightly backup coverage for quota ledger state too.
12. Configure `/etc/logrotate.d/evalbot` (daily, 7 files, compressed, `maxsize 20M`).
13. Configure nightly backup job for:
   - SQLite `.backup`
   - `output/` snapshot
   - quota ledger snapshot
   - compressed tar archive with retention (keep last 7-14)
14. Add weekly cleanup for old `output/generated_*` folders (e.g., older than 14 days).

### Capacity limits for Stage A
- Concurrency: exactly 1 run
- Frequency: continuous, back-to-back single-run execution
- Rate ceilings: max 1000 agent calls / 5h and max 15000 agent calls / 7d
- Max recommended round profile: small/medium single batches only

### Stage A timer profile (default)
Use this timer for near-continuous execution without overlap:

```ini
[Timer]
OnBootSec=30s
OnUnitInactiveSec=10s
Persistent=true
Unit=evalbot-generate.service
```

### Stage A quota gate (required)
Evaluate both windows before each run:

1. Rolling 5-hour window:
   - allow only if `calls_5h + expected_calls_next_run <= 1000`
2. Rolling 7-day window:
   - allow only if `calls_7d + expected_calls_next_run <= 15000`

Recommended conservative default:
- set `expected_calls_next_run=8` (one call per agent)
- if your retries/reruns are frequent, raise this estimate (for example 10-12)

If a limit is hit:
1. skip the run
2. log the reason and current window totals
3. let the timer retry at the next `OnUnitInactiveSec` cycle

### Stage A success criteria (must hold for 7 consecutive days)
1. Timer runs complete without overlap.
2. No OOM kills (`dmesg` / kernel logs clear).
3. Disk free stays above 30%.
4. Quota gate never permits a run that would breach 5h/7d limits.
5. Backup archive generated nightly.
6. P95 run duration within expected bounds (stable trend, no runaway increase).

### Cutover gate to Stage B
Move to Stage B if **any** of these are true:
1. You need >1 workflow at a time.
2. You need higher run frequency than Stage A can safely handle.
3. Swap usage remains high after most runs (persistent memory pressure).
4. You need better failure isolation than one-process execution.

### Rollback plan (Stage A)
- N/A for architecture rollback (this is baseline).
- If unstable, increase `OnUnitInactiveSec` and reduce rounds immediately.
- If quota behavior is noisy, increase `expected_calls_next_run` so gate is more conservative.

---

## Stage B — Limited Parallelism (2 Workers)

### Goal
Safely run limited concurrency (2 parallel workflows) with queue-based control.

### Target architecture
- Upgraded VM: at least 2 GB RAM, 25+ GB disk
- Queue layer: Redis
- Worker process manager: `systemd` (2 worker services)
- Producer/API trigger still simple (CLI or scheduler)
- SQLite still possible for short term, but monitor lock contention

### Implementation checklist
1. Resize droplet to >=2 GB RAM.
2. Keep swap, but reduce reliance (performance should primarily be RAM-backed).
3. Install Redis (local or managed).
4. Introduce queue contracts:
   - Job payload schema (startup input, config, priority)
   - Job status lifecycle (`queued`, `running`, `succeeded`, `failed`)
5. Split execution into:
   - producer (`enqueue` job)
   - worker (`consume` and run pipeline)
6. Deploy 2 worker services:
   - `evalbot-worker@1.service`
   - `evalbot-worker@2.service`
7. Set max concurrent jobs = 2 globally.
8. Add retry policy for transient network errors:
   - exponential backoff
   - capped retries
9. Add idempotency key per job to prevent duplicate processing.
10. Move long-term logs to centralized sink if possible.

### SQLite note for Stage B
If SQLite write locks appear under parallelism, schedule immediate migration to Postgres (Stage C data-plane) without waiting for full Stage C.

### Stage B success criteria (must hold for 14 consecutive days)
1. Queue latency remains acceptable under normal load.
2. Worker crash rate is low and auto-recovery works.
3. No persistent DB lock contention affecting throughput.
4. Retries recover transient provider/network failures without manual intervention.
5. Disk growth remains controlled.

### Cutover gate to Stage C
Move to Stage C if **any** of these are true:
1. You need >2 parallel workflows.
2. You need stronger data durability/audit requirements.
3. SQLite contention or local disk constraints become operational risk.
4. You need clearer multi-tenant isolation or horizontal scaling.

### Rollback plan (Stage B)
1. Set worker count from 2 to 1.
2. Pause producer enqueue path.
3. Drain queue and resume Stage A timer-only execution.

---

## Stage C — Fully Queued Multi-Workflow Execution

### Goal
Operate scalable, resilient multi-workflow processing with managed persistence.

### Target architecture
- Compute: larger VM pool or managed job runner
- Queue: Redis (or managed queue)
- Database: Postgres (managed preferred)
- Artifact storage: S3-compatible object storage
- Observability: centralized logs + metrics + alerts
- Worker autoscaling based on queue depth and processing latency

### Implementation checklist
1. Migrate SQLite -> Postgres:
   - schema migration scripts
   - one-time data copy
   - dual-write or maintenance-window cutover
2. Move `output/` artifacts to object storage:
   - deterministic object keys per run/job
   - lifecycle retention policies
3. Implement robust job orchestration:
   - dead-letter queue (DLQ)
   - poison-message handling
   - per-job timeout and cancellation controls
4. Add distributed locking/idempotency safeguards.
5. Add autoscaling policy:
   - scale out by queue depth and oldest-message age
   - scale in with cooldown
6. Add SLO dashboards:
   - success rate
   - p95/p99 completion time
   - retry rate
   - provider error distribution
7. Add alerts:
   - queue backlog threshold
   - failure spikes
   - storage/database capacity thresholds

### Stage C success criteria
1. Parallel workloads process without queue starvation.
2. Reruns/retries are deterministic and auditable.
3. Artifact and DB durability meets recovery targets.
4. Horizontal scaling improves throughput linearly within expected limits.

### Rollback plan (Stage C)
1. Freeze autoscaling (set fixed low worker count).
2. Route new job intake to maintenance mode.
3. Revert workers to prior stable release.
4. Keep Postgres as source of truth; do not roll back to SQLite unless full outage protocol requires it.

---

## Exact Cutover Checklist (Operational)

Use this at each stage boundary.

1. Pre-cutover
   - Confirm backup is green for at least 3 recent cycles.
   - Confirm release tag exists and rollback artifact is prepared.
   - Confirm runbook is updated and tested.

2. Cutover
   - Apply infra changes (size, services, dependencies).
   - Deploy app with migration flags disabled by default.
   - Enable new execution path for a small canary percentage (or single job class).

3. Validation
   - Compare success/failure rates old vs new path.
   - Verify outputs are complete and schema-valid.
   - Verify runtime/cost are within budget envelope.

4. Commit
   - Shift all traffic/jobs to new path.
   - Disable deprecated path after observation window.

5. Rollback trigger
   - If failure rate or latency breaches threshold for two consecutive windows, roll back immediately.

---

## Suggested Thresholds You Can Start With

- Stage A -> B trigger:
  - average CPU > 75% for 3 days, or
  - memory pressure with sustained swap-in activity, or
  - requirement for concurrent workflows.

- Stage B -> C trigger:
  - queue wait p95 > 5 minutes during normal load, or
  - repeated DB lock/contention incidents, or
  - need for 3+ concurrent workflows and stronger durability.

---

## Immediate Next Actions (This Week)

1. Complete Stage A automation on the current droplet.
2. Run 7-day stability check with back-to-back single-run schedule.
3. Enable and validate quota gate behavior against 5h and 7d windows.
4. Record baseline metrics (run duration, memory peak, disk growth, calls_5h, calls_7d).
5. Pre-design queue payload schema now, even if Stage B is later.

This keeps today low-cost while making the future parallel transition straightforward.
