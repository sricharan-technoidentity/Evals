# MS-001: Support microsecond units in `parse()`

## Context
Users measuring high-resolution timings (e.g. from `performance.now()`) want to write
durations such as `"250us"` and have `ms` convert them to (fractional) milliseconds.
Today these strings return `NaN`.

## Request
Add microsecond units to the string parser.

## Acceptance criteria
1. `parse()` / `ms()` accept the units `us`, `microsecond` and `microseconds`, with or
   without a space between number and unit, case-insensitive like every other unit.
   - `parse('500us') === 0.5`
   - `parse('1 microsecond') === 0.001`
   - `parse('1.5US') === 0.0015`
2. The `StringValue` type accepts the new units, so `ms('250us')` type-checks.
3. All existing parsing and formatting behaviour is unchanged (e.g. `parse('1ms') === 1`,
   `parse('1m') === 60000`, `format()` output is not affected).
4. Unknown units still return `NaN` (e.g. `parse('1u')`).
5. The existing test, typecheck and lint commands still pass, including the 100% coverage threshold.

## Out of scope
- Formatting values below 1 ms as microseconds.
- Nanoseconds.
