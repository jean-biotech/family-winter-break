// Family vote API (Vercel serverless function).
// Stores each person's top 5 in Upstash Redis (Vercel Storage > Upstash, free tier).
// One vote per person; once saved it cannot be changed (clear the key in Upstash to reset).
// Privacy rule: never return anyone's individual ranking. Before everyone has voted,
// only "who has voted" is returned; after all 4 have voted, only the combined points.

const VOTERS = ["mom", "dad", "emily", "jennifer"];
const KEY = "winter2026:votes";
const POINTS = [5, 4, 3, 2, 1];

const REDIS_URL = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const REDIS_TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;

async function redis(command) {
  const r = await fetch(REDIS_URL, {
    method: "POST",
    headers: { Authorization: `Bearer ${REDIS_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify(command),
  });
  const out = await r.json();
  if (!r.ok || out.error) throw new Error(out.error || `redis ${r.status}`);
  return out.result;
}

async function summary() {
  // HGETALL returns a flat [field, value, field, value, ...] list
  const flat = (await redis(["HGETALL", KEY])) || [];
  const votes = {};
  for (let i = 0; i < flat.length; i += 2) votes[flat[i]] = JSON.parse(flat[i + 1]);
  const voted = Object.fromEntries(VOTERS.map(v => [v, Boolean(votes[v])]));
  const complete = VOTERS.every(v => voted[v]);
  let results = null;
  if (complete) {
    const tally = {};
    for (const v of VOTERS) {
      votes[v].forEach((id, i) => {
        tally[id] = tally[id] || { id, points: 0, picks: 0, firsts: 0 };
        tally[id].points += POINTS[i];
        tally[id].picks += 1;
        if (i === 0) tally[id].firsts += 1;
      });
    }
    results = Object.values(tally).sort((a, b) => b.points - a.points || b.firsts - a.firsts || b.picks - a.picks);
  }
  return { voted, complete, results };
}

function readBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  try { return JSON.parse(req.body || "{}"); } catch { return {}; }
}

module.exports = async (req, res) => {
  // Allow the GitHub Pages copy of the site to call this API too
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Cache-Control", "no-store");
  if (req.method === "OPTIONS") return res.status(204).end();

  if (!REDIS_URL || !REDIS_TOKEN) {
    return res.status(503).json({ error: "Vote storage is not connected yet. Add an Upstash Redis database to this Vercel project." });
  }

  try {
    if (req.method === "POST") {
      const { voter, ranking } = readBody(req);
      if (!VOTERS.includes(voter)) return res.status(400).json({ error: "Pick Mom, Dad, Emily or Jennifer first." });
      const valid = Array.isArray(ranking) && ranking.length === 5 &&
        new Set(ranking).size === 5 && ranking.every(id => typeof id === "string" && /^[a-z0-9-]{1,40}$/.test(id));
      if (!valid) return res.status(400).json({ error: "A vote needs 5 different trips." });
      // one vote per person, final: HSETNX only writes if this person has not voted yet,
      // so a second device (or anyone else) cannot vote again as them
      const added = await redis(["HSETNX", KEY, voter, JSON.stringify(ranking)]);
      if (!added) return res.status(409).json({ error: "already_voted", ...(await summary()) });
    } else if (req.method !== "GET") {
      return res.status(405).json({ error: "Use GET or POST." });
    }
    return res.status(200).json(await summary());
  } catch (e) {
    return res.status(500).json({ error: "Could not reach vote storage. Try again in a minute." });
  }
};
