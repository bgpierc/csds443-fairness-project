# Carbon Pricing Reference Guide

This document provides realistic carbon price ranges for capacity expansion modeling, based on actual implemented policies and social cost of carbon estimates as of 2024-2025.

## Current Carbon Prices (2024-2025)

### United States

#### California Cap-and-Trade System
- **2024**: ~$42/ton CO2
- **2025 (projected)**: ~$46/ton CO2
- **2023**: $34/ton CO2
- **Range**: $40-48/ton

**Source**: BloombergNEF Global Carbon Market Outlook 2024

#### Social Cost of Carbon (US Federal Government)
The social cost of carbon (SCC) represents the economic damages from one additional ton of CO2 emissions.

**Biden Administration EPA (2023-2024)**:
- **Central estimate**: $190/ton (for year 2020 emissions)
- **2023**: $204/ton
- **2030 (projected)**: $230/ton
- **2050 (projected)**: $308/ton
- **Range by discount rate**: $120-340/ton (using 1.5-2.5% discount rates)

**Previous interim value (2021-2023)**: $51/ton

**Sources**:
- EPA final rules (December 2023)
- Senator Whitehouse press release on EPA methane rule
- Brookings Institution analysis

**Note**: As of March 2025, the current EPA administration is revisiting these values.

### European Union

#### EU ETS (Emissions Trading System)
- **2024 average**: €65.22 ($71/ton)
- **April 2024**: >$60/ton
- **Peak (early 2023)**: €100/ton ($109/ton)
- **Recent range**: €60-100/ton ($65-109/ton)

**Source**: I4CE Global Carbon Accounts 2025, Statista

#### EU Carbon Taxes
Individual countries in Europe levy carbon taxes:
- **Switzerland/Liechtenstein**: €120 ($131/ton) - *highest*
- **Sweden**: €115 ($125/ton)
- **Norway**: €83 ($91/ton)
- **23 European countries** have carbon taxes ranging from <€1 to >€125/ton

**Source**: Tax Foundation Europe, Carbon Taxes in Europe 2024

### Global Range
- **Minimum**: $0.10/ton (some developing countries)
- **Maximum**: $160/ton (Switzerland carbon tax)
- **Typical range**: $20-100/ton

**Source**: I4CE Global Carbon Accounts 2025

## Recommended Values for Modeling

### Conservative/Current Policy Scenario
Use prices reflecting actual implemented carbon markets:
- **Low**: $0/ton (no carbon price - baseline)
- **Medium**: $40-50/ton (California, moderate EU ETS)
- **High**: $80-100/ton (High EU ETS, Nordic carbon taxes)

### Social Cost of Carbon Scenarios
Use values reflecting economic damages:
- **Low (historical)**: $51/ton (Biden interim 2021-2023)
- **Medium**: $100-150/ton (middle ground)
- **High**: $190-230/ton (EPA 2023 central estimate)
- **Very High**: $300+/ton (long-term projections, stringent climate goals)

### Climate Ambition Scenarios
For exploring deep decarbonization:
- **2030 Paris goals**: $50-100/ton
- **2050 Net Zero**: $150-300/ton
- **1.5°C pathway**: $200-500/ton (some models suggest even higher)

## Your Model Results Context

Based on your ERCOT model results, here's how different prices compare:

| Your Model | Real-World Equivalent | Policy Context |
|-----------|----------------------|----------------|
| $0/ton | No carbon pricing | Texas (current), most of US |
| $25/ton | Below California | Modest carbon fee proposals |
| $50/ton | California 2025 | Moderate carbon pricing |
| $100/ton | High EU ETS | Strong carbon policy |
| $200/ton | EPA social cost | Economic damage estimate |

## Key Insights for Your Analysis

1. **$40-50/ton** is realistic for current/near-term US policy scenarios (matches California)
2. **$190-230/ton** represents EPA's estimate of actual climate damages
3. **€60-100/ton ($65-109)** is the current EU carbon market price
4. **$100-150/ton** is a reasonable "medium ambition" scenario for modeling

## Sources

1. **BloombergNEF**: Global Carbon Market Outlook 2024
   - California cap-and-trade projections

2. **EPA**: Final Methane Rule (December 2023)
   - Social cost of carbon: $190/ton

3. **I4CE (Institute for Climate Economics)**: Global Carbon Accounts 2025
   - Comprehensive global carbon price data

4. **Tax Foundation Europe**: Carbon Taxes in Europe 2024-2025
   - Individual country carbon tax rates

5. **Statista**: Global carbon prices by jurisdiction 2024
   - EU ETS pricing data

6. **Senator Whitehouse Press Release**: EPA Rule announcement
   - Confirms $190/ton social cost of carbon codification

7. **Brookings Institution**: Social Cost of Carbon explainers
   - Context and methodology

## Citation Recommendation

For academic work, you might cite:
> "Carbon prices modeled range from $0/ton (no policy) to $200/ton, reflecting current market prices ($40-100/ton in California and EU ETS) and social cost estimates ($190/ton, EPA 2023) for economic damages from CO2 emissions."

---

*Last updated: January 2025*
*Note: Carbon prices are dynamic and vary by jurisdiction. Check current sources for the most up-to-date values.*
