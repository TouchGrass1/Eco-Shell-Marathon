import json
import numpy as np

# Load Constants
with open('consts.json', 'r') as f:
    config = json.load(f)

# Mock LUTs for VOCV and R_int based on SOC (ignoring T for simplicity in this 1D interpolation)
soc_points = np.linspace(0, 1, 11) # as a % of battery left
vocv_points = np.array([3.0, 3.2, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 4.2])
rint_points = np.array([0.05, 0.04, 0.03, 0.02, 0.015, 0.015, 0.015, 0.015, 0.015, 0.018, 0.02])


def get_vocv(soc):
    return np.interp(soc, soc_points, vocv_points)

def get_rint(soc):
    return np.interp(soc, soc_points, rint_points)

class BatterySim:
    def __init__(self, config):
        self.cfg = config

        # Initial States
        self.soc_cc = self.cfg['SOC_initial'] # Coulomb counting SOC
        self.temp_K = self.cfg['T_initial_K']
        self.Capacity_As = self.cfg['Capacity_Ah'] * 3600 #convert into seconds

    def step(self, I_actual):
            #I_actual: Current drawn (Amps). Positive = discharge.
            dt = self.cfg['dt_s']

            I_eff = I_actual * (abs(I_actual) ** (self.cfg['peukert_k'] - 1)) #Effective current cuz batteries wierd icl
            delta_soc = (self.cfg['efficiency'] * I_eff * dt) / self.Capacity_As
            self.soc_cc -= delta_soc # Love some numerical "integration"

            # When the battery is a perfect voltage source (very realisitc, good physics assumptions)
            vocv = get_vocv(self.soc_cc) # Resting voltage when no load
            r_int = get_rint(self.soc_cc) #Internal resistance,
            v_term = vocv - (I_actual * r_int) #actual terminal voltage delivered to the motor controller.

            # This crazy formula
            q_gen_vol = (1 / self.cfg['V_b_m3']) * (I_actual * (vocv - v_term) - I_actual * self.temp_K * self.cfg['dE_dT_V_K'])

            total_heat_gen_W = q_gen_vol * self.cfg['V_b_m3']
            q_cool_W = self.cfg['cooling_coeff_W_K'] * (self.temp_K - self.cfg['T_ambient_K'])

            delta_T = ((total_heat_gen_W - q_cool_W) / (self.cfg['mass_kg'] * self.cfg['cp_J_kg_K'])) * dt
            self.temp_K += delta_T

            return v_term

# The experiment, is coasting better or worse for the battery???
def run_simulation(strategy_name, current_profile, dt):
    sim = BatterySim(config)
    total_energy_delivered_Joules = 0

    for I_actual in current_profile:
        v_term = sim.step(I_actual)
        # Energy (Joules) = Power (Watts) * Time (Seconds) = V * I * dt
        total_energy_delivered_Joules += v_term * I_actual * dt

    print(f"--- Strategy: {strategy_name} ---")
    print(f"Total Energy Delivered: {total_energy_delivered_Joules:.2f} Joules")
    print(f"Remaining SOC:          {sim.soc_cc * 100:.2f}%")
    print(f"Final Temperature:      {sim.temp_K - 273.15:.2f} °C\n")


constant_profile = [2.0] * 1000
coasting_profile = ([10.0] * 200) + ([0.0] * 800) #BOth pull same current

run_simulation("Constant Current (Steady Speed)", constant_profile, config['dt_s'])
run_simulation("Coasting (fast then no throttle)", coasting_profile, config['dt_s'])
