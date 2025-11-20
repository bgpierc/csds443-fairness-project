# Why Doesn't the Model Install More Solar?

Great question! The model's lack of solar investment doesn't match real-world trends where solar is the fastest-growing electricity source. Here's why:

## TL;DR - The Main Issues

1. **Missing capital costs** - Model only includes O&M, not upfront investment
2. **No tax incentives** - ITC/PTC subsidies not modeled
3. **No storage** - Can't shift solar to evening peak
4. **Short time horizon** - 10 days vs 20-30 year real projects
5. **No renewable mandates** - RPS requirements not included
6. **Fixed fuel prices** - Misses gas price volatility risk

## Economic Comparison (What the Model Sees)

### Solar PV (utility scale)
- **Fixed O&M**: $12,603/MW-yr
- **Variable cost**: $0/MWh (no fuel!)
- **Capacity factor**: 21.6% (only generates during day)
- **Levelized cost**: $6.68/MWh from fixed costs
- **Total**: ~$7/MWh (very cheap!)

### Natural Gas Combined Cycle
- **Fixed O&M**: $10,463/MW-yr (20% LOWER than solar!)
- **Variable cost**: $24.36/MWh (fuel + O&M)
- **Capacity factor**: Can run 24/7 at 100%
- **Dispatchable**: Available whenever needed

### Why Gas Wins in the Model
Even though solar has zero fuel cost, gas has:
- ✅ **Lower fixed costs** ($10k vs $13k per MW-yr)
- ✅ **Full dispatchability** (100% vs 22% capacity factor)
- ✅ **Reliability for peaks** (solar only 52% during peak hours)

**Result**: Gas is cheaper on an annual basis when you only count O&M!

## What's Missing? Capital Costs!

### Real-World Capital Costs (2025)

| Technology | Capital Cost | Annual O&M | Total 1st Year |
|-----------|--------------|------------|----------------|
| **Solar PV** | $1,000,000/MW | $12,603/MW | $1,012,603/MW |
| **Gas CC** | $950,000/MW | $10,463/MW | $960,463/MW |
| **Gas CT** | $750,000/MW | $7,143/MW | $757,143/MW |

When you include capital costs:
- Solar and gas CC are roughly **equal** in upfront cost
- But solar has **zero fuel cost** over 30 years
- Gas accumulates $22/MWh × 8,760 hrs × 30 years = **$5.8M/MW** in fuel costs!

### Why Your Model Doesn't See This

Your model uses the `Inv_cost_per_MWyr` field from the data, but let's check if it's being used:

```python
# In simple_brownfield_model.py, objective function:
fixed_new = sum(FixedCost[g] * m.CAP[g] for g in m.NEW)
```

This only uses `Fixed_OM_cost_per_MWyr`, **NOT** `Inv_cost_per_MWyr` (the investment/capital cost field)!

Let's check the data:

```bash
$ csvcut -c Resource,Inv_cost_per_MWyr,Fixed_OM_cost_per_MWyr Generators_data.csv | grep -E "utilitypv|naturalgas_cc"

utilitypv_losangeles,156892,12603
naturalgas_ccavgcf,76983,10463
```

**The capital costs ARE in the data!**
- Solar: $156,892/MW-yr (amortized)
- Gas CC: $76,983/MW-yr (amortized)

If you included these, solar would be less attractive initially, but the model would also need to account for the 20+ year lifetime where solar has zero fuel cost.

## Real-World Factors Driving Solar Growth

### 1. Tax Incentives (30-50% of capital cost!)

**Investment Tax Credit (ITC)**:
- Solar gets 30% federal tax credit
- Effectively reduces capital cost from $1M to $700k per MW
- **Not modeled**

**Production Tax Credit (PTC)**:
- Wind gets ~$27/MWh for 10 years
- **Not modeled**

### 2. Fuel Price Risk

Historical natural gas prices:
- 2020: $2/MMBtu (COVID crash)
- 2022: $9/MMBtu (Russia-Ukraine war)
- 2025: $3.62/MMBtu (current)

Your model uses **fixed** $3.62/MMBtu. Real investors worry about:
- 30-year fuel cost uncertainty
- Carbon regulation risk
- Supply disruptions

Solar = **zero fuel price risk** forever

### 3. Renewable Portfolio Standards (RPS)

Many states require X% renewable energy:
- California: 60% by 2030
- Texas: ~25% renewable energy goal
- Federal clean energy standards proposed

Your model has **no renewable mandate constraint**.

### 4. Battery Storage Pairing

Reality: Solar + batteries can store midday sun for evening peak
- Battery costs dropped 90% since 2010
- Now ~$300-400/kWh
- Solar+storage beats peaker plants

Your model: **Storage excluded** (STOR generators filtered out)

### 5. Corporate Power Purchase Agreements (PPAs)

Major trend: Companies signing 20-year fixed-price solar contracts
- Google, Amazon, Microsoft, etc.
- Guaranteed revenue reduces financing costs
- Makes solar more bankable

Your model: **Short-term spot pricing** (10 days)

### 6. Declining Solar Costs

Solar capital costs fell:
- 2010: $5,000/kW
- 2015: $2,000/kW
- 2020: $1,000/kW
- 2025: $800-1,000/kW

Your model: Uses current costs but doesn't reflect the **dramatic cost decline trajectory**

## How to Make the Model More Realistic

### Option 1: Add Investment Costs (Simple)

Modify the objective function in `simple_brownfield_model.py`:

```python
# current (line ~131):
fixed_new = sum(FixedCost[g] * m.CAP[g] for g in m.NEW)

# change to:
InvCost = gens['Inv_cost_per_MWyr'].to_dict()
fixed_new = sum((FixedCost[g] + InvCost[g]) * m.CAP[g] for g in m.NEW)
```

This would make solar much more expensive initially (but still no fuel costs).

### Option 2: Add Renewable Energy Mandate

Add a constraint requiring X% of generation from renewables:

```python
def renewable_mandate_rule(m):
    renewable_gen = sum(m.GEN[g, t] for g in m.VRE for t in m.T)
    total_gen = sum(m.GEN[g, t] for g in m.G for t in m.T)
    return renewable_gen >= 0.30 * total_gen  # 30% renewable

model.cRPS = pyo.Constraint(rule=renewable_mandate_rule)
```

### Option 3: Add Tax Credit for Solar

Reduce solar costs by 30% to reflect ITC:

```python
# when calculating costs for solar
if 'solar' in resource_name or 'pv' in resource_name:
    InvCost[g] = InvCost[g] * 0.70  # 30% ITC
```

### Option 4: Include Storage

Allow solar + battery combinations (more complex, would need charge/discharge constraints)

### Option 5: Use Longer Time Horizon

Run the 52_weeks dataset instead of 10_days:
- Better captures seasonal patterns
- More realistic for long-term investment
- Solar's zero fuel cost accumulates over time

## Testing: What Happens with High Carbon Prices?

You already tested this! At $200/ton CO2:
- Gas CC total cost: $24.36/MWh + $200 × 0.296 tons/MWh = **$83.56/MWh**
- Solar total cost: $6.68/MWh + $0 carbon = **$6.68/MWh**

Solar is **12x cheaper** at high carbon prices, yet model still doesn't build it!

**Why?** Because:
1. Model needs **reliable capacity** for peaks (solar only 52% at peak)
2. 10-day horizon doesn't show long-term fuel cost savings
3. Gas has lower fixed O&M, so cheaper to build initially

## Conclusion

Your model is technically correct for its assumptions (10-day horizon, O&M costs only, no subsidies, no mandates), but **misses key real-world drivers**:

| Factor | Real World | Your Model |
|--------|-----------|------------|
| Capital costs | Critical | Excluded |
| Tax credits | 30% subsidy | Not modeled |
| Fuel risk | Major concern | Fixed prices |
| Storage | Enables solar | Excluded |
| RPS mandates | Common | Not modeled |
| Time horizon | 20-30 years | 10 days |
| PPAs | Common | Spot pricing |

**Real-world solar growth driven by**:
- ✅ 90% cost decline (2010-2025)
- ✅ 30% federal tax credit
- ✅ Zero fuel cost over 30 years
- ✅ Battery pairing for dispatchability
- ✅ State renewable mandates
- ✅ Corporate sustainability goals

**Your model shows**:
- ✅ Gas cheaper on annual O&M basis
- ✅ Gas fully dispatchable
- ✅ Solar limited by capacity factor
- ❌ Misses 30-year fuel savings
- ❌ No subsidies
- ❌ No mandates

## Recommended Next Steps

1. **Add investment costs** to objective function
2. **Test 52_weeks** dataset for longer horizon
3. **Add renewable mandate** constraint (e.g., 30% requirement)
4. **Reduce solar cost by 30%** to reflect ITC
5. **Include battery storage** as complement to solar
6. **Model fuel price uncertainty** with scenarios

This would make your model match industry trends much better!

---

*This is a feature, not a bug - your model is revealing what happens when you strip away policy incentives and long-term considerations. It shows that solar growth is driven by policy and long-term economics, not just short-term operational costs.*
