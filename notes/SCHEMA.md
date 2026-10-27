# Research note format (one JSON file per batch: notes/<batch>.json = array of destinations)

{
  "id": "paris",                       // short slug
  "name": "Paris, France",
  "region": "Europe" | "US" | "Canada" | "Asia" | "Caribbean",
  "passport": true|false,
  "warm": true|false,                  // daytime highs >= 70F
  "tagline": "max 8 words",
  "whyParents": "one sentence, max 20 words",
  "costPP": {                          // USD per person, group of 4 adults, Dec 12/13 -> Dec 18/19 2026
     "flights": 650, "flightsBasis": "how you got it (fare seen on X on date, or typical range)", "flightsVerified": true|false,
     "lodging": 300, "lodgingBasis": "2BR apartment ~$X/night total split 4 ways, or 2 hotel rooms", "lodgingVerified": true|false,
     "foodFun": 450, "foodFunBasis": "per-day estimate"
  },
  "flight": {
     "from": "PHL" | "JFK" | "EWR" | "LGA",
     "airline": "American",
     "routing": "PHL-CDG nonstop (AA, daily in Dec)" ,
     "aaMetal": true|false,            // flown by American itself
     "hours": "7h 15m",
     "notes": "short; alt option e.g. Air France via Capital One transfer partner Flying Blue"
  },
  "weather": { "highF": 46, "lowF": 37, "daylight": "8h 20m", "precip": "rain ~10 days/month, snow rare" },
  "stay": "neighborhood + 4-6 words why",
  "getAround": "max 25 words: trains/metro/car (car size for 4 adults + luggage)",
  "entry": "max 20 words for US passport holders, incl ETIAS/EES status where relevant",
  "events": ["things actually happening Dec 12-18 2026, with verified dates, e.g. Christmas markets (exact 2026 open/close dates), festivals, closures"],
  "pros": ["3 short bullets, max 10 words each"],
  "cons": ["3 short bullets, max 10 words each"],
  "itinerary": [                       // 7 days: Day 1 = arrival day ... Day 7 = fly home. Keep each plan <= 20 words.
     { "day": 1, "title": "Arrive + Seine stroll", "plan": "...", "eat": "one specific restaurant or dish", 
       "photo": { "file": "Exact_Commons_File_Name.jpg", "author": "...", "license": "CC BY-SA 4.0", "caption": "3-6 words" } }
  ],
  "heroPhotos": [ { "file": "...", "author": "...", "license": "...", "caption": "..." } ],   // 2-3 iconic shots
  "sources": [ { "label": "short", "url": "https://..." } ],
  "unverified": ["any claim you could not verify"]
}
