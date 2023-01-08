
CRIME_COLS = ["Date of Report", "Crime", "Address", "Time of Report", "Full Text"]
ALERTING_CRIME_OPTIONS = [
    "Fire", "Shooting", "Stabbing", "Robbery", "Sound of Gunshots", "Gas Leak", "Person with a Knife", 
    "Person with a Gun", "Missing", "Protest", "Industrial Accident", "Wires Down", "Marine Rescue",
    "Collision", "Police Investigation", "Demonstration", "Assault"
]
ALERTING_CRIME_DEFAULTS = [
    'Shooting', 'Stabbing', 'Robbery', 'Assault',
    'Person with a Gun', 'Sound of Gunshots', 'Person with a Knife'
]
CRIME_REGEX = {
    "fire": "Fire",
    "shooting": "Shooting",
    "stabbing": "Stabbing",
    "robbery": "Robbery",
    "gunshot": "Sound of Gunshots",
    "gas leak": "Gas Leak",
    "knife": "Person With a Knife",
    "gun\s": "Person with a Gun",
    "gun$": "Person with a Gun",
    "missing": "Missing",
    "protest": "Protest",
    "industrial accident": "Industrial Accident",
    "wires down": "Wires Down",
    "marine rescue": "Marine Rescue",
    "collision": "Collision",
    "police investigation": "Police Investigation",
    "demonstration": "Demonstration",
    "assault": "Assault"
}