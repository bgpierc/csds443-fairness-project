# csds443-fairness-project

## Simple Brownfield Capacity Expansion Model for ERCOT

A minimal working example of a brownfield capacity expansion model for the Texas ERCOT power grid using Python and Pyomo.

### Overview

This model optimizes electricity generation capacity decisions to meet demand at minimum cost. It includes:

- **Existing generators** (thermal, nuclear, wind, solar, hydro) that can continue operating
- **New generation options** that can be built
- **Hourly demand** that must be met across 240 hours (10 days), 672 hours (4 weeks), or full year
- **Variable generation costs** based on fuel prices and heat rates
- **Fixed O&M costs** for maintaining capacity
- **Capacity factors** for variable renewable energy (wind/solar)

The model decides how much new capacity to build while minimizing total system cost.

### Installation

**Requirements:**

```bash
# Install Python packages
pip install pyomo pandas numpy

# Install GLPK solver (on macOS)
brew install glpk

# Or on Ubuntu/Debian
# sudo apt-get install glpk-utils
```

### Usage

**Basic Usage:**

Run the model with default settings (10 days of data, Zone 2 - ERC_R):

```bash
python simple_brownfield_model.py
```

**Custom Configuration:**

```bash
python simple_brownfield_model.py [data_folder] [zone] [solver] [carbon_price]
```

Parameters:
- `data_folder`: Path to ERCOT data folder (default: `./ercot_brownfield_expansion/10_days`)
- `zone`: ERCOT zone number (1=Panhandle, 2=Rest, 3=West, default: 2)
- `solver`: Optimization solver (glpk, highs, cbc, gurobi, default: glpk)
- `carbon_price`: Carbon tax in $/ton CO2 (default: 0, no carbon tax)

Examples:

```bash
# Run 4 weeks of data for Zone 2
python simple_brownfield_model.py ./ercot_brownfield_expansion/4_weeks 2 glpk

# Run 10 days for Zone 3 (West)
python simple_brownfield_model.py ./ercot_brownfield_expansion/10_days 3 glpk

# Run with $50/ton carbon price to incentivize clean energy
python simple_brownfield_model.py ./ercot_brownfield_expansion/10_days 2 glpk 50

# Run with $100/ton carbon price
python simple_brownfield_model.py ./ercot_brownfield_expansion/10_days 2 glpk 100
```

### Output

The model produces:

1. **Console output** showing:
   - Total system cost ($)
   - Total CO2 emissions (tons)
   - New capacity built by generator type (MW)
   - Generation mix (top 10 generators)

2. **CSV file** (`results_zone{N}.csv`) with detailed capacity and generation data

### Example Results

**No Carbon Price ($0/ton):**
```
Total System Cost: $2,591,438,708
Total CO2 Emissions: 6,050,439 tons

New Capacity: 25,419 MW natural gas combustion turbines

Generation Mix:
    natural_gas_fired_combined_cycle     5,888 GWh    (51%)
             conventional_steam_coal     3,256 GWh    (28%)
                             nuclear     1,205 GWh    (10%)
```

**With $50/ton Carbon Price:**
```
Total System Cost: $2,819,572,037
Total CO2 emissions: 3,606,976 tons (40% reduction!)

New Capacity: 25,419 MW cleaner natural gas combined cycle

Generation Mix:
           naturalgas_ccavgcf (new CC)     6,096 GWh    (53%)
    natural_gas_fired_combined_cycle     3,414 GWh    (30%)
                             nuclear     1,205 GWh    (10%)
                               wind       493 GWh     (4%)
```

The carbon price shifts investment from dirty coal and peaking turbines to cleaner combined cycle plants, reducing emissions by 40% while meeting the same demand.

### Model Details

**Decision Variables:**
- `CAP[g]` - New capacity to build (MW)
- `GEN[g,t]` - Generation at each hour (MWh)

**Objective:** Minimize total system cost (fixed O&M + variable generation costs + carbon emissions cost)

**Constraints:**
- Demand balance each hour
- Generation limited by available capacity
- VRE generation limited by capacity factors

**Simplifications** (this is a minimal model):
- No storage/batteries
- No transmission constraints
- No unit commitment
- Only fixed O&M costs (no capital costs for new builds)