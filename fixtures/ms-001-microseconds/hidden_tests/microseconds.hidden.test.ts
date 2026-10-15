import { describe, expect, it } from '@jest/globals';
import { ms, parse } from './index';

describe('[hidden] MS-001 microseconds', () => {
  it('parses "us"', () => {
    expect(parse('500us')).toBeCloseTo(0.5, 10);
    expect(parse('500 us')).toBeCloseTo(0.5, 10);
  });

  it('parses "microsecond" and "microseconds"', () => {
    expect(parse('1 microsecond')).toBeCloseTo(0.001, 10);
    expect(parse('2microseconds')).toBeCloseTo(0.002, 10);
  });

  it('is case-insensitive', () => {
    expect(parse('1.5US')).toBeCloseTo(0.0015, 10);
    expect(parse('3 Microseconds')).toBeCloseTo(0.003, 10);
  });

  it('type-checks through ms() and StringValue', () => {
    // The acceptance command also runs `tsc --noEmit` over this file, so an
    // un-widened StringValue fails acceptance even though jest (isolatedModules) passes.
    expect(ms('250us')).toBeCloseTo(0.25, 10);
    expect(ms('4 microseconds')).toBeCloseTo(0.004, 10);
  });

  it('leaves existing units unchanged', () => {
    expect(parse('1ms')).toBe(1);
    expect(parse('1m')).toBe(60000);
    expect(parse('2 mins')).toBe(120000);
    expect(parse('1s')).toBe(1000);
    expect(ms(1500)).toBe('2s');
  });

  it('still returns NaN for unknown units', () => {
    expect(parse('1u')).toBeNaN();
    expect(parse('1 usec')).toBeNaN();
  });
});
