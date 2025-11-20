# Carbon Price Scenario Analysis

This script runs the brownfield capacity expansion model across multiple carbon price scenarios and generates plots showing how coal generation and the overall generation mix respond to carbon pricing.

## Usage

### Basic Usage

Run with default carbon prices ($0, $25, $50, $75, $100, $150, $200/ton):

```bash
python run_carbon_scenarios.py
```

### Custom Carbon Prices

Specify your own carbon prices as command-line arguments:

```bash
# Test specific prices
python run_carbon_scenarios.py 0 50 100 200

# Test high carbon prices
python run_carbon_scenarios.py 100 150 200 250 300

# Fine-grained analysis
python run_carbon_scenarios.py 0 10 20 30 40 50 60 70 80 90 100
```

## Outputs

The script generates:

### 1. CSV Files

**`coal_analysis.csv`**
- Carbon price tested
- Coal capacity (MW)
- Coal generation (GWh)
- Total system cost ($)
- Total CO2 emissions (tons)

**`generation_mix_analysis.csv`**
- Detailed generation mix by fuel type for each carbon price
- Capacity and generation data for all fuel types

### 2. Plots (saved in `plots/` directory)

1. **`coal_capacity_vs_carbon_price.png`**
   - Shows how coal capacity changes with carbon price
   - X-axis: Carbon price ($/ton)
   - Y-axis: Coal capacity (MW)

2. **`coal_generation_vs_carbon_price.png`**
   - Shows how coal generation responds to carbon pricing
   - X-axis: Carbon price ($/ton)
   - Y-axis: Coal generation (GWh)
   - **Key finding**: Sharp drop in coal generation as carbon price increases

3. **`co2_emissions_vs_carbon_price.png`**
   - Shows total CO2 emissions vs carbon price
   - X-axis: Carbon price ($/ton)
   - Y-axis: Total CO2 emissions (Million tons)

4. **`generation_mix_by_carbon_price.png`**
   - Stacked bar chart showing generation by fuel type
   - X-axis: Carbon price ($/ton)
   - Y-axis: Generation (GWh)
   - Colors: Each fuel type has a distinct color

5. **`generation_mix_percentage.png`**
   - Stacked area chart showing generation mix as percentages
   - X-axis: Carbon price ($/ton)
   - Y-axis: Generation mix (%)

6. **`coal_vs_renewables.png`**
   - Dual-axis plot comparing coal and renewable generation
   - Left axis: Coal generation (brown line)
   - Right axis: Renewable generation (green line)
   - **Key finding**: Shows the trade-off between coal and renewables

## Key Results (10-day model, Zone 2)

Based on the default scenario analysis:

| Carbon Price | Coal Generation | CO2 Emissions | Change from Baseline |
|-------------|-----------------|---------------|---------------------|
| $0/ton      | 3,256 GWh      | 6.05 M tons   | baseline            |
| $25/ton     | 639 GWh        | 4.37 M tons   | -80% coal, -28% CO2 |
| $50/ton     | 116 GWh        | 3.61 M tons   | -96% coal, -40% CO2 |
| $75/ton     | 102 GWh        | 3.60 M tons   | -97% coal, -40% CO2 |
| $100+/ton   | 102 GWh        | 3.60 M tons   | -97% coal, -40% CO2 |

### Key Insights

1. **Steep Coal Decline**: Coal generation drops 80% with just $25/ton carbon price
2. **Diminishing Returns**: Beyond $50/ton, additional carbon pricing has minimal effect
3. **Technology Constraint**: Can't eliminate coal entirely due to system reliability needs
4. **Gas Substitution**: Natural gas replaces most coal generation, not renewables (in this short 10-day model)
5. **CO2 Floor**: Emissions stabilize at ~3.6M tons due to gas-fired generation

## Customization

To analyze different scenarios, edit the configuration in `run_carbon_scenarios.py`:

```python
# config
data_folder = "./ercot_brownfield_expansion/10_days"  # or 4_weeks, 52_weeks
zone = 2  # 1=ERC_P, 2=ERC_R, 3=ERC_W
solver = 'glpk'
carbon_prices = [0, 25, 50, 75, 100, 150, 200]  # $/ton CO2
```

## Requirements

```bash
pip install pandas numpy matplotlib
```

(Already installed if you set up the main model)

## Plot Customization

Colors for fuel types are defined in the `plot_results()` function:

```python
colors = {
    'Coal': '#654321',
    'Natural Gas': '#4682B4',
    'Nuclear': '#FF6347',
    'Wind': '#90EE90',
    'Solar': '#FFD700',
    'Hydro': '#4169E1',
    'Other': '#808080'
}
```

Modify these to change plot colors or add new fuel types.

## For Academic/Research Use

### Suggested Analysis

1. **Sensitivity Analysis**: Run fine-grained carbon prices (0-200 in steps of 10)
2. **Long-term Planning**: Use 52_weeks data for annual planning
3. **Multi-zone Comparison**: Run analysis for all three ERCOT zones
4. **Policy Scenarios**: Compare California ($40-50), EU ($65-100), and EPA SCC ($190)

### Citation of Results

When presenting results, note:
- Model type: Brownfield capacity expansion (existing + new capacity)
- Time horizon: 10 days / 4 weeks / 52 weeks
- Geographic scope: ERCOT Zone [zone name]
- Carbon prices tested: List range

Example:
> "A brownfield capacity expansion model was run for ERCOT Zone R across carbon prices ranging from $0-200/ton CO2. Results show coal generation drops 96% at $50/ton (comparable to California's cap-and-trade price), primarily replaced by natural gas combined cycle plants."

## Troubleshooting

**Problem**: Plots not generated
```
ModuleNotFoundError: No module named 'matplotlib'
```
**Solution**: `pip install matplotlib`

**Problem**: No results files
```
FileNotFoundError: results_zone2.csv
```
**Solution**: Make sure `simple_brownfield_model.py` is in the same directory

**Problem**: Long runtime
**Solution**: Use 10_days data instead of 52_weeks for faster analysis

---

*Part of the ERCOT Brownfield Capacity Expansion Model*
