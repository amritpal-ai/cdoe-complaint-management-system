# Phase 0: no routes yet — this blueprint is registered so the app structure
# and url_prefix are in place, but is intentionally empty until Phase 6.
#
# Planned endpoint:
#   POST /email-sync/  -> triggers email_service.sync_emails()
#                          (same function the APScheduler job calls every
#                          SYNC_INTERVAL_MINUTES)
