"""
Run multiple carbon price scenarios and analyze results
========================================================

runs the brownfield capacity expansion model with different carbon prices
and saves results for comparison and plotting
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
import sys


def run_scenario(data_folder, zone, solver, carbon_price):
    """run model with specific carbon price and capture results"""

    print(f"\nRunning scenario: ${carbon_price}/ton CO2...")

    # run the model
    cmd = ['python', 'simple_brownfield_model.py', data_folder, str(zone), solver, str(carbon_price)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # parse output to extract key metrics
    lines = result.stdout.split('\n')

    metrics = {
        'carbon_price': carbon_price,
        'total_cost': None,
        'total_co2': None,
    }

    for line in lines:
        if 'Total System Cost:' in line:
            # extract number from "Total System Cost: $2,591,438,708"
            cost_str = line.split('$')[1].replace(',', '')
            metrics['total_cost'] = float(cost_str)
        elif 'Total CO2 Emissions:' in line:
            # extract from "Total CO2 Emissions: 6,050,439 tons"
            co2_str = line.split(':')[1].replace('tons', '').replace(',', '').strip()
            metrics['total_co2'] = float(co2_str)

    # load the detailed results CSV
    results_file = f"results_zone{zone}.csv"
    if os.path.exists(results_file):
        df = pd.read_csv(results_file)
        metrics['results_df'] = df
    else:
        metrics['results_df'] = None

    return metrics


def analyze_coal_generation(scenarios_results):
    """extract coal generation/capacity data from all scenarios"""

    coal_data = []

    for result in scenarios_results:
        carbon_price = result['carbon_price']
        df = result['results_df']

        if df is not None:
            # find coal generators
            coal_mask = df['Generator'].str.contains('coal', case=False, na=False)
            coal_gens = df[coal_mask]

            total_coal_capacity = coal_gens['Final_MW'].sum()
            total_coal_generation = coal_gens['Generation_GWh'].sum()

            coal_data.append({
                'carbon_price': carbon_price,
                'coal_capacity_MW': total_coal_capacity,
                'coal_generation_GWh': total_coal_generation,
                'total_cost': result['total_cost'],
                'total_co2': result['total_co2']
            })

    return pd.DataFrame(coal_data)


def analyze_generator_mix(scenarios_results):
    """extract generation mix by fuel type for all scenarios"""

    mix_data = []

    for result in scenarios_results:
        carbon_price = result['carbon_price']
        df = result['results_df']

        if df is not None:
            # categorize generators by fuel type
            for idx, row in df.iterrows():
                gen_name = row['Generator'].lower()

                # categorize
                if 'coal' in gen_name:
                    fuel_type = 'Coal'
                elif 'nuclear' in gen_name:
                    fuel_type = 'Nuclear'
                elif 'wind' in gen_name:
                    fuel_type = 'Wind'
                elif 'solar' in gen_name or 'pv' in gen_name:
                    fuel_type = 'Solar'
                elif 'gas' in gen_name or 'naturalgas' in gen_name:
                    fuel_type = 'Natural Gas'
                elif 'hydro' in gen_name:
                    fuel_type = 'Hydro'
                else:
                    fuel_type = 'Other'

                mix_data.append({
                    'carbon_price': carbon_price,
                    'fuel_type': fuel_type,
                    'capacity_MW': row['Final_MW'],
                    'generation_GWh': row['Generation_GWh']
                })

    return pd.DataFrame(mix_data)


def plot_results(coal_df, mix_df, output_dir='plots'):
    """create plots showing impact of carbon price"""

    os.makedirs(output_dir, exist_ok=True)

    # plot 1: coal capacity vs carbon price
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(coal_df['carbon_price'], coal_df['coal_capacity_MW'],
            marker='o', linewidth=2, markersize=8, color='#8B4513', label='Coal Capacity')
    ax.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax.set_ylabel('Coal Capacity (MW)', fontsize=12)
    ax.set_title('Coal Capacity vs Carbon Price', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/coal_capacity_vs_carbon_price.png', dpi=300)
    print(f"saved: {output_dir}/coal_capacity_vs_carbon_price.png")

    # plot 2: coal generation vs carbon price
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(coal_df['carbon_price'], coal_df['coal_generation_GWh'],
            marker='o', linewidth=2, markersize=8, color='#654321', label='Coal Generation')
    ax.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax.set_ylabel('Coal Generation (GWh)', fontsize=12)
    ax.set_title('Coal Generation vs Carbon Price', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/coal_generation_vs_carbon_price.png', dpi=300)
    print(f"saved: {output_dir}/coal_generation_vs_carbon_price.png")

    # plot 3: total CO2 emissions vs carbon price
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(coal_df['carbon_price'], coal_df['total_co2'] / 1e6,
            marker='o', linewidth=2, markersize=8, color='#DC143C', label='Total CO2')
    ax.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax.set_ylabel('Total CO2 Emissions (Million tons)', fontsize=12)
    ax.set_title('Total CO2 Emissions vs Carbon Price', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/co2_emissions_vs_carbon_price.png', dpi=300)
    print(f"saved: {output_dir}/co2_emissions_vs_carbon_price.png")

    # plot 4: generation mix by carbon price (stacked bar)
    mix_pivot = mix_df.groupby(['carbon_price', 'fuel_type'])['generation_GWh'].sum().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))

    # define colors for each fuel type
    colors = {
        'Coal': '#654321',
        'Natural Gas': '#4682B4',
        'Nuclear': '#FF6347',
        'Wind': '#90EE90',
        'Solar': '#FFD700',
        'Hydro': '#4169E1',
        'Other': '#808080'
    }

    # plot stacked bars
    bottom = np.zeros(len(mix_pivot))
    for fuel in mix_pivot.columns:
        color = colors.get(fuel, '#808080')
        ax.bar(mix_pivot.index, mix_pivot[fuel], bottom=bottom,
               label=fuel, color=color, edgecolor='white', linewidth=0.5)
        bottom += mix_pivot[fuel].values

    ax.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax.set_ylabel('Generation (GWh)', fontsize=12)
    ax.set_title('Generation Mix by Carbon Price', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/generation_mix_by_carbon_price.png', dpi=300)
    print(f"saved: {output_dir}/generation_mix_by_carbon_price.png")

    # plot 5: generation mix percentages (stacked area)
    mix_pct = mix_pivot.div(mix_pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.stackplot(mix_pct.index, *[mix_pct[col] for col in mix_pct.columns],
                 labels=mix_pct.columns,
                 colors=[colors.get(col, '#808080') for col in mix_pct.columns],
                 alpha=0.8)
    ax.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax.set_ylabel('Generation Mix (%)', fontsize=12)
    ax.set_title('Generation Mix Percentage by Carbon Price', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 100)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/generation_mix_percentage.png', dpi=300)
    print(f"saved: {output_dir}/generation_mix_percentage.png")

    # plot 6: coal vs renewables trade-off
    renewable_gen = mix_df[mix_df['fuel_type'].isin(['Wind', 'Solar'])].groupby('carbon_price')['generation_GWh'].sum()
    coal_gen = coal_df.set_index('carbon_price')['coal_generation_GWh']

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(coal_gen.index, coal_gen.values,
             marker='o', linewidth=2, markersize=8, color='#654321', label='Coal')
    ax1.set_xlabel('Carbon Price ($/ton CO2)', fontsize=12)
    ax1.set_ylabel('Coal Generation (GWh)', fontsize=12, color='#654321')
    ax1.tick_params(axis='y', labelcolor='#654321')
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(renewable_gen.index, renewable_gen.values,
             marker='s', linewidth=2, markersize=8, color='#228B22', label='Renewables')
    ax2.set_ylabel('Renewable Generation (GWh)', fontsize=12, color='#228B22')
    ax2.tick_params(axis='y', labelcolor='#228B22')

    fig.legend(loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=2)
    plt.title('Coal vs Renewable Generation', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/coal_vs_renewables.png', dpi=300)
    print(f"saved: {output_dir}/coal_vs_renewables.png")


def main():
    """run all carbon price scenarios and generate plots"""

    print("="*70)
    print("Carbon Price Scenario Analysis")
    print("="*70)

    # config
    data_folder = "./ercot_brownfield_expansion/10_days"
    zone = 2  # ERC_R
    solver = 'glpk'

    # carbon prices to test
    carbon_prices = [0, 25, 50, 75, 100, 150, 200]

    # allow command line override
    if len(sys.argv) > 1:
        carbon_prices = [float(p) for p in sys.argv[1:]]

    print(f"\nCarbon prices to test: {carbon_prices}")
    print(f"Data folder: {data_folder}")
    print(f"Zone: {zone}")
    print(f"Solver: {solver}")

    # run all scenarios
    print("\n" + "="*70)
    print("Running scenarios...")
    print("="*70)

    scenarios_results = []
    for price in carbon_prices:
        result = run_scenario(data_folder, zone, solver, price)
        scenarios_results.append(result)

    # analyze results
    print("\n" + "="*70)
    print("Analyzing results...")
    print("="*70)

    coal_df = analyze_coal_generation(scenarios_results)
    mix_df = analyze_generator_mix(scenarios_results)

    # save summary data
    coal_df.to_csv('coal_analysis.csv', index=False)
    print("\nsaved: coal_analysis.csv")

    mix_df.to_csv('generation_mix_analysis.csv', index=False)
    print("saved: generation_mix_analysis.csv")

    # print summary
    print("\n" + "="*70)
    print("Coal Analysis Summary")
    print("="*70)
    print(coal_df.to_string(index=False))

    # create plots
    print("\n" + "="*70)
    print("Generating plots...")
    print("="*70)

    plot_results(coal_df, mix_df)

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)
    print("\nResults saved to:")
    print("  - coal_analysis.csv")
    print("  - generation_mix_analysis.csv")
    print("  - plots/")


if __name__ == "__main__":
    main()
