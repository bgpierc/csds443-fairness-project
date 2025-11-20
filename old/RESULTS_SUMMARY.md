# Carbon Price Analysis Results Summary

## Quick Results (10-day ERCOT Zone 2 Model)

### Coal Generation Response to Carbon Pricing

| Carbon Price | Coal Generation | % Change | CO2 Emissions | % Change | System Cost | % Change |
|-------------|-----------------|----------|---------------|----------|-------------|----------|
| **$0/ton**  | 3,256 GWh      | baseline | 6.05 M tons   | baseline | $2.59B      | baseline |
| **$25/ton** | 639 GWh        | **-80%** | 4.37 M tons   | **-28%** | $2.72B      | +5%      |
| **$50/ton** | 116 GWh        | **-96%** | 3.61 M tons   | **-40%** | $2.82B      | +9%      |
| **$75/ton** | 102 GWh        | **-97%** | 3.60 M tons   | **-40%** | $2.91B      | +12%     |
| **$100/ton**| 102 GWh        | **-97%** | 3.60 M tons   | **-40%** | $3.00B      | +16%     |
| **$150/ton**| 102 GWh        | **-97%** | 3.60 M tons   | **-40%** | $3.18B      | +23%     |
| **$200/ton**| 102 GWh        | **-97%** | 3.60 M tons   | **-40%** | $3.36B      | +30%     |

## Key Findings

### 1. Steep Coal Decline at Low Carbon Prices
- **$25/ton**: Coal generation drops 80% (from 3,256 to 639 GWh)
- **$50/ton**: Coal generation drops 96% (from 3,256 to 116 GWh)
- This is consistent with real-world observations where modest carbon prices have large impacts on coal

### 2. Diminishing Returns Beyond $50/ton
- Coal generation stabilizes at ~102 GWh for all prices ≥$75/ton
- CO2 emissions stabilize at ~3.6M tons
- System can't fully eliminate coal in this 10-day model (reliability/peak demand needs)

### 3. Cost vs. Environmental Trade-off
- To achieve a 40% CO2 reduction requires 9-30% cost increase (depending on carbon price)
- Most emissions reductions occur between $0-50/ton carbon price
- Higher carbon prices mainly increase costs without additional emissions reductions

### 4. What Replaces Coal?
Based on the generation mix analysis:
- **Natural gas combined cycle** is the primary coal replacement
- Gas plants have ~50% lower CO2 emissions than coal
- Existing renewable capacity (wind/solar) is fully utilized but limited
- Model builds cleaner gas plants instead of peakers at higher carbon prices

## Comparison to Real-World Carbon Prices

| Jurisdiction | Carbon Price | Our Model Result |
|--------------|-------------|------------------|
| California (2025) | $46/ton | 96% coal reduction, 40% CO2 reduction |
| EU ETS (2024) | $65-100/ton | Minimal additional benefit beyond $50/ton |
| EPA Social Cost (2023) | $190/ton | No additional emissions reductions, but 30% higher costs |

### Implications
- **California's carbon price** ($40-50/ton) is highly effective at reducing coal
- **EU's higher prices** don't achieve much more in this model (gas becomes dominant)
- **EPA's $190/ton** reflects damages, not optimal policy price for this system
- To achieve deeper decarbonization, would need:
  - More renewable capacity options
  - Energy storage
  - Transmission expansion
  - Longer time horizons for investment

## Technical Notes

**Coal Capacity vs Generation**:
- Coal capacity stays constant at 13,568 MW (no retirements in 10-day model)
- Coal *generation* drops dramatically (utilization falls from 24% to 1%)
- Coal plants kept for reliability but rarely dispatch

**Why No New Renewables?**:
This 10-day model has limited renewable capacity options:
- Existing wind: 6,979 MW (fully utilized at all carbon prices)
- Existing solar: 455 MW (fully utilized at all carbon prices)
- New renewable options available but not cost-effective vs. cleaner gas
- Longer time horizons (52_weeks) would show more renewable investment

**Model Limitations**:
- 10 days may not capture seasonal renewable variability
- No energy storage modeled
- No transmission constraints
- Fixed O&M costs only (no capital costs for new builds)
- Single zone (doesn't model inter-zone trade)

## Visualizations Generated

The analysis script creates 6 plots in the `plots/` directory:

1. **coal_capacity_vs_carbon_price.png** - Shows coal capacity (stays constant)
2. **coal_generation_vs_carbon_price.png** - Shows sharp drop in coal generation
3. **co2_emissions_vs_carbon_price.png** - Shows emissions reduction curve
4. **generation_mix_by_carbon_price.png** - Stacked bars showing fuel mix
5. **generation_mix_percentage.png** - Percentage breakdown by fuel type
6. **coal_vs_renewables.png** - Dual-axis showing coal decline vs renewable generation

## How to Reproduce

```bash
# Run the analysis
python run_carbon_scenarios.py

# View results
cat coal_analysis.csv
cat generation_mix_analysis.csv

# Open plots
./view_plots.sh  # or manually open files in plots/ directory
```

## Recommendations for Further Analysis

1. **Run 52-week model** for longer-term capacity planning
2. **Test all three zones** to see regional differences
3. **Add storage constraints** to enable more renewable integration
4. **Model capital costs** for new builds (currently only fixed O&M)
5. **Test very high carbon prices** ($300-500/ton) to explore deep decarbonization
6. **Compare with renewable subsidies** (PTC/ITC) instead of carbon pricing

---

*Generated from ERCOT Brownfield Capacity Expansion Model*
*Data: 10-day sample, Zone 2 (ERC_R - Rest of Texas)*
*Carbon prices tested: $0, $25, $50, $75, $100, $150, $200 per ton CO2*
