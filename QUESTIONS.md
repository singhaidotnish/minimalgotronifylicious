#1)
Notes (future‑you, CI/CD brain):

This version doesn’t include exchange holidays. If you later add a holiday list, inject a predicate isHoliday(dateInTZ) and advance the boundary day(s) inside nextMarketBoundary.

Unit tests to lock behavior:

“Sunday noon IST → !isMarketOpen() and boundary is Monday 09:15”

“Friday 16:00 IST → boundary is Monday 09:15”

“Wednesday 09:00 IST → boundary is today 09:15”

“Wednesday 14:00 IST → boundary is today 15:30”

If you want, I can add a tiny holiday hook you can pass in (so you don’t hardcode calendars), and a quick Jest test file scaffold.





#2)

Right now in your SettingsProvider you have this:


#3)

Kill implicit anys:

#4)

what is difference in reduce here

export function evaluateGroup(group: ConditionGroup, livePrices: Record<string, number>): boolean {
  if (group.logic === 'AND') {
    return group.conditions.every((cond: ConditionNode) =>
      cond.type === 'group'
        ? evaluateGroup(cond, livePrices)
        : evaluateCondition(cond, livePrices)
    );
  } else { // 'OR'
    return group.conditions.some((cond: ConditionNode) =>
      cond.type === 'group'
        ? evaluateGroup(cond, livePrices)
        : evaluateCondition(cond, livePrices)
    );
  }
}

If you really want to use reduce:

export function evaluateGroup(group: ConditionGroup, livePrices: Record<string, number>): boolean {
  return group.conditions.reduce<boolean>((acc, cond) => {
    const result = cond.type === 'group'
      ? evaluateGroup(cond, livePrices)
      : evaluateCondition(cond, livePrices);

    return group.logic === 'AND' ? (acc && result) : (acc || result);
  }, group.logic === 'AND'); // seed true for AND, false for OR
}


#5)

what does mapping options means here

// …when mapping options
{p.options!.map((o: { label: string; value: string }) => (
  <option key={o.value} value={o.value}>{o.label}</option>
))}


