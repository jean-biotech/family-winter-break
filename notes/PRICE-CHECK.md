# Price re-check brief

The family (Mom, Dad, Emily, Jennifer; 4 adults) found the first-pass prices too low (e.g. Quebec + Montreal had flights
$380 pp, but American actually shows ~$476 RT PHL-YUL for Dec 12-16 and Quebec City December rentals average $375-430/night).
Re-check EVERY destination's numbers in your batch with fresh web searches. Be realistic, not optimistic: when sources range,
use a typical/median fare for those exact dates, not the cheapest teaser. Today is Oct 27, 2026.

FLIGHTS (per person, round trip, economy Main Cabin, NOT Basic Economy): depart PHL or NYC on Sat Dec 12 or Sun Dec 13 2026,
return Fri Dec 18 (Asia: leave Dec 18 local, arrive Dec 18/19). Search aggregator route pages (Expedia, Travelocity, Orbitz,
Kayak, Cheapflights, aa.com route pages) that show dated December 2026 fares; quote the actual fare and date you saw.
Include any internal legs (inter-island, domestic flight, open jaw). Main Cabin is usually ~$60 to $120 RT more than the
basic fares aggregators show; add that if the quote is basic economy.

LODGING (per person = total / 4): whole-home rental with at least 2 real bedrooms (Mom and Dad in one, Emily and Jennifer
sharing the other; sofa beds don't count), in the neighborhood the itinerary uses, for mid-December 2026, ALL-IN nightly
cost including cleaning fee, service fee and taxes (Airbnb/Vrbo all-in usually runs 20-30% above the listed nightly rate).
If two hotel rooms are cheaper (or rentals are restricted, e.g. Singapore), use that. Use December averages from
HomeToGo/Kayak/Airbnb market data/AirDNA style sources and real listings; note the source. Count the real number of nights
in the itinerary (usually 6).

FOOD & FUN (per person for the week): sanity-check it includes meals at a realistic level for that place, the itinerary's
paid activities, local transport, and a 1/4 share of any rental car (full-size SUV or minivan for 4 adults + luggage) incl. gas
and parking. Fix it if it looks low.

Mark flightsVerified true ONLY if you saw a real dated December 2026 fare for this route; lodgingVerified true only if you saw
December data for that area. Never use em dashes.

OUTPUT: write notes/price-<batch>.json as an object keyed by destination id:
{ "<id>": { "flights": int, "flightsBasis": "short: fare seen, source, date", "flightsVerified": bool,
            "lodging": int, "lodgingBasis": "short: $X/night all-in x N nights / 4, source", "lodgingVerified": bool,
            "foodFun": int, "foodFunBasis": "short", "sources": [{"label": "...", "url": "..."}] } }
Then reply with a table: id, old -> new for flights, lodging, foodFun.
