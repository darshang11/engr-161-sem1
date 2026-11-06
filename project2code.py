import math

# constants
SECONDS_PER_DAY = 86400
G = 9.807
GAL_PER_M3 = 264.172
KJ_PER_KWH = 3600
ETHANOL_MJ_PER_GAL = 80.1
OUTPUT_HEIGHT = 3.0

TARGET_GAL_PER_DAY = 100000
TARGET_PURITY = 0.98

DENSITIES = {"sugar": 1599, "water": 997, "fiber": 1311, "ethanol": 789}
SLURRY_FRACTIONS = {"sugar": 0.2, "water": 0.6, "fiber": 0.2, "ethanol": 0.0}


# parts
FERMENTERS = {
    "Scrap":       {"eff": 0.50, "kwh": 46600, "cost": 320000},
    "Average":     {"eff": 0.75, "kwh": 47200, "cost": 380000},
    "Premium":     {"eff": 0.90, "kwh": 47500, "cost": 460000},
    "World-class": {"eff": 0.95, "kwh": 48000, "cost": 1100000},
}

DISTILLERS = {
    "Scrap":       {"eff": 0.81,  "kwh": 47004, "cost": 390000},
    "Average":     {"eff": 0.90,  "kwh": 47812, "cost": 460000},
    "Premium":     {"eff": 0.915, "kwh": 48200, "cost": 560000},
    "World-class": {"eff": 0.98,  "kwh": 49500, "cost": 1370000},
}

# filters and dehydrators share this table
REMOVERS = {
    "Scrap":       {"eff": 0.50, "kwh": 48800, "cost": 200000},
    "Average":     {"eff": 0.75, "kwh": 49536, "cost": 240000},
    "Premium":     {"eff": 0.90, "kwh": 50350, "cost": 280000},
    "World-class": {"eff": 0.98, "kwh": 51000, "cost": 480000},
}

PUMP_EFF = {"Cheap": 0.80, "Value": 0.83, "Standard": 0.86, "High-Grade": 0.89, "Premium": 0.92}


PUMP_COST = {
    6:  {"Cheap": 200000, "Value": 240000, "Standard": 280000, "High-Grade": 340000, "Premium": 415000},
    9:  {"Cheap": 220000, "Value": 260000, "Standard": 310000, "High-Grade": 380000, "Premium": 456000},
    12: {"Cheap": 240000, "Value": 290000, "Standard": 340000, "High-Grade": 410000, "Premium": 502000},
    15: {"Cheap": 260000, "Value": 310000, "Standard": 380000, "High-Grade": 460000, "Premium": 552000},
    18: {"Cheap": 290000, "Value": 350000, "Standard": 420000, "High-Grade": 500000, "Premium": 607000},
    21: {"Cheap": 320000, "Value": 380000, "Standard": 460000, "High-Grade": 550000, "Premium": 668000},
    24: {"Cheap": 350000, "Value": 420000, "Standard": 510000, "High-Grade": 610000, "Premium": 735000},
    27: {"Cheap": 390000, "Value": 460000, "Standard": 560000, "High-Grade": 670000, "Premium": 808000},
    30: {"Cheap": 420000, "Value": 510000, "Standard": 610000, "High-Grade": 740000, "Premium": 889000},
    33: {"Cheap": 470000, "Value": 560000, "Standard": 670000, "High-Grade": 810000, "Premium": 978000},
    36: {"Cheap": 510000, "Value": 620000, "Standard": 740000, "High-Grade": 890000, "Premium": 1076000},
}

PIPE_FRICTION = {"Salvage": 0.05, "Questionable": 0.03, "Better": 0.02,
                 "Nice": 0.01, "Outstanding": 0.005, "Glorious": 0.002}

# $ per m, by internal diameter (m)
PIPE_COST = {
    0.10: {"Salvage": 1000,  "Questionable": 1200,  "Better": 1440,  "Nice": 2160,  "Outstanding": 2700,  "Glorious": 2970},
    0.11: {"Salvage": 1200,  "Questionable": 1440,  "Better": 1720,  "Nice": 2580,  "Outstanding": 3230,  "Glorious": 3550},
    0.12: {"Salvage": 2570,  "Questionable": 3080,  "Better": 3700,  "Nice": 5550,  "Outstanding": 6940,  "Glorious": 7640},
    0.13: {"Salvage": 6300,  "Questionable": 7560,  "Better": 9070,  "Nice": 14000, "Outstanding": 17000, "Glorious": 19000},
    0.14: {"Salvage": 14000, "Questionable": 16000, "Better": 20000, "Nice": 29000, "Outstanding": 37000, "Glorious": 40000},
    0.15: {"Salvage": 26000, "Questionable": 31000, "Better": 37000, "Nice": 55000, "Outstanding": 69000, "Glorious": 76000},
}

DUCT_COST_PER_M = 228

VALVE_K = {"Salvage": 800, "Questionable": 700, "Outstanding": 600, "Glorious": 500}

VALVE_COST = {
    0.10: {"Salvage": 100,  "Questionable": 120,  "Outstanding": 270,  "Glorious": 297},
    0.11: {"Salvage": 120,  "Questionable": 144,  "Outstanding": 323,  "Glorious": 355},
    0.12: {"Salvage": 257,  "Questionable": 308,  "Outstanding": 694,  "Glorious": 764},
    0.13: {"Salvage": 630,  "Questionable": 756,  "Outstanding": 1700, "Glorious": 1900},
    0.14: {"Salvage": 1400, "Questionable": 1600, "Outstanding": 3700, "Glorious": 4000},
    0.15: {"Salvage": 2600, "Questionable": 3100, "Outstanding": 6900, "Glorious": 7600},
}

BEND_XI_90 = 0.3
BEND_COST_90 = {0.10: 128, 0.11: 190, 0.12: 700, 0.13: 1800, 0.14: 4100, 0.15: 8000}

SITE = {
    "building_cost": 1600000 * 1.1,
    "other_cost": 12000,
    "long_pipe_m": 15.24,
    "short_pipe_m": 3.048,
    "bends_long": 2,
    "bends_short": 2,
    "valves": 8,
    "duct_m": 3.048,
    "ferm_height": 12.192,
    "filt_height": 6.096,
    "pump_rating": 18,
}

# mass

# Converts the chosen fraction of sugar into ethanol and CO2, passing water and fiber through.
def fermenter_unit(stream_in, n_ferm):
    carbon_waste = 0.49 * stream_in["sugar"] * n_ferm
    stream_out = {
        "sugar": stream_in["sugar"] * (1 - n_ferm),
        "water": stream_in["water"],
        "fiber": stream_in["fiber"],
        "ethanol": 0.51 * stream_in["sugar"] * n_ferm,
    }
    return stream_out, carbon_waste


# Removes the chosen fraction of fiber and passes everything else through.
def filter_unit(stream_in, n_filt):
    fiber_waste = stream_in["fiber"] * n_filt
    stream_out = {
        "sugar": stream_in["sugar"],
        "water": stream_in["water"],
        "fiber": stream_in["fiber"] * (1 - n_filt),
        "ethanol": stream_in["ethanol"],
    }
    return stream_out, fiber_waste


# Calculates the top half of the distiller formula
def distiller_numerator_helper(mass_in, ethanol_in, n_distill):
    return mass_in * ethanol_in * (1 / n_distill - 1)


# Lets all ethanol through and cuts sugar, water and fiber down to hit the distiller's purity.
def distiller_unit(stream_in, n_distill):
    m_sum = stream_in["water"] + stream_in["sugar"] + stream_in["fiber"]
    stream_out = {
        "ethanol": stream_in["ethanol"],
        "water": distiller_numerator_helper(stream_in["water"], stream_in["ethanol"], n_distill) / m_sum,
        "sugar": distiller_numerator_helper(stream_in["sugar"], stream_in["ethanol"], n_distill) / m_sum,
        "fiber": distiller_numerator_helper(stream_in["fiber"], stream_in["ethanol"], n_distill) / m_sum,
    }
    waste_out = {
        "fiber": stream_in["fiber"] - stream_out["fiber"],
        "sugar": stream_in["sugar"] - stream_out["sugar"],
        "water": stream_in["water"] - stream_out["water"],
    }
    return stream_out, waste_out


# Removes the chosen fraction of water and passes everything else through.
def dehydrator_unit(stream_in, n_dehy):
    water_waste = stream_in["water"] * n_dehy
    stream_out = {
        "water": stream_in["water"] * (1 - n_dehy),
        "ethanol": stream_in["ethanol"],
        "sugar": stream_in["sugar"],
        "fiber": stream_in["fiber"],
    }
    return stream_out, water_waste


# Turns a daily slurry volume into kg/s of sugar, water, fiber and ethanol.
def make_slurry(volume_per_day):
    total_mass = volume_per_day * stream_density(SLURRY_FRACTIONS) / SECONDS_PER_DAY
    slurry = {}
    for key in SLURRY_FRACTIONS:
        slurry[key] = SLURRY_FRACTIONS[key] * total_mass
    return slurry


# Runs the slurry through all four units and returns every stream and waste.
def mass_balance(volume_per_day, design):
    slurry = make_slurry(volume_per_day)
    ferm, co2_waste = fermenter_unit(slurry, FERMENTERS[design["fermenter"]]["eff"])
    filt, fiber_waste = filter_unit(ferm, REMOVERS[design["filter"]]["eff"])
    dist, dist_waste = distiller_unit(filt, DISTILLERS[design["distiller"]]["eff"])
    dehy, water_waste = dehydrator_unit(dist, REMOVERS[design["dehydrator"]]["eff"])

    streams = {"slurry": slurry, "ferm": ferm, "filt": filt, "dist": dist, "dehy": dehy}
    wastes = {
        "co2": co2_waste,
        "fiber": fiber_waste,
        "dist": dist_waste["sugar"] + dist_waste["water"] + dist_waste["fiber"],
        "dist_sugar": dist_waste["sugar"],
        "water": water_waste,
    }
    return streams, wastes


# density, flow rate, velocity

# Adds up all four components of a stream.
def total_mass(stream):
    total = 0
    for key in stream:
        total += stream[key]
    return total


# Finds a stream's mixed density as a mass-weighted average.
def stream_density(stream):
    fluid_density = 0
    for key in DENSITIES:
        fluid_density += DENSITIES[key] * stream[key]
    return fluid_density / total_mass(stream)


# Pipe cross-sectional area, A = pi D^2 / 4.
def pipe_area(D):
    return math.pi * D ** 2 / 4


# Volume of fluid moved during time t, V = mass / density.
def volume_moved(stream, t):
    return total_mass(stream) * t / stream_density(stream)


# Volumetric flow rate, Q = V / t.
def flow_rate(stream):
    t = SECONDS_PER_DAY
    V = volume_moved(stream, t)
    return V / t

