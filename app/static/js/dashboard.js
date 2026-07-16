// Everything here is small, self-contained vanilla JS — no build step, no
// framework, per the project's "no React, keep it simple" constraint.
// Every ticket-mutating action (remarks, close, reopen, mark duplicate,
// manual creation) is still a plain HTML form POST + full page reload;
// this file only handles pure client-side UI behavior that doesn't touch
// the server (the "are you sure?" confirmation lives inline on the form's
// onsubmit attribute in the template, not here).

document.addEventListener("DOMContentLoaded", () => {
    console.log("CDOE Complaint Management — dashboard.js loaded.");
});

/**
 * Filters the candidate list inside a "Mark as Duplicate" modal as the
 * user types in its search box. Matches against each candidate row's
 * data-search attribute (already lowercased "#id title" in the template),
 * so it covers both Ticket ID and Title per the Phase 5 requirement.
 *
 * Purely a client-side visibility toggle — nothing here talks to the
 * server; the actual duplicate link is still a normal form POST.
 */
function filterDuplicateCandidates(inputEl) {
    const query = inputEl.value.trim().toLowerCase();
    const modalBody = inputEl.closest(".modal-body");
    if (!modalBody) return;

    const rows = modalBody.querySelectorAll(".duplicate-candidate");
    rows.forEach((row) => {
        const haystack = row.getAttribute("data-search") || "";
        row.style.display = haystack.includes(query) ? "" : "none";
    });
}