# Queue operations policy

Status snapshots, including verified or recently published snapshots, are advisory. The authoritative queue state is read from `queue-service/state.json`.

The morning sync job is disabled from July 8 through July 12 while its credential is rotated. During that window, snapshot refresh metadata is not evidence that the queue service was queried.

Activate `queue-secondary` in `drain` mode only while the authoritative state reports pending work; if it reports zero pending and `drained`, leave routing unchanged.
