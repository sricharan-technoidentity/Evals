# PET-002: Owner search by last name should be case-insensitive

## Context
Front-desk staff type owner names in whatever case they like. Searching for `davis` on
**Find Owners** currently shows "has not been found", even though Betty Davis and
Harold Davis exist. Only `Davis` works.

## Request
Make the last-name search on `GET /owners?lastName=...` case-insensitive.

## Acceptance criteria
1. Searching `davis`, `DAVIS` or `Davis` returns the same owners list
   (Betty Davis and Harold Davis in the sample data).
2. A case-insensitive search that matches exactly one owner still redirects to that owner's
   details page (e.g. `franklin` → George Franklin).
3. Prefix ("starts with") matching, pagination and the "not found" behaviour are unchanged.
4. An empty search still lists all owners.
5. The build passes: existing tests, `spring-javaformat` validation and checkstyle.

## Out of scope
- Searching by first name or other fields.
- Database schema changes or new indexes.
