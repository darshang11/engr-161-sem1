import math
import matplotlib.pyplot as plt

# constants
SECONDS_PER_DAY = 86400
G = 9.807
GAL_PER_M3 = 264.172
KJ_PER_KWH = 3600
ETHANOL_MJ_PER_GAL = 80.1
OUTPUT_HEIGHT = 3.0

TARGET_GAL_PER_DAY = 100000
TARGET_PURITY = 0.98

# how much cost and ROI count when picking the best balanced design (add to 1)
WEIGHT_COST = 0.5
WEIGHT_ROI = 0.5

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

# extra energy effect: fraction of the flow that leaks out per meter of pipe
# 0 = no leaks (the validation case assumes none)
LEAK_FRACTION_PER_M = 0

# realistic leak rate: median real leakage in Pennsylvania DEP water audits (Kunkel, 2018)
LEAK_GAL_PER_MILE_PER_DAY = 1401
M_PER_MILE = 1609.34

# upper limit: leaks above 1% of daily flow get detected (Kuprewicz, 2007)
LEAK_UPPER_LIMIT = 0.01



# site layout: Site 3 (team floor plan)
# fermenter on the top floor, filter on the second floor,
# distiller and dehydrator on the ground floor
# total: 102 ft of pipe (40 ft vertical), 8 valves, 15 ft of CO2 ductwork
FT = 0.3048
SITE = {
    "building_cost": 1600000 * 1.1,
    "other_cost": 12000,
    "pump_to_ferm_m": 18.8976,
    "pump_to_ferm_bends": 2,
    "ferm_to_filt_m": 3.048,
    "ferm_to_filt_bends": 0,
    "filt_to_dist_m": 3.048,
    "filt_to_dist_bends": 0,
    "dist_to_dehy_m": 3.048,
    "dist_to_dehy_bends": 0,
    "dehy_to_exit_m": 3.048,
    "dehy_to_exit_bends": 0,
    "valves": 8,
    "duct_m": 4.572,
    "ferm_height": 12.192,
    "filt_height": 6.096,
    "pump_rating": 15,
}

# validation layout (Site 3 from the validation document)
VALIDATION_SITE = {
    "building_cost": 1600000 * 1.1,
    "other_cost": 12000,
    "pump_to_ferm_m": 15.24,
    "pump_to_ferm_bends": 2,
    "ferm_to_filt_m": 0,
    "ferm_to_filt_bends": 0,
    "filt_to_dist_m": 0,
    "filt_to_dist_bends": 0,
    "dist_to_dehy_m": 3.048,
    "dist_to_dehy_bends": 2,
    "dehy_to_exit_m": 0,
    "dehy_to_exit_bends": 0,
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


# Calculates the top half of the distiller formula.
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


# Removes the fraction of a stream that leaks out of a pipe of the given length.
def pipe_leak(stream, length):
    fraction = LEAK_FRACTION_PER_M * length
    stream_out = {}
    for key in stream:
        stream_out[key] = stream[key] * (1 - fraction)
    leaked = total_mass(stream) * fraction
    return stream_out, leaked


# Runs the slurry through every pipe and unit and returns every stream and waste.
def mass_balance(volume_per_day, design):
    slurry = make_slurry(volume_per_day)

    ferm_in, leak_pump_to_ferm = pipe_leak(slurry, SITE["pump_to_ferm_m"])
    ferm, co2_waste = fermenter_unit(ferm_in, FERMENTERS[design["fermenter"]]["eff"])

    filt_in, leak_ferm_to_filt = pipe_leak(ferm, SITE["ferm_to_filt_m"])
    filt, fiber_waste = filter_unit(filt_in, REMOVERS[design["filter"]]["eff"])

    dist_in, leak_filt_to_dist = pipe_leak(filt, SITE["filt_to_dist_m"])
    dist, dist_waste = distiller_unit(dist_in, DISTILLERS[design["distiller"]]["eff"])

    dehy_in, leak_dist_to_dehy = pipe_leak(dist, SITE["dist_to_dehy_m"])
    dehy, water_waste = dehydrator_unit(dehy_in, REMOVERS[design["dehydrator"]]["eff"])

    delivered, leak_dehy_to_exit = pipe_leak(dehy, SITE["dehy_to_exit_m"])

    streams = {
        "slurry": slurry,
        "ferm": ferm,
        "filt": filt,
        "dist": dist,
        "dehy": dehy,
        "delivered": delivered,
    }
    wastes = {
        "co2": co2_waste,
        "fiber": fiber_waste,
        "dist": dist_waste["sugar"] + dist_waste["water"] + dist_waste["fiber"],
        "dist_sugar": dist_waste["sugar"],
        "water": water_waste,
        "leak_pump_to_ferm": leak_pump_to_ferm,
        "leak_ferm_to_filt": leak_ferm_to_filt,
        "leak_filt_to_dist": leak_filt_to_dist,
        "leak_dist_to_dehy": leak_dist_to_dehy,
        "leak_dehy_to_exit": leak_dehy_to_exit,
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


# Average fluid speed in the pipe, v = Q / A.
def velocity(Q, A):
    return Q / A


# energy, every term in kJ/day
DT = SECONDS_PER_DAY


# Kinetic energy carried by a stream per day, 1/2 m v^2.
def kinetic_energy(mass_rate, v):
    return 0.5 * mass_rate * v ** 2 * DT / 1000


# Potential energy to lift a stream per day, m g h.
def potential_energy(mass_rate, height):
    return mass_rate * G * height * DT / 1000


# Energy lost to friction along one pipe.
def pipe_friction_loss(rho, Q, f, L, D):
    return rho * DT * (f * (8 / math.pi ** 2) * (Q ** 3 * L) / D ** 5) / 1000


# Energy lost in one pipe bend.
def bend_loss(rho, Q, xi, r):
    v = Q / (math.pi * r ** 2)
    return (rho * Q * DT) * (xi * v ** 2 / 2) / 1000


# Energy lost in one valve.
def valve_loss(rho, Q, K, r):
    v = Q / (math.pi * r ** 2)
    return (rho * Q * DT) * (K * v ** 2 / 2) / 1000


# Electricity the pump needs to do its work, given its efficiency.
def pump_input(pump_work, eta_pump):
    return pump_work / eta_pump


# Energy wasted inside the pump, (1 - eta) E_in.
def pump_loss(e_in, eta_pump):
    return (1 - eta_pump) * e_in


# Converts a unit's catalog kWh/day into kJ/day.
def unit_energy(kwh_per_day):
    return kwh_per_day * KJ_PER_KWH


# Adds up every energy term and returns pump energy, total energy in and ROI.
def energy_balance(streams, wastes, design):
    D = design["pipe_diameter"]
    r = D / 2
    f = PIPE_FRICTION[design["pipe_line"]]
    K = VALVE_K[design["valve_line"]]
    xi = BEND_XI_90
    eta_pump = PUMP_EFF[design["pump_line"]]

    # density and flow rate after each stage
    rho_slurry = stream_density(streams["slurry"])
    rho_ferm = stream_density(streams["ferm"])
    rho_filt = stream_density(streams["filt"])
    rho_dist = stream_density(streams["dist"])
    rho_dehy = stream_density(streams["dehy"])

    Q_slurry = flow_rate(streams["slurry"])
    Q_ferm = flow_rate(streams["ferm"])
    Q_filt = flow_rate(streams["filt"])
    Q_dist = flow_rate(streams["dist"])
    Q_dehy = flow_rate(streams["dehy"])

    A = pipe_area(D)
    v_slurry = velocity(Q_slurry, A)
    v_ferm = velocity(Q_ferm, A)
    v_filt = velocity(Q_filt, A)
    v_dist = velocity(Q_dist, A)
    v_dehy = velocity(Q_dehy, A)

    # pipe friction (one per pipe segment, using the stream flowing through it)
    friction_pump_to_ferm = pipe_friction_loss(rho_slurry, Q_slurry, f, SITE["pump_to_ferm_m"], D)
    friction_ferm_to_filt = pipe_friction_loss(rho_ferm, Q_ferm, f, SITE["ferm_to_filt_m"], D)
    friction_filt_to_dist = pipe_friction_loss(rho_filt, Q_filt, f, SITE["filt_to_dist_m"], D)
    friction_dist_to_dehy = pipe_friction_loss(rho_dist, Q_dist, f, SITE["dist_to_dehy_m"], D)
    friction_dehy_to_exit = pipe_friction_loss(rho_dehy, Q_dehy, f, SITE["dehy_to_exit_m"], D)

    # bends (loss of one bend times the number of bends in that segment)
    bends_pump_to_ferm = SITE["pump_to_ferm_bends"] * bend_loss(rho_slurry, Q_slurry, xi, r)
    bends_ferm_to_filt = SITE["ferm_to_filt_bends"] * bend_loss(rho_ferm, Q_ferm, xi, r)
    bends_filt_to_dist = SITE["filt_to_dist_bends"] * bend_loss(rho_filt, Q_filt, xi, r)
    bends_dist_to_dehy = SITE["dist_to_dehy_bends"] * bend_loss(rho_dist, Q_dist, xi, r)
    bends_dehy_to_exit = SITE["dehy_to_exit_bends"] * bend_loss(rho_dehy, Q_dehy, xi, r)

    # valves (entry valve sees the stream coming in, exit valve the stream going out)
    valve_ferm_in = valve_loss(rho_slurry, Q_slurry, K, r)
    valve_ferm_out = valve_loss(rho_ferm, Q_ferm, K, r)
    valve_filt_in = valve_loss(rho_ferm, Q_ferm, K, r)
    valve_filt_out = valve_loss(rho_filt, Q_filt, K, r)
    valve_dist_in = valve_loss(rho_filt, Q_filt, K, r)
    valve_dist_out = valve_loss(rho_dist, Q_dist, K, r)
    valve_dehy_in = valve_loss(rho_dist, Q_dist, K, r)
    valve_dehy_out = valve_loss(rho_dehy, Q_dehy, K, r)

    # waste streams
    co2_pe = potential_energy(wastes["co2"], SITE["ferm_height"])
    co2_ke = kinetic_energy(wastes["co2"], v_ferm)
    fiber_pe = potential_energy(wastes["fiber"], SITE["filt_height"])
    fiber_ke = kinetic_energy(wastes["fiber"], v_filt)
    dist_waste_ke = kinetic_energy(wastes["dist"], v_dist)
    dehy_waste_ke = kinetic_energy(wastes["water"], v_dehy)

    # leaks (fluid escaping a pipe carries away the kinetic energy the pump gave it)
    leak_pump_to_ferm_ke = kinetic_energy(wastes["leak_pump_to_ferm"], v_slurry)
    leak_ferm_to_filt_ke = kinetic_energy(wastes["leak_ferm_to_filt"], v_ferm)
    leak_filt_to_dist_ke = kinetic_energy(wastes["leak_filt_to_dist"], v_filt)
    leak_dist_to_dehy_ke = kinetic_energy(wastes["leak_dist_to_dehy"], v_dist)
    leak_dehy_to_exit_ke = kinetic_energy(wastes["leak_dehy_to_exit"], v_dehy)

    # product leaving the plant (E_out)
    product_ke = kinetic_energy(total_mass(streams["dehy"]), v_dehy)
    product_pe = potential_energy(total_mass(streams["dehy"]), OUTPUT_HEIGHT)

    # everything the pump has to supply
    pump_work = 0
    pump_work += friction_pump_to_ferm + friction_ferm_to_filt + friction_filt_to_dist
    pump_work += friction_dist_to_dehy + friction_dehy_to_exit
    pump_work += bends_pump_to_ferm + bends_ferm_to_filt + bends_filt_to_dist
    pump_work += bends_dist_to_dehy + bends_dehy_to_exit
    pump_work += valve_ferm_in + valve_ferm_out
    pump_work += valve_filt_in + valve_filt_out
    pump_work += valve_dist_in + valve_dist_out
    pump_work += valve_dehy_in + valve_dehy_out
    pump_work += co2_pe + co2_ke + fiber_pe + fiber_ke
    pump_work += dist_waste_ke + dehy_waste_ke
    pump_work += product_ke + product_pe
    pump_work += leak_pump_to_ferm_ke + leak_ferm_to_filt_ke + leak_filt_to_dist_ke
    pump_work += leak_dist_to_dehy_ke + leak_dehy_to_exit_ke

    # pump (E_in) and its loss
    e_pump = pump_input(pump_work, eta_pump)
    e_pump_loss = pump_loss(e_pump, eta_pump)

    # unit operations (E_unit from the catalog)
    e_ferm = unit_energy(FERMENTERS[design["fermenter"]]["kwh"])
    e_filt = unit_energy(REMOVERS[design["filter"]]["kwh"])
    e_dist = unit_energy(DISTILLERS[design["distiller"]]["kwh"])
    e_dehy = unit_energy(REMOVERS[design["dehydrator"]]["kwh"])
    e_units = e_ferm + e_filt + e_dist + e_dehy

    total_in = e_pump + e_units

    # chemical energy of the ethanol out (same method as the validation sheet)
    ethanol_volume = streams["delivered"]["ethanol"] / rho_dehy
    chem_out = ETHANOL_MJ_PER_GAL * GAL_PER_M3 * ethanol_volume * DT * 1000

    return {
        "pump": e_pump,
        "pump_loss": e_pump_loss,
        "units": e_units,
        "total_in": total_in,
        "chem_out": chem_out,
        "roi": chem_out / total_in,
        "filter_v": v_ferm,
        "dehy_waste_ke": dehy_waste_ke,
    }


# Adds up the price of the building, pump, units, pipes, ductwork, valves and bends.
def capital_cost(streams, wastes, design, bend_price=None):
    d = design["pipe_diameter"]

    # inflow to each unit = previous product + its waste, over the product density
    q_slurry = flow_rate(streams["slurry"])
    q_filt_in = (total_mass(streams["ferm"]) + wastes["co2"]) / stream_density(streams["ferm"])
    q_dist_in = (total_mass(streams["filt"]) + wastes["fiber"]) / stream_density(streams["filt"])
    q_dehy_in = (total_mass(streams["dist"]) + wastes["dist"]) / stream_density(streams["dist"])

    if bend_price is None:
        bend_price = BEND_COST_90[d]

    cost = SITE["building_cost"] + SITE["other_cost"]
    cost += PUMP_COST[SITE["pump_rating"]][design["pump_line"]] * q_slurry
    cost += FERMENTERS[design["fermenter"]]["cost"] * q_slurry
    cost += REMOVERS[design["filter"]]["cost"] * q_filt_in
    cost += DISTILLERS[design["distiller"]]["cost"] * q_dist_in
    cost += REMOVERS[design["dehydrator"]]["cost"] * q_dehy_in
    total_pipe_m = SITE["pump_to_ferm_m"] + SITE["ferm_to_filt_m"] + SITE["filt_to_dist_m"]
    total_pipe_m += SITE["dist_to_dehy_m"] + SITE["dehy_to_exit_m"]
    total_bends = SITE["pump_to_ferm_bends"] + SITE["ferm_to_filt_bends"] + SITE["filt_to_dist_bends"]
    total_bends += SITE["dist_to_dehy_bends"] + SITE["dehy_to_exit_bends"]

    cost += PIPE_COST[d][design["pipe_line"]] * total_pipe_m
    cost += DUCT_COST_PER_M * SITE["duct_m"]
    cost += VALVE_COST[d][design["valve_line"]] * SITE["valves"]
    cost += bend_price * total_bends
    return cost



# full model

# Runs mass, energy and cost for one design at one slurry volume.
def run_model(design, volume_per_day, bend_price=None):
    streams, wastes = mass_balance(volume_per_day, design)
    energy = energy_balance(streams, wastes, design)
    cost = capital_cost(streams, wastes, design, bend_price)

    output = streams["delivered"]
    gallons = flow_rate(output) * SECONDS_PER_DAY * GAL_PER_M3
    purity = output["ethanol"] / total_mass(output)

    return {
        "cost": cost,
        "roi": energy["roi"],
        "gallons": gallons,
        "purity": purity,
        "slurry_gal": volume_per_day * GAL_PER_M3,
        "energy": energy,
        "wastes": wastes,
    }


# Scales the slurry so the design makes exactly 100,000 gal/day, then runs it.
def run_at_target(design):
    # everything scales with input, so run once and rescale to 100,000 gal/day
    trial = run_model(design, 1000)
    volume = 1000 * TARGET_GAL_PER_DAY / trial["gallons"]
    return run_model(design, volume)


# validation

VALIDATION_DESIGN = {
    "fermenter": "Scrap",
    "filter": "Scrap",
    "distiller": "Scrap",
    "dehydrator": "Scrap",
    "pump_line": "Cheap",
    "pipe_line": "Nice",
    "pipe_diameter": 0.10,
    "valve_line": "Salvage",
}


# Runs the course's validation case (on its own layout) and prints each result next to its expected value.
def run_validation():
    global SITE
    team_site = SITE
    SITE = VALIDATION_SITE
    r = run_model(VALIDATION_DESIGN, 3161.58, bend_price=100)
    SITE = team_site
    print("VALIDATION CASE")
    print("Velocity into filter:", round(r["energy"]["filter_v"], 2), "m/s  (expected 4.69)")
    print("Dehydrator waste KE:", round(r["energy"]["dehy_waste_ke"], 2), "kJ/day  (expected 1.23)")
    print("Distiller sugar waste:", round(r["wastes"]["dist_sugar"] * SECONDS_PER_DAY), "kg/day  (expected 367,500)")
    print("Capital cost: $", round(r["cost"]), "  (expected 1,867,000)")
    print("Energy ROI:", round(r["roi"], 2), "  (expected 5.55)")
    print("Ethanol out:", round(r["gallons"]), "gal/day  (expected 68,700)")
    print("Purity:", round(r["purity"] * 100, 1), "%  (expected 87)")
    print()


# design search


# Prints one design's parts and results.
def print_design(design, r):
    print("  Fermenter:", design["fermenter"], "| Filter:", design["filter"],
          "| Distiller:", design["distiller"], "| Dehydrator:", design["dehydrator"])
    print("  Pump:", design["pump_line"], "| Pipe:", design["pipe_line"], design["pipe_diameter"], "m",
          "| Valves:", design["valve_line"])
    print("  Capital cost: $", round(r["cost"]))
    print("  Energy ROI:", round(r["roi"], 2))
    print("  Ethanol out:", round(r["gallons"]), "gal/day at", round(r["purity"] * 100, 2), "%")
    print("  Slurry needed:", round(r["slurry_gal"]), "gal/day")


# Gives a design a 0-to-1 score for cost and ROI, then blends them with the weights.
def balance_score(r, cost_min, cost_max, roi_min, roi_max):
    cost_score = (cost_max - r["cost"]) / (cost_max - cost_min)
    roi_score = (r["roi"] - roi_min) / (roi_max - roi_min)
    return WEIGHT_COST * cost_score + WEIGHT_ROI * roi_score


# Tries every catalog combo and prints the cheapest, highest-ROI and best balanced designs.
def search():
    passing = []

    for ferm in FERMENTERS:
        for filt in REMOVERS:
            for dist in DISTILLERS:
                for dehy in REMOVERS:
                    for pump in PUMP_EFF:
                        for pipe in PIPE_FRICTION:
                            for diameter in PIPE_COST:
                                for valve in VALVE_K:
                                    design = {
                                        "fermenter": ferm,
                                        "filter": filt,
                                        "distiller": dist,
                                        "dehydrator": dehy,
                                        "pump_line": pump,
                                        "pipe_line": pipe,
                                        "pipe_diameter": diameter,
                                        "valve_line": valve,
                                    }
                                    r = run_at_target(design)
                                    if r["purity"] < TARGET_PURITY:
                                        continue
                                    passing.append((design, r))

    # find the cheapest and highest-ROI designs, and the range of cost and ROI
    best_cost = passing[0]
    best_roi = passing[0]
    for item in passing:
        if item[1]["cost"] < best_cost[1]["cost"]:
            best_cost = item
        if item[1]["roi"] > best_roi[1]["roi"]:
            best_roi = item

    cost_min = best_cost[1]["cost"]
    roi_max = best_roi[1]["roi"]
    cost_max = cost_min
    roi_min = roi_max
    for item in passing:
        if item[1]["cost"] > cost_max:
            cost_max = item[1]["cost"]
        if item[1]["roi"] < roi_min:
            roi_min = item[1]["roi"]

    # best balanced design: highest blended score
    best_balanced = passing[0]
    best_score = balance_score(passing[0][1], cost_min, cost_max, roi_min, roi_max)
    for item in passing:
        score = balance_score(item[1], cost_min, cost_max, roi_min, roi_max)
        if score > best_score:
            best_score = score
            best_balanced = item

    print("DESIGN SEARCH:", len(passing), "designs make 100,000 gal/day at 98% or better")
    print()
    print("Cheapest design:")
    print_design(best_cost[0], best_cost[1])
    print()
    print("Highest ROI design:")
    print_design(best_roi[0], best_roi[1])
    print()
    print("Best balanced design (cost weight", WEIGHT_COST, "| ROI weight", str(WEIGHT_ROI) + "):")
    print_design(best_balanced[0], best_balanced[1])
    print()
    return best_balanced, best_cost, best_roi, passing


# leak check
# Reruns one design with no leaks, a realistic leak rate and the 1% upper limit.
def check_leaks(design):
    global LEAK_FRACTION_PER_M

    no_leak = run_at_target(design)

    total_pipe_m = SITE["pump_to_ferm_m"] + SITE["ferm_to_filt_m"] + SITE["filt_to_dist_m"]
    total_pipe_m += SITE["dist_to_dehy_m"] + SITE["dehy_to_exit_m"]

    # realistic: water audit median, turned into a fraction of the flow per meter
    realistic_rate = (LEAK_GAL_PER_MILE_PER_DAY / M_PER_MILE) / no_leak["slurry_gal"]

    # upper limit: 1% of the flow lost over all the pipe (leaks bigger than this get caught)
    upper_limit_rate = LEAK_UPPER_LIMIT / total_pipe_m

    cases = [
        ("No leaks", 0),
        ("Realistic (water audit median)", realistic_rate),
        ("Upper limit (1% of flow)", upper_limit_rate),
    ]

    print("LEAK CHECK (best balanced design, sized to 100,000 gal/day)")
    for name, rate in cases:
        LEAK_FRACTION_PER_M = rate
        r = run_at_target(design)
        print("  " + name + ":",
              "slurry needed", round(r["slurry_gal"]), "gal/day |",
              "ROI", round(r["roi"], 4), "|",
              "cost $", round(r["cost"]))
    LEAK_FRACTION_PER_M = 0
    print()


# graph
# Plots ROI vs capital cost for every design that meets spec, with the three picks marked.
def plot_results(passing, best_cost, best_roi, best_balanced):
    costs = []
    rois = []
    for item in passing:
        costs.append(item[1]["cost"] / 1e6)
        rois.append(item[1]["roi"])

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(costs, rois, s=6, color="#b4b2a9", alpha=0.5, label="Designs that meet spec")
    ax.axhline(10, color="#5f5e5a", linestyle="--", linewidth=1.5)
    ax.text(3.45, 9.92, "Client goal (10x)", ha="center", va="top", fontsize=11, color="#444441")

    picks = [
        ("Cheapest", best_cost, "#2a78d6", "o", (40, -45)),
        ("Best balanced", best_balanced, "#eb6834", "s", (40, 8)),
        ("Highest ROI", best_roi, "#1baf7a", "^", (-150, -50)),
    ]
    for name, item, color, marker, offset in picks:
        x = item[1]["cost"] / 1e6
        y = item[1]["roi"]
        ax.scatter([x], [y], s=120, color=color, marker=marker, edgecolors="white", linewidths=2,
                   zorder=3, label=name)
        ax.annotate(name + "\n$" + str(round(x, 2)) + "M, ROI " + str(round(y, 2)), (x, y),
                    textcoords="offset points", xytext=offset, fontsize=10, color="#2c2c2a",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#b4b2a9"),
                    arrowprops=dict(arrowstyle="-", color="#5f5e5a", linewidth=1))

    ax.set_ylim(top=11.8)
    ax.set_xlabel("Capital cost (millions of $)", fontsize=12)
    ax.set_ylabel("Energy ROI (energy out / energy in)", fontsize=12)
    ax.set_title("Energy ROI vs capital cost, Site 3 (100,000 gal/day, 98%+ purity)", fontsize=13)
    ax.grid(color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig("roi_vs_cost.png", dpi=300)
    plt.show()


run_validation()
best_balanced, best_cost, best_roi, passing = search()
check_leaks(best_balanced[0])
plot_results(passing, best_cost, best_roi, best_balanced)
