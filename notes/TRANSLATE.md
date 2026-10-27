# Vietnamese translation brief

Translate the trip text in the given source JSON into natural, warm Vietnamese for a Vietnamese-American family
(the parents read Vietnamese best; Southern usage is fine: "Ba Mẹ" for Dad and Mom). Output a JSON file with exactly the
same keys and structure (same ids, same array lengths, same itinerary length and order). Translate every string value.

Rules:
- Keep proper names of places, hotels, restaurants, airlines and dishes recognizable: use the usual Vietnamese name if one
  exists (Paris, Luân Đôn may stay "London", Bắc Kinh for Beijing, Vạn Lý Trường Thành for the Great Wall), otherwise keep
  the original name. Keep airport codes (PHL, JFK), flight numbers, prices ($1,200) and dates numeric.
- Convert dates to Vietnamese style (Dec 12 -> 12/12, Nov 19 2026 -> 19/11/2026). Keep °F temperatures as written if any
  appear inside sentences (the page shows °C separately).
- Keep it short and plain, like the English. No em dashes.
- "name" for each trip: translate the country/city part naturally, e.g. "Paris, France" -> "Paris, Pháp".
- "_recs" (if present) maps trip id to a one-sentence reason: translate those too.
- Output must be valid JSON (UTF-8, not escaped). Validate with python3 -c "import json;json.load(open(PATH))".
