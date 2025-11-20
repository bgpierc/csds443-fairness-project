"""
Simple Brownfield Capacity Expansion Model for ERCOT
======================================================

This script implements a minimal capacity expansion optimization model
for the ERCOT power grid. It decides how much new generation capacity
to build while meeting electricity demand at minimum cost.

Model Features:
- Existing generators (can be retired if old)
- New generator options (can be built)
- Hourly demand that must be met
- Variable generation costs
- Fixed O&M costs for capacity
"""

import pyomo.environ as pyo
from pyomo.opt import SolverFactory
import pandas as pd
import numpy as np
import sys


def load_ercot_data(data_folder):
    print(f"\nLoading data from {data_folder}...")

    demand = pd.read_csv(f"{data_folder}/Load_data.csv")
    gens = pd.read_csv(f"{data_folder}/Generators_data.csv")
    fuels = pd.read_csv(f"{data_folder}/Fuels_data.csv")
    gen_cf = pd.read_csv(f"{data_folder}/Generators_variability.csv")

    return demand, gens, fuels, gen_cf


def calculate_variable_costs(gens, fuels):
    gens = gens.merge(fuels[['Fuel', 'Cost_per_MMBtu', 'CO2_content_tons_per_MMBtu']], on='Fuel', how='left')
    # Variable cost = Heat rate (MMBTU/MWh) × Fuel cost ($/MMBTU) + Var O&M ($/MWh)
    gens['Var_Cost'] = (
        gens['Heat_rate_MMBTU_per_MWh'].fillna(0) *
        gens['Cost_per_MMBtu'].fillna(0) +
        gens['Var_OM_cost_per_MWh'].fillna(0)
    )
    # carbon emissions = heat rate (MMBTU/MWh) × CO2 content (tons/MMBTU)
    gens['CO2_tons_per_MWh'] = (
        gens['Heat_rate_MMBTU_per_MWh'].fillna(0) *
        gens['CO2_content_tons_per_MMBtu'].fillna(0)
    )
    return gens


def build_capacity_expansion_model(gens, demand_zone, gen_cf_zone, carbon_price=0, zone_name="All Zones"):
    """
    Build and solve a capacity expansion optimization model.

    Decision Variables:
        CAP[g] - New capacity to build for generator g (MW)
        RET[g] - Capacity to retire for old generator g (MW)
        GEN[g,t] - Generation from generator g at time t (MWh)
        NSE[t] - Non-served energy (load shedding) at time t (MWh)

    Objective:
        Minimize total system cost = Fixed O&M + Variable generation costs + Load shedding penalty

    Constraints:
        - Supply must meet demand each hour
        - Generation cannot exceed available capacity (accounting for capacity factors)
        - Retirements cannot exceed existing capacity
    """
    model = pyo.ConcreteModel(name="ERCOT_Brownfield_Expansion")

    model.G = pyo.Set(initialize=gens.index.tolist())  # All generators
    model.T = pyo.Set(initialize=range(len(demand_zone)))  # Time periods

    # Categorize generators
    # OLD: Can be retired (like old combined cycle or combustion turbine plants)
    # NEW: Can be built (have New_Build = 1)
    # THERM: Thermal generators (not variable renewable energy)
    # VRE: Variable renewable energy (wind, solar)

    OLD = gens[gens['Resource'].str.contains('Old', na=False)].index.tolist()
    NEW = gens[gens['New_Build'] == 1].index.tolist()
    THERM = gens[gens['THERM'] == 1].index.tolist()
    # VRE = Variable renewable energy with capacity factors (wind, solar)
    # these have DISP==1 (dispatchable with variability) and NDISP==0
    VRE = gens[(gens['DISP'] == 1) & (gens['THERM'] == 0)].index.tolist()
    # NDISP = Non-dispatchable renewables that must-run with capacity factors
    NDISP = gens[gens['NDISP'] == 1].index.tolist()
    # basically need to treat hydro like THERM
    HYDRO = gens[gens['HYDRO'] == 1].index.tolist()

    model.OLD = pyo.Set(initialize=OLD)
    model.NEW = pyo.Set(initialize=NEW)
    model.THERM = pyo.Set(initialize=THERM)
    model.VRE = pyo.Set(initialize=VRE)
    model.NDISP = pyo.Set(initialize=NDISP)
    model.HYDRO = pyo.Set(initialize=HYDRO)

    ExistingCap = gens['Existing_Cap_MW'].to_dict()
    FixedCost = gens['Fixed_OM_cost_per_MWyr'].to_dict()
    VarCost = gens['Var_Cost'].to_dict()
    CO2_emissions = gens['CO2_tons_per_MWh'].to_dict()

    # non-served energy penalty (v large, don't want load shedding)
    NSECost = 1e6  # $/MWh

    # Capacity factors for VRE and NDISP (wind/solar/biomass)
    cf_dict = {}
    for g in list(VRE) + list(NDISP):
        #  match by R_ID (resource ID)
        r_id = int(gens.loc[g, 'R_ID'])
        resource_name = gens.loc[g, 'Resource'].replace(' ', '_')
        col_name = f"{resource_name}_{r_id}"

        if col_name in gen_cf_zone.columns:
            cf_dict[g] = gen_cf_zone[col_name].values
        else:
            # Default to 0.3 capacity factor if not found
            print(f"  Warning: No capacity factors found for {resource_name} (ID={r_id}), using default 0.3")
            cf_dict[g] = np.full(len(demand_zone), 0.3)

    # decision variables
    # what the model actuallly changes
    model.CAP = pyo.Var(model.NEW, domain=pyo.NonNegativeReals, doc="New capacity (MW)")
    model.RET = pyo.Var(model.OLD, domain=pyo.NonNegativeReals, doc="Retired capacity (MW)")
    model.GEN = pyo.Var(model.G, model.T, domain=pyo.NonNegativeReals, doc="Generation (MWh)")
    model.NSE = pyo.Var(model.T, domain=pyo.NonNegativeReals, doc="Non-served energy (MWh)")

    # obj function
    def objective_rule(m):
        # Fixed O&M for new capacity
        fixed_new = sum(FixedCost[g] * m.CAP[g] for g in m.NEW)

        # Fixed O&M for existing capacity (minus retirements)
        fixed_existing = sum(FixedCost[g] * (ExistingCap[g] - m.RET[g]) for g in m.OLD)
        fixed_existing += sum(FixedCost[g] * ExistingCap[g] for g in m.G if g not in m.OLD and g not in m.NEW)

        #var costs
        var_cost = sum(VarCost[g] * m.GEN[g, t] for g in m.G for t in m.T)

        # carbon emissions cost ($/ton CO2)
        carbon_cost = carbon_price * sum(CO2_emissions[g] * m.GEN[g, t] for g in m.G for t in m.T)

        # nse penalty
        nse_cost = NSECost * sum(m.NSE[t] for t in m.T)

        return fixed_new + fixed_existing + var_cost + carbon_cost + nse_cost

    model.obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize, doc="Minimize total system cost")

    # some constraints

    # demand balance: generation + load shedding = demand
    def demand_balance_rule(m, t):
        return sum(m.GEN[g, t] for g in m.G) + m.NSE[t] == demand_zone.iloc[t]

    model.cDemand = pyo.Constraint(model.T, rule=demand_balance_rule,
                                    doc="Supply must meet demand")

    # capacity constraint for thermal generators
    def capacity_therm_rule(m, g, t):
        if g in m.THERM or g in m.HYDRO:
            if g in m.NEW:
                # New thermal: limited by capacity built
                return m.GEN[g, t] <= m.CAP[g]
            elif g in m.OLD:
                # Old thermal: limited by existing capacity minus retirements
                return m.GEN[g, t] <= ExistingCap[g] - m.RET[g]
            else:
                # Other existing thermal/hydro: limited by existing capacity
                return m.GEN[g, t] <= ExistingCap[g]
        return pyo.Constraint.Skip

    model.cCapTherm = pyo.Constraint(model.G, model.T, rule=capacity_therm_rule,
                                      doc="Thermal and hydro generation capacity limits")

    # capacity constraint for VRE (includes capacity factor)
    def capacity_vre_rule(m, g, t):
        if g in m.VRE or g in m.NDISP:
            cf = cf_dict.get(g, np.ones(len(demand_zone)))[t]
            if g in m.NEW:
                return m.GEN[g, t] <= m.CAP[g] * cf
            else:
                return m.GEN[g, t] <= ExistingCap[g] * cf
        return pyo.Constraint.Skip

    model.cCapVRE = pyo.Constraint(model.G, model.T, rule=capacity_vre_rule,
                                    doc="VRE and NDISP generation capacity limits")

    # retirement limit: Cannot retire more than existing capacity
    # tbh i do not think this matters, we probs won't retire anything
    def max_retirement_rule(m, g):
        return m.RET[g] <= ExistingCap[g]

    model.cMaxRet = pyo.Constraint(model.OLD, rule=max_retirement_rule,
                                    doc="Retirements limited by existing capacity")

    return model


def solve_model(model, solver_name='glpk', verbose=False):
    print(f"\nSolving with {solver_name}...")

    solver = SolverFactory(solver_name)

    if not solver.available():
        print(f"solver '{solver_name}' is not available.")
        return None

    results = solver.solve(model, tee=verbose)

    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
        print("optimal soln found")
        return results
    else:
        print(f"solver failed: {results.solver.termination_condition}")
        return results


def extract_results(model, gens):

    obj_value = pyo.value(model.obj)

    print(f"\nRESULTS\n")
    print(f"Total System Cost: ${obj_value:,.0f}")

    # calc total CO2 emissions
    total_co2 = sum(
        gens.loc[g, 'CO2_tons_per_MWh'] * sum(pyo.value(model.GEN[g, t]) for t in model.T)
        for g in model.G
    )
    print(f"Total CO2 Emissions: {total_co2:,.0f} tons")

    results = []

    for g in model.G:
        resource = gens.loc[g, 'Resource']
        region = gens.loc[g, 'region']
        existing_mw = gens.loc[g, 'Existing_Cap_MW']

        new_mw = pyo.value(model.CAP[g]) if g in model.NEW else 0
        ret_mw = pyo.value(model.RET[g]) if g in model.OLD else 0
        total_mw = existing_mw + new_mw - ret_mw

        gen_gwh = sum(pyo.value(model.GEN[g, t]) for t in model.T) / 1000

        results.append({
            'Generator': resource,
            'Region': region,
            'Existing_MW': existing_mw,
            'New_MW': new_mw,
            'Retired_MW': ret_mw,
            'Final_MW': total_mw,
            'Generation_GWh': gen_gwh
        })

    nse_gwh = sum(pyo.value(model.NSE[t]) for t in model.T) / 1000
    results.append({
        'Generator': 'Non-Served Energy',
        'Region': 'N/A',
        'Existing_MW': 0,
        'New_MW': 0,
        'Retired_MW': 0,
        'Final_MW': 0,
        'Generation_GWh': nse_gwh
    })

    df = pd.DataFrame(results)

    total_gen = df['Generation_GWh'].sum()
    df['Generation_Pct'] = (df['Generation_GWh'] / total_gen * 100).round(2)

    df = df.sort_values('Generation_GWh', ascending=False).reset_index(drop=True)

    return df, obj_value, nse_gwh


def print_summary(results_df, nse_gwh):

    # Capacity changes
    new_capacity = results_df[results_df['New_MW'] > 0]
    retired_capacity = results_df[results_df['Retired_MW'] > 0]

    if len(new_capacity) > 0:
        print(f"\nNew Capacity Built:")
        print(new_capacity[['Generator', 'Region', 'New_MW']].to_string(index=False))
        print(f"Total New: {new_capacity['New_MW'].sum():.0f} MW")
    else:
        print(f"\nNo new capacity built.")

    if len(retired_capacity) > 0:
        print(f"\nCapacity Retired:")
        print(retired_capacity[['Generator', 'Region', 'Retired_MW']].to_string(index=False))
        print(f"Total Retired: {retired_capacity['Retired_MW'].sum():.0f} MW")
    else:
        print(f"\nNo capacity retired.")

    print(f"\nGeneration Mix (top 10):")
    top_gen = results_df[results_df['Generation_GWh'] > 0].head(10)
    print(top_gen[['Generator', 'Generation_GWh', 'Generation_Pct']].to_string(index=False))

    if nse_gwh > 0.01:
        print("The system cannot meet demand, need more capacity.")


def main():

    data_folder = "./ercot_brownfield_expansion/10_days"
    zone_to_model = 2  # 1=ERC_P, 2=ERC_R, 3=ERC_W
    solver_name = 'glpk'  # Options: glpk, highs, cbc, gurobi, cplex
    carbon_price = 0  # $/ton CO2 (default = no carbon tax)

    if len(sys.argv) > 1:
        data_folder = sys.argv[1]
    if len(sys.argv) > 2:
        zone_to_model = int(sys.argv[2])
    if len(sys.argv) > 3:
        solver_name = sys.argv[3]
    if len(sys.argv) > 4:
        carbon_price = float(sys.argv[4])

    zone_names = {1: "ERC_P (Panhandle)", 2: "ERC_R (Rest)", 3: "ERC_W (West)"}

    demand, gens, fuels, gen_cf = load_ercot_data(data_folder)

    gens = calculate_variable_costs(gens, fuels)

    # filter out storage not considering dfor this model
    gens = gens[gens['STOR'] == 0].copy()

    # filter to specific zone
    gens_zone = gens[gens['zone'] == zone_to_model].copy().reset_index(drop=True)
    demand_zone = demand[f'Load_MW_z{zone_to_model}']

    # Get generator capacity factors (match by column index)
    gen_cf_zone = gen_cf

    print(f"\nCarbon price: ${carbon_price:.2f}/ton CO2")

    model = build_capacity_expansion_model(
        gens_zone,
        demand_zone,
        gen_cf_zone,
        carbon_price=carbon_price,
        zone_name=zone_names.get(zone_to_model, f"Zone {zone_to_model}")
    )

    results = solve_model(model, solver_name=solver_name, verbose=False)

    if results and results.solver.termination_condition == pyo.TerminationCondition.optimal:
        results_df, obj_value, nse_gwh = extract_results(model, gens_zone)
        print_summary(results_df, nse_gwh)

        output_file = f"results_zone{zone_to_model}.csv"
        results_df.to_csv(output_file, index=False)
        print(f"results saved to {output_file}")

        return results_df, obj_value
    else:
        print("model did not solve successfully.")
        return None, None


if __name__ == "__main__":
    main()
