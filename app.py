from flask import Flask, jsonify
from flask_cors import CORS
from espn_api.baseball import League
import os
import traceback

app = Flask(__name__)
CORS(app)

LEAGUE_ID = 83176
YEAR = 2026
ESPN_S2 = os.environ.get("ESPN_S2")
SWID = os.environ.get("SWID")

def get_league():
    return League(league_id=LEAGUE_ID, year=YEAR, espn_s2=ESPN_S2, swid=SWID)

@app.route("/health")
def health():
    return jsonify({"status": "ok", "hasCredentials": bool(ESPN_S2 and SWID)})

@app.route("/api/teams")
def teams():
    try:
        league = get_league()
        teams_data = []
        for team in league.teams:
            teams_data.append({
                "id": team.team_id,
                "name": team.team_name,
                "owners": ", ".join(team.owners),
                "wins": team.wins,
                "losses": team.losses,
                "roster": [{"name": p.name, "position": p.position, "proTeam": p.proTeam, "injuryStatus": p.injuryStatus} for p in team.roster]
            })
        return jsonify({"teams": teams_data})
    except Exception as e:
        tb = traceback.format_exc()
        if "Authentication" in str(e) or "401" in str(e) or "private" in str(e).lower():
            return jsonify({"error": "AUTH_EXPIRED"}), 401
        return jsonify({"error": str(e), "trace": tb}), 500

@app.route("/api/standings")
def standings():
    try:
        league = get_league()
        data = [{"name": t.team_name, "owners": ", ".join(t.owners), "wins": t.wins, "losses": t.losses} for t in sorted(league.teams, key=lambda t: t.wins, reverse=True)]
        return jsonify({"standings": data})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/matchup")
def matchup():
    try:
        league = get_league()
        week = league.currentMatchupPeriod
        box_scores = league.box_scores(week)
        matchups = [{"home": m.home_team.team_name, "homeScore": m.home_score, "away": m.away_team.team_name, "awayScore": m.away_score} for m in box_scores]
        return jsonify({"matchups": matchups, "week": week})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route("/api/dashboard")
def dashboard():
    try:
        league = get_league()
        week = league.currentMatchupPeriod
        teams_data = []
        my_team = None
        for team in league.teams:
            t = {
                "id": team.team_id,
                "name": team.team_name,
                "owners": ", ".join(team.owners),
                "wins": team.wins,
                "losses": team.losses,
                "roster": [{"name": p.name, "position": p.position, "proTeam": p.proTeam, "injuryStatus": p.injuryStatus} for p in team.roster]
            }
            teams_data.append(t)
            if "slumber" in team.team_name.lower() or "matt" in str(team.owners).lower():
                my_team = t
        box_scores = league.box_scores(week)
        matchups = [{"home": m.home_team.team_name, "homeScore": m.home_score, "away": m.away_team.team_name, "awayScore": m.away_score} for m in box_scores]
        return jsonify({"week": week, "myTeam": my_team, "teams": teams_data, "matchups": matchups})
    except Exception as e:
        tb = traceback.format_exc()
        if "Authentication" in str(e) or "401" in str(e) or "private" in str(e).lower():
            return jsonify({"error": "AUTH_EXPIRED"}), 401
        return jsonify({"error": str(e), "trace": tb}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3001))
    app.run(host="0.0.0.0", port=port)
