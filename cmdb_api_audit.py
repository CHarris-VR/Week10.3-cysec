import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

# Created a api url for the headers and created headers to load requests from the api key
API_URL = "https://my.api.mockaroo.com/ironclad/cmdb.json"

headers = {
    "X-API-Key": "cf7bbbd0" # Loading API key into headers
}

# Changed the Response = Request for challenge A
try:
    response = requests.get(API_URL, headers=headers, timeout=10)
    print("Status code:", response.status_code)
except ConnectionError:
    print("Network error: unable to connect to API host.") # Handling connection errors
    raise SystemExit
except Timeout:
    print("Network error: request timed out.") # Handling timeout errors
    raise SystemExit
except RequestException as e:
    print("Unexpected request error:", e) # Handling other request exceptions
    raise SystemExit

# Checking for malformed JSON in the response: Success!
try:
    data = response.json()
except ValueError:
    print("Error: API returned invalid JSON.")  # Handling malformed JSON
    print("Response preview:", response.text[:200])
    raise SystemExit


# Check if the request was successful
if response.status_code != 200:
    print("Request failed:", response.status_code)
    print("Response preview:", response.text[:200])
    raise SystemExit

# Parse the JSON response
data = response.json()
print("Type of data:", type(data))

if isinstance(data, list) and data:
    print("Number of assets:", len(data))
    print("Fields available:", list(data[0].keys()))
    print("First asset preview:", data[0])
else:
    print("Unexpected JSON structure. Expected a list of assets.")
    raise SystemExit

# Check point for errors: No errors found in the response


# Creating Asset Class: 
class Asset:
    def __init__(self, raw: dict):
        self.raw = raw
        self.asset_id = raw.get("asset_id")
        self.hostname = raw.get("hostname", "unknown")
        self.asset_type = raw.get("asset_type", "unknown")
        self.os = raw.get("os", "unknown")
        self.environment = raw.get("environment", "unknown")
        self.owner_team = raw.get("owner_team", "unknown")
        self.internet_exposed = bool(raw.get("internet_exposed", False))
        self.criticality = raw.get("criticality", "low")
        self.last_seen = raw.get("last_seen", "unknown")

    def risk_level(self) -> str:
        """
        A simple (not perfect) risk rule set:
        - HIGH if internet_exposed AND criticality is high
        - MEDIUM if internet_exposed OR criticality is high
        - LOW otherwise
        """
        crit_high = str(self.criticality).lower() == "high"
        if self.internet_exposed and crit_high:
            return "HIGH"
        if self.internet_exposed or crit_high:
            return "MEDIUM"
        return "LOW"

    def __str__(self) -> str:
        return (f"{self.hostname} ({self.asset_type}, {self.os}, {self.environment}) "
                f"owner={self.owner_team} exposed={self.internet_exposed} "
                f"crit={self.criticality} last_seen={self.last_seen} risk={self.risk_level()}")
    
    # Checking for failures in the Asset class: No failures found


# Creating Asset objects from the data
assets = []
for record in data:
    assets.append(Asset(record))

# Reviewing assets based on priority (Challenge B)
high_priority = [
    a for a in assets
    if str(a.environment).lower() == "prod"
    and (a.internet_exposed or str(a.criticality).lower() == "high")
]

# Printing high priority assets
print("\n=== High Priority Review (Prod + Exposed/Critical) ===")
if high_priority:
    for a in high_priority:
        print(
            f"{a.hostname} | owner={a.owner_team} | "
            f"exposed={a.internet_exposed} | crit={a.criticality} | "
            f"env={a.environment} | risk={a.risk_level()}"
        )
else:
    print("None found.")
print("\nFirst asset object:")
print(assets[0] if assets else "No assets")

# Challenge C: Generate Top 3 owner teams by high risk
high_risk_by_team = {}
for a in assets:
    if a.risk_level() == "HIGH":
        team = a.owner_team
        high_risk_by_team[team] = high_risk_by_team.get(team, 0) + 1

# Sorting and getting top 3 teams
top_3_teams = sorted(high_risk_by_team.items(), key=lambda x: x[1], reverse=True)[:3]
print("\n=== Top 3 Owner Teams by High Risk Assets ===")
if top_3_teams:
    for team, count in top_3_teams:
        print(f"{team}: {count} high risk assets")
else:
    print("No high risk assets found.")

# Counting assets by environment
env_counts = {}
for a in assets:
    env = a.environment
    env_counts[env] = env_counts.get(env, 0) + 1

print("\n=== Assets by Environment ===")
for env, count in env_counts.items():
    print(env, count)

# Counting assets by risk level
risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
for a in assets:
    risk_counts[a.risk_level()] += 1

print("\n=== Assets by Risk Level ===")
for k, v in risk_counts.items():
    print(k, v)

# Listing internet-exposed assets
exposed = [a for a in assets if a.internet_exposed]

print("\n=== Internet-Exposed Assets ===")
for a in exposed:
    print(f"{a.hostname} | owner={a.owner_team} | crit={a.criticality} | env={a.environment}")


# Writing summary report to a text file
with open("cmdb_summary.txt", "w", encoding="utf-8") as out:
    out.write("Ironclad CMDB API Audit Report\n")
    out.write("==============================\n")
    out.write(f"URL: {API_URL}\n")
    out.write(f"Status: {response.status_code}\n")
    out.write(f"Total assets: {len(assets)}\n\n")

    out.write("Assets by Environment:\n")
    for env, count in env_counts.items():
        out.write(f"- {env}: {count}\n")

    out.write("\nAssets by Risk Level:\n")
    for level, count in risk_counts.items():
        out.write(f"- {level}: {count}\n")

    # Internet-Exposed Assets
    out.write("\nInternet-Exposed Assets:\n")
    for a in exposed:
        out.write(f"- {a.hostname} | owner={a.owner_team} | crit={a.criticality} | env={a.environment}\n")

    # High Priority Assets : Success!
    out.write("\nHigh Priority Assets (Prod + Exposed/Critical):\n")
    if high_priority:
        for a in high_priority:
            out.write(f"- {a.hostname} | owner={a.owner_team} | exposed={a.internet_exposed} | crit={a.criticality} | env={a.environment} | risk={a.risk_level()}\n")
    else:
        out.write("None found.\n")
    
    # Top 3 Owner Teams by High Risk Assets as header for challenge C
    out.write("\nTop 3 Owner Teams by High Risk Assets:\n")
    if top_3_teams:
        for team, count in top_3_teams:
            out.write(f"- {team}: {count} high risk assets\n")
    else:
        out.write("No high risk assets found.\n")

    print("\nWrote report to cmdb_summary.txt")

# Testing summary report for errors: No errors found in the report Success!