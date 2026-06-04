# -*- coding: utf-8 -*-
import CoolProp.CoolProp as CP
import numpy as np
import matplotlib.pyplot as plt

def calculate_orc_efficiency(fluid, T_evap_C, T_cond_C=35.0, eta_t=0.85, eta_p=0.80):
    """
    Calculates the thermal efficiency of an ORC system for a specific fluid and temperature.
    """
    try:
        T_evap = T_evap_C + 273.15
        T_cond = T_cond_C + 273.15
        
        # 1. Pressures
        P_evap = CP.PropsSI('P', 'T', T_evap, 'Q', 1, fluid)
        P_cond = CP.PropsSI('P', 'T', T_cond, 'Q', 0, fluid)
        
        # 2. Pump (State 1 to 2)
        h1 = CP.PropsSI('H', 'P', P_cond, 'Q', 0, fluid)
        v1 = 1 / CP.PropsSI('D', 'P', P_cond, 'Q', 0, fluid)
        w_pump = (v1 * (P_evap - P_cond)) / eta_p
        h2 = h1 + w_pump
        
        # 3. Evaporator Exit (State 3) - Assumed Saturated Vapor
        h3 = CP.PropsSI('H', 'P', P_evap, 'Q', 1, fluid)
        s3 = CP.PropsSI('S', 'P', P_evap, 'Q', 1, fluid)
        
        # 4. Turbine (State 3 to 4)
        h4_s = CP.PropsSI('H', 'P', P_cond, 'S', s3, fluid)
        w_turbine = (h3 - h4_s) * eta_t
        
        # 5. Efficiency
        w_net = w_turbine - w_pump
        q_in = h3 - h2
        
        if q_in > 0 and w_net > 0:
            return (w_net / q_in) * 100
        else:
            return None
            
    except Exception:
        return None

# ==========================================
# Main Optimization Script
# ==========================================
print("Running ORC Parametric Optimization...")
print("Comparing R245fa (Legacy), R1233zd(E) (Green), and Isobutane (Hydrocarbon)...\n")

# Temperature range for Geothermal/Waste Heat: 80 C to 150 C
evap_temps = np.linspace(80, 150, 30)

fluids = {
    'R245fa': {'name': 'R245fa (Legacy, High GWP)', 'color': 'red', 'marker': 'o'},
    'R1233zd(E)': {'name': 'R1233zd(E) (Next-Gen, Low GWP)', 'color': 'green', 'marker': 's'},
    'IsoButane': {'name': 'Isobutane (Flammable, Low GWP)', 'color': 'orange', 'marker': '^'}
}

# Dictionary to store results
results = {fluid: [] for fluid in fluids}

# Calculate efficiencies
for T in evap_temps:
    for fluid_id in fluids:
        eff = calculate_orc_efficiency(fluid_id, T)
        results[fluid_id].append(eff)

# ==========================================
# Plotting the Results
# ==========================================
plt.figure(figsize=(10, 6))

for fluid_id, props in fluids.items():
    plt.plot(evap_temps, results[fluid_id], 
             label=props['name'], 
             color=props['color'], 
             marker=props['marker'], 
             markevery=4, 
             linewidth=2)

plt.title('ORC Thermal Efficiency vs Evaporator Temperature (T_cond = 35 C)', fontsize=14)
plt.xlabel('Evaporator Temperature (C)', fontsize=12)
plt.ylabel('Thermal Efficiency (%)', fontsize=12)
plt.grid(linestyle='--', alpha=0.7)
plt.legend(fontsize=11)
plt.tight_layout()

print("Optimization complete. Displaying efficiency curves...")
plt.show()
