# Research and safety notes

Upstream: https://github.com/lucasforster1108-boop/oracle-snatch (MIT). Original license retained.

## Safety changes
- Persist launch intent before OCI launch. Stop if a previous record exists.
- Record instance ID before IP lookup; never retry provisioning because IP lookup failed.
- Local shape and boot volume limits are not a billing guarantee.
- Keep minimum retry intervals and redact Telegram exception details.

## Recovery
Inspect snatched.json and the OCI Console after a pending or created record. Do not delete the record until the launch outcome and existing resources are reconciled. This guard is local to one working directory; it does not coordinate multiple hosts.

## Remaining research
- Verify current OCI free-tier rules, tenancy-wide compute/storage usage and home region. PAYG can incur charges.
- Implement explicit reconciliation, durable distributed locking, bounded jittered retry, Docker and service hardening.
- Test with mocked OCI responses before any live provisioning. No live credentials in CI.
