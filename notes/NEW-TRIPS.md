# Brief: add new trip options

Read BRIEF.md (family, dates, photo method, style) and SCHEMA.md (JSON format) in this folder first, then PRICE-CHECK.md
(how to price flights and lodging realistically). Additional rules decided since:

- Family: Mom, Dad, Emily, Jennifer (4 adults). Dates: depart Sat Dec 12 2026, return Fri Dec 18 2026. 7-day itinerary,
  Day 1 = Dec 12 arrival day, Day 7 = Dec 18 fly home.
- FLIGHTS, balance rule: use the nonstop in regular economy (Main Cabin, not Basic) from PHL, JFK, EWR or LGA when one
  operates in December 2026 and costs no more than about $250 per person over a good 1-stop; otherwise use the 1-stop and
  mention the nonstop and its price in flightsBasis. Verify the nonstop actually runs in December 2026.
- LODGING: whole rental with 2 real bedrooms (Mom and Dad; Emily and Jennifer share), all-in incl. cleaning, service fees and
  taxes, December rates, split 4 ways. Two hotel rooms if cheaper or rentals are restricted. National park trips: lodges or
  rentals near the park, say which.
- costPP: flights, lodging (per person), foodFun: 0 (the family removed food and fun from the site), and the basis/verified fields.
- Add these extra fields per destination: "fly": "e.g. 6h nonstop" or "8h, 1 stop"; flight.from = departure airport;
  for road trips, say in getAround which rental car (full-size SUV for 4 adults + bags) and roughly the driving times.
- National parks: check December conditions and closures for 2026 (e.g. Yosemite Tioga Road and Glacier Point Road closed in
  winter, chains requirements, Death Valley weather, Grand Canyon North Rim closed). Be honest in cons.
- Every itinerary day needs a real Wikimedia Commons photo; 3 heroPhotos. Avoid NC licenses.
- "region" must be one of: "US", "Canada", "Europe", "Asia", "Caribbean", "Latin America".
- No em dashes anywhere.
Output: a JSON array (valid JSON) of the destinations in your batch to the file named in your task. Reply with a short
table: id, flights pp, lodging pp, fly, and anything unverified.
