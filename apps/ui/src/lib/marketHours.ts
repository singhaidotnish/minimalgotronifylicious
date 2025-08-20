// src/lib/marketHours.ts

/**
 * NSE/BSE regular session (IST):
 *   Open  : 09:15
 *   Close : 15:30
 * Days   : Monday (1) ... Friday (5)
 *
 * We compute everything in "minutes since midnight" for the target timezone,
 * then return absolute Dates by adding the computed delta to `now`.
 * No external libs, no fragile timezone math.
 */

const OPEN_MIN = 9 * 60 + 15;   // 09:15
const CLOSE_MIN = 15 * 60 + 30; // 15:30

type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6; // 0 = Sun ... 6 = Sat

/**
 * Return the weekday (0=Sun..6=Sat) for `now` in the given tz.
 */
function zonedWeekday(now: Date, tz: string): Weekday {
  // Use Intl to get the weekday name in that TZ and map to number
  const wd = new Intl.DateTimeFormat('en-GB', {
    weekday: 'short',
    timeZone: tz,
  }).format(now); // e.g., "Mon", "Tue", ...

  switch (wd) {
    case 'Sun': return 0;
    case 'Mon': return 1;
    case 'Tue': return 2;
    case 'Wed': return 3;
    case 'Thu': return 4;
    case 'Fri': return 5;
    case 'Sat': return 6;
    default:    return (now.getDay() as Weekday); // fallback
  }
}

/**
 * Return minutes since midnight for `now` in the given tz (0..1439).
 */
function zonedMinutesSinceMidnight(now: Date, tz: string): number {
  // 24h clock to avoid AM/PM parsing
  const parts = new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: tz,
  })
    .formatToParts(now)
    .reduce<Record<string, string>>((acc, p) => {
      if (p.type === 'hour' || p.type === 'minute') acc[p.type] = p.value;
      return acc;
    }, {});

  const h = Number(parts.hour ?? '0');
  const m = Number(parts.minute ?? '0');
  return h * 60 + m;
}

/**
 * Is it a trading weekday in the given tz? (Mon..Fri)
 * Note: does not include exchange holidays; extend if needed.
 */
function isTradingWeekday(now: Date, tz: string): boolean {
  const wd = zonedWeekday(now, tz);
  return wd >= 1 && wd <= 5;
}

/**
 * True if market is currently open in the given tz.
 * (Mon–Fri and within 09:15..15:30)
 */
export function isMarketOpen(now: Date = new Date(), tz = 'Asia/Kolkata'): boolean {
  if (!isTradingWeekday(now, tz)) return false;
  const min = zonedMinutesSinceMidnight(now, tz);
  return min >= OPEN_MIN && min < CLOSE_MIN;
}

/**
 * Returns a Date for the next "market boundary" from `now` in tz:
 *  - If currently open  → next boundary is today's close (15:30 IST)
 *  - If before open     → next boundary is today's open (09:15 IST)
 *  - If after close     → next boundary is next trading day's open
 *  - If weekend         → next boundary is next Monday open
 *
 * This function does not include exchange holidays; you can inject a holiday
 * predicate later if required (see TODO in code).
 */
export function nextMarketBoundary(now: Date = new Date(), tz = 'Asia/Kolkata'): Date {
  // Helper to add minutes to an absolute Date
  const addMinutes = (d: Date, mins: number) => new Date(d.getTime() + mins * 60_000);

  const wd = zonedWeekday(now, tz);
  const min = zonedMinutesSinceMidnight(now, tz);

  // If we're within session → boundary is today's close.
  if (isTradingWeekday(now, tz) && min >= OPEN_MIN && min < CLOSE_MIN) {
    const delta = CLOSE_MIN - min; // minutes until close
    return addMinutes(now, delta);
  }

  // If it's a trading day but BEFORE open → boundary is today's open.
  if (isTradingWeekday(now, tz) && min < OPEN_MIN) {
    const delta = OPEN_MIN - min;
    return addMinutes(now, delta);
  }

  // Otherwise: after close or weekend → find next trading day and return its open.
  let daysToAdd: number;
  switch (wd) {
    case 5: // Fri → next is Mon
      daysToAdd = 3;
      break;
    case 6: // Sat → next is Mon
      daysToAdd = 2;
      break;
    default:
      // Sun (0) → +1 day; Mon–Thu (1..4) when after close → +1 day
      daysToAdd = 1;
      break;
  }

  // Compute minutes until next day’s midnight in tz, then add OPEN_MIN.
  // We only need a delta, so we can avoid constructing a zoned Date.
  const minutesLeftToday = 24 * 60 - min;
  const fullDaysToSkip = daysToAdd - 1;
  const delta =
    // remainder of today (if any)
    minutesLeftToday +
    // whole days to skip
    fullDaysToSkip * 24 * 60 +
    // minutes to next day's open
    OPEN_MIN;

  // TODO (optional): inject holiday calendar
  // If that next day is an exchange holiday in tz, loop forward by +1 day (add 1440)
  // until a non-holiday weekday and adjust `delta` accordingly.

  return addMinutes(now, delta);
}
