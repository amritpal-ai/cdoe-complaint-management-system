"""
Service layer — business logic lives here, kept separate from routes.py
so route handlers stay thin (parse request -> call service -> respond).

Phase 1 scope is data layer only, so this file is intentionally empty.
Starting Phase 2, functions such as create_ticket(), add_remark(),
close_ticket(), reopen_ticket(), and mark_duplicate() will be added here,
each responsible for writing its own TimelineEvent as part of the same
transaction that changes ticket state.
"""