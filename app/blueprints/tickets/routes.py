# Phase 0: no routes yet — this blueprint is registered so the app structure
# and url_prefix are in place, but is intentionally empty until Phase 2+.
#
# Planned endpoints (added incrementally):
#   POST   /tickets/                     -> create_ticket (manual)      [Phase 2]
#   POST   /tickets/<id>/remarks         -> add_remark                 [Phase 3]
#   POST   /tickets/<id>/close           -> close_ticket                [Phase 3]
#   POST   /tickets/<id>/reopen          -> reopen_ticket                [Phase 3]
#   PATCH  /tickets/<id>/title           -> update_title                [Phase 4]
#   POST   /tickets/<id>/mark-duplicate  -> mark_duplicate               [Phase 5]
