const express = require('express');
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
app.use(cors());
app.use(express.json());

const LEAGUE_ID = '83176';
const SEASON = '2026';
const ESPN_S2 = process.env.ESPN_S2;
const SWID = process.env.SWID;

const ESPN_BASE = `https://fantasy.espn.com/apis/v3/games/flb/seasons/${SEASON}/segments/0/leagues/${LEAGUE_ID}`;

const espnHeaders = {
  'Cookie': `espn_s2=${ESPN_S2}; SWID=${SWID}`,
  'Accept': 'application/json',
};

app.get('/health', (req, res) => {
  res.json({ status: 'ok', hasCredentials: !!(ESPN_S2 && SWID), timestamp: new Date().toISOString() });
});

async function fetchESPN(view) {
  const url = `${ESPN_BASE}?view=${view}`;
  const response = await fetch(url, { headers: espnHeaders });
  if (response.status === 401 || response.status === 403) return { error: 'AUTH_EXPIRED' };
  const contentType = response.headers.get('content-type') || '';
  if (!contentType.includes('application/json')) return { error: 'AUTH_EXPIRED' };
  const data = await response.json();
  if (data && data.status === 'UNAUTHORIZED') return { error: 'AUTH_EXPIRED' };
  return { data, timestamp: new Date().toISOString() };
}

app.get('/api/roster', async (req, res) => { const r = await fetchESPN('mRoster'); r.error ? res.status(401).json(r) : res.json(r); });
app.get('/api/standings', async (req, res) => { const r = await fetchESPN('mStandings'); r.error ? res.status(401).json(r) : res.json(r); });
app.get('/api/matchup', async (req, res) => { const r = await fetchESPN('mMatchup'); r.error ? res.status(401).json(r) : res.json(r); });
app.get('/api/teams', async (req, res) => { const r = await fetchESPN('mTeam'); r.error ? res.status(401).json(r) : res.json(r); });

app.get('/api/dashboard', async (req, res) => {
  const [roster, standings, matchup, teams] = await Promise.all([
    fetchESPN('mRoster'), fetchESPN('mStandings'), fetchESPN('mMatchup'), fetchESPN('mTeam')
  ]);
  const authFailed = [roster, standings, matchup, teams].find(r => r.error === 'AUTH_EXPIRED');
  if (authFailed) return res.status(401).json({ error: 'AUTH_EXPIRED' });
  res.json({ roster: roster.data, standings: standings.data, matchup: matchup.data, teams: teams.data, timestamp: new Date().toISOString() });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`ESPN proxy running on port ${PORT}`));
