import os
import json
import pandas as pd

folder_path = "C:/Users/katiy/OneDrive/Desktop/IPL data set/ipl_male_json"   # path of JSON files folder 

matches = []
deliveries = []

for file in os.listdir(folder_path):

    if file.endswith(".json"):

        with open(os.path.join(folder_path, file), encoding="utf-8") as f:
            data = json.load(f)

        info = data["info"]
        match_id = file.replace(".json", "")
        teams = info["teams"]

        # ---------------- TARGET RUN CALCULATION ----------------
        first_innings_total = 0

        first_innings = data["innings"][0]

        for over_data in first_innings["overs"]:
            for ball_data in over_data["deliveries"]:
                first_innings_total += ball_data["runs"]["total"]

        target_runs = first_innings_total + 1
        target_overs = info.get("overs", 20)

        # ---------------- MATCH RESULT ----------------
        outcome = info.get("outcome", {})

        result_margin = None
        if "by" in outcome:
            result_margin = list(outcome["by"].values())[0]

        # ---------------- MATCHES TABLE ----------------
        match_row = {

            "id": match_id,
            "season": info.get("season"),
            "city": info.get("city"),
            "date": info["dates"][0],
            "match_type": info.get("match_type"),
            "player_of_match": ",".join(info.get("player_of_match", [])),
            "venue": info.get("venue"),
            "team1": teams[0],
            "team2": teams[1],
            "toss_winner": info["toss"]["winner"],
            "toss_decision": info["toss"]["decision"],
            "winner": outcome.get("winner"),
            "result": "normal",
            "result_margin": result_margin,
            "target_runs": target_runs,
            "target_overs": target_overs,
            "super_over": "N",
            "method": outcome.get("method"),
            "umpire1": info["officials"]["umpires"][0],
            "umpire2": info["officials"]["umpires"][1]

        }

        matches.append(match_row)

        # ---------------- DELIVERIES TABLE ----------------
        for inning_no, inning in enumerate(data["innings"], start=1):

            batting_team = inning["team"]

            bowling_team = teams[1] if batting_team == teams[0] else teams[0]

            for over_data in inning["overs"]:

                over = over_data["over"]

                for ball_no, ball_data in enumerate(over_data["deliveries"], start=1):

                    runs = ball_data["runs"]

                    # extras type
                    extras_type = "NA"
                    if "extras" in ball_data:
                        extras_type = ",".join(ball_data["extras"].keys())

                    # wicket info
                    is_wicket = 0
                    player_dismissed = "NA"
                    dismissal_kind = "NA"
                    fielder = "NA"

                    if "wickets" in ball_data:

                        is_wicket = 1
                        wicket = ball_data["wickets"][0]

                        player_dismissed = wicket.get("player_out", "NA")
                        dismissal_kind = wicket.get("kind", "NA")

                        if "fielders" in wicket:
                            fielder = wicket["fielders"][0].get("name", "NA")

                    delivery_row = {

                        "match_id": match_id,
                        "inning": inning_no,
                        "batting_team": batting_team,
                        "bowling_team": bowling_team,
                        "over": over,
                        "ball": ball_no,
                        "batter": ball_data.get("batter"),
                        "bowler": ball_data.get("bowler"),
                        "non_striker": ball_data.get("non_striker"),
                        "batsman_runs": runs.get("batter", 0),
                        "extra_runs": runs.get("extras", 0),
                        "total_runs": runs.get("total", 0),
                        "extras_type": extras_type,
                        "is_wicket": is_wicket,
                        "player_dismissed": player_dismissed,
                        "dismissal_kind": dismissal_kind,
                        "fielder": fielder

                    }

                    deliveries.append(delivery_row)

# ---------------- CREATE DATAFRAMES ----------------
matches_df = pd.DataFrame(matches)
deliveries_df = pd.DataFrame(deliveries)

# ---------------- SAVE CSV ----------------
matches_df.to_csv("matches.csv", index=False)
deliveries_df.to_csv("deliveries.csv", index=False)

print("✅ matches.csv and deliveries.csv created successfully")
