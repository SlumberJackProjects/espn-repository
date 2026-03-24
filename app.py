from flask import Flask, jsonify
from flask_cors import CORS
from espn_api.baseball import League
import os
import traceback

app = Flask(**name**)
CORS(app)

LEAGUE_ID = 83176
YEAR = 2026
ESPN_S2 = os.environ.get(‘ESPN_S2’)
SWID = os.environ.get(‘SWID’)

def get_league():
return League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

@app.route(’/health’)
def health():
return jsonify({
‘status’: ‘ok’,
‘hasCredentials’: bool(ESPN_S2 and SWID),
})

@app.route(’/api/teams’)
def teams():
try:
league = get_league()
teams_data = []
for team in league.teams:
teams_data.append({
‘id’: team.team_id,
‘name’: team.team_name,
‘owner’: team.owner,
‘wins’: team.wins,
‘losses’: team.losses,
‘roster’: [
{
‘name’: p.name,
‘position’: p.position,
‘proTeam’: p.proTeam,
‘injuryStatus’: p.injuryStatus,
}
for p in team.roster
]
})
return jsonify({‘teams’: teams_data})
except Exception as e:
tb = traceback.format_exc()
if ‘Authentication’ in str(e) or ‘401’ in str(e) or ‘private’ in str(e).lower():
return jsonify({‘error’: ‘AUTH_EXPIRED’}), 401
return jsonify({‘error’: str(e), ‘trace’: tb}), 500

@app.route(’/api/standings’)
def standings():
try:
league = get_league()
standings_data = []
for team in sorted(league.teams, key=lambda t: t.wins, reverse=True):
standings_data.append({
‘name’: team.team_name,
‘owner’: team.owner,
‘wins’: team.wins,
‘losses’: team.losses,
‘ties’: team.ties,
})
return jsonify({‘standings’: standings_data})
except Exception as e:
if ‘Authentication’ in str(e) or ‘401’ in str(e) or ‘private’ in str(e).lower():
return jsonify({‘error’: ‘AUTH_EXPIRED’}), 401
return jsonify({‘error’: str(e)}), 500

@app.route(’/api/matchup’)
def matchup():
try:
league = get_league()
week = league.currentMatchupPeriod
box_scores = league.box_scores(week)
matchups = []
for match in box_scores:
matchups.append({
‘week’: week,
‘home’: {
‘team’: match.home_team.team_name if match.home_team else ‘BYE’,
‘score’: match.home_score,
},
‘away’: {
‘team’: match.away_team.team_name if match.away_team else ‘BYE’,
‘score’: match.away_score,
}
})
return jsonify({‘matchups’: matchups, ‘week’: week})
except Exception as e:
if ‘Authentication’ in str(e) or ‘401’ in str(e) or ‘private’ in str(e).lower():
return jsonify({‘error’: ‘AUTH_EXPIRED’}), 401
return jsonify({‘error’: str(e)}), 500

@app.route(’/api/roster/<int:team_id>’)
def roster(team_id):
try:
league = get_league()
team = next((t for t in league.teams if t.team_id == team_id), None)
if not team:
return jsonify({‘error’: ‘Team not found’}), 404
roster_data = [
{
‘name’: p.name,
‘position’: p.position,
‘proTeam’: p.proTeam,
‘injuryStatus’: p.injuryStatus,
}
for p in team.roster
]
return jsonify({‘team’: team.team_name, ‘roster’: roster_data})
except Exception as e:
if ‘Authentication’ in str(e) or ‘401’ in str(e) or ‘private’ in str(e).lower():
return jsonify({‘error’: ‘AUTH_EXPIRED’}), 401
return jsonify({‘error’: str(e)}), 500

@app.route(’/api/dashboard’)
def dashboard():
try:
league = get_league()
week = league.currentMatchupPeriod

```
    # Teams + rosters
    teams_data = []
    my_team = None
    for team in league.teams:
        t = {
            'id': team.team_id,
            'name': team.team_name,
            'owner': team.owner,
            'wins': team.wins,
            'losses': team.losses,
            'roster': [
                {
                    'name': p.name,
                    'position': p.position,
                    'proTeam': p.proTeam,
                    'injuryStatus': p.injuryStatus,
                }
                for p in team.roster
            ]
        }
        teams_data.append(t)
        if 'slumber' in team.team_name.lower() or 'matt' in team.owner.lower():
            my_team = t

    # Matchups
    box_scores = league.box_scores(week)
    matchups = []
    for match in box_scores:
        matchups.append({
            'home': match.home_team.team_name if match.home_team else 'BYE',
            'homeScore': match.home_score,
            'away': match.away_team.team_name if match.away_team else 'BYE',
            'awayScore': match.away_score,
        })

    return jsonify({
        'week': week,
        'myTeam': my_team,
        'teams': teams_data,
        'matchups': matchups,
    })
except Exception as e:
    tb = traceback.format_exc()
    if 'Authentication' in str(e) or '401' in str(e) or 'private' in str(e).lower():
        return jsonify({'error': 'AUTH_EXPIRED'}), 401
    return jsonify({'error': str(e), 'trace': tb}), 500
```

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 3001))
app.run(host=‘0.0.0.0’, port=port)
