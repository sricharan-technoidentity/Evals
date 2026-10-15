# PET-001: Make `PetValidator` the single place that rejects future birth dates

## Context
The rule "a pet's birth date cannot be in the future" is currently duplicated inside
`PetController.processCreationForm` and `PetController.processUpdateForm`. `PetValidator`,
which is already registered for the `pet` model attribute, only checks that a birth date is
present. Anything that validates a `Pet` without going through the controller (for example a
future REST endpoint or a batch import) silently accepts future dates.

## Request
Move the future-birth-date rule into `PetValidator` and remove the duplicated checks from
`PetController`.

## Acceptance criteria
1. `PetValidator.validate()` rejects a pet whose birth date is after today with a field error on
   `birthDate` using the existing error code `typeMismatch.birthDate`
   (already defined in `messages.properties`).
2. A birth date of today or in the past is accepted by the validator.
3. A missing birth date is still rejected with the existing `required` code.
4. `PetController` no longer contains its own future-birth-date check (single source of truth).
5. Behaviour seen by users is unchanged: submitting the create or edit pet form with a future
   date still re-renders the form with the `typeMismatch.birthDate` error on `birthDate`.
6. The build passes: existing tests, `spring-javaformat` validation and checkstyle.

## Out of scope
- UI or message text changes.
- Other validation rules.
