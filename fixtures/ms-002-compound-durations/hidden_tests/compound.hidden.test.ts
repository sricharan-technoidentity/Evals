import { describe, expect, it } from '@jest/globals';
import { parse } from './index';

describe('[hidden] MS-002 compound durations', () => {
  it('sums whitespace-separated segments', () => {
    expect(parse('1h 30m')).toBe(5_400_000);
    expect(parse('2d 3h 4m 5s')).toBe(183_845_000);
  });

  it('sums back-to-back segments', () => {
    expect(parse('1h30m')).toBe(5_400_000);
    expect(parse('1m30s')).toBe(90_000);
  });

  it('supports long unit names', () => {
    expect(parse('1 hour 30 minutes')).toBe(5_400_000);
    expect(parse('1 day 1 hour')).toBe(90_000_000);
  });

  it('returns NaN when any segment is invalid', () => {
    expect(parse('1h 30x')).toBeNaN();
    expect(parse('1h 30')).toBeNaN();
    expect(parse('h 30m')).toBeNaN();
    expect(parse('1h 30m foo')).toBeNaN();
  });

  it('keeps single-segment behaviour', () => {
    expect(parse('100')).toBe(100);
    expect(parse('-1h')).toBe(-3_600_000);
    expect(parse('1.5h')).toBe(5_400_000);
    expect(parse('2 days')).toBe(172_800_000);
    expect(parse('foo')).toBeNaN();
  });

  it('keeps the input length limit', () => {
    expect(() => parse('1h '.repeat(40))).toThrow();
  });
});
