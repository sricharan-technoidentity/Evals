# MS-002: Parse compound durations like `"1h 30m"`

## Context
A frequently requested feature: configuration files often contain durations such as
`"1h 30m"` or `"2d 4h"`. Today `parse()` only understands a single number+unit pair and
returns `NaN` for these.

## Request
Teach `parse()` to accept a sequence of number+unit segments and return their sum.

## Acceptance criteria
1. Segments may be separated by whitespace or written back to back:
   - `parse('1h 30m') === 5_400_000`
   - `parse('1h30m') === 5_400_000`
   - `parse('2d 3h 4m 5s') === 183_845_000`
2. Long unit names work in compound form: `parse('1 hour 30 minutes') === 5_400_000`.
3. Each segment in a compound string must have an explicit unit. If any segment is
   invalid, the whole result is `NaN` (e.g. `parse('1h 30x')`, `parse('1h 30')`, `parse('h 30m')`).
4. Single-segment behaviour is unchanged, including unitless numbers (`parse('100') === 100`),
   negatives (`parse('-1h') === -3_600_000`) and decimals (`parse('1.5h')`).
5. The existing 100-character input limit and its error still apply.
6. The existing test, typecheck and lint commands still pass, including the 100% coverage threshold.

## Out of scope
- Changing `format()` to emit compound strings.
- Updating the `StringValue` template-literal type for compound strings.
- Negative signs on segments after the first.
