"""Static reference data: Nigeria's 36 states + FCT, and tracked fuel types."""

STATES = [
    "Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue",
    "Borno", "Cross River", "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu",
    "FCT (Abuja)", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
    "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo",
    "Osun", "Oyo", "Plateau", "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara",
]

# code -> full name. Both priced per litre, which keeps the schema simple.
# Kerosene (DPK) and cooking gas (LPG) are priced differently (and LPG by kg,
# not litre) — left out for now, see README "Known limitations".
FUEL_TYPES = {
    "PMS": "Petrol (PMS)",
    "AGO": "Diesel (AGO)",
}
