#%%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
plt.style.use("seaborn-v0_8")


#%%
outages = pd.read_csv("./data/eaglei_outages_2024.csv")
education = pd.read_csv("./data/Education2023.csv", encoding='latin-1')
population = pd.read_csv("./data/PopulationEstimates.csv", encoding='latin-1')
unemployment = pd.read_csv("./data/Unemployment2023.csv", encoding='latin-1')
poverty = pd.read_csv("./data/Poverty2023.csv", encoding='latin-1')

#%% 
education.columns = education.columns.str.strip()
population.columns = population.columns.str.strip()
unemployment.columns = unemployment.columns.str.strip()
poverty.columns = poverty.columns.str.strip()
education = education.rename(columns={'FIPS Code': 'fips_code'})
population = population.rename(columns={'FIPStxt': 'fips_code'})
unemployment = unemployment.rename(columns={'FIPS_Code': 'fips_code'})
poverty = poverty.rename(columns={'FIPS_Code': 'fips_code'})
#%%
edu_2023 = education[education['Attribute'].str.contains('2019-23', na=False)]
education_pivot = edu_2023.pivot_table(
    index='fips_code',
    columns='Attribute',
    values='Value',
    aggfunc='first').reset_index()

pop_2023 = population[population['Attribute'] == 'POP_ESTIMATE_2023']
population_pivot = pop_2023[['fips_code', 'Value']].rename(columns={'Value': 'population_2023'})
unemp_2023 = unemployment[unemployment['Attribute'] == 'Unemployment_rate_2023']
unemployment_pivot = unemp_2023[['fips_code', 'Value']].rename(columns={'Value': 'unemployment_rate_2023'})
pov_2023 = poverty[poverty['Attribute'] == 'PCTPOVALL_2023']
poverty_pivot = pov_2023[['fips_code', 'Value']].rename(columns={'Value': 'poverty_rate_2023'})
#%%
census_data = education_pivot.merge(
    population_pivot, on='fips_code', how='outer').merge(
    unemployment_pivot,on='fips_code', how='outer').merge(
    poverty_pivot, on='fips_code', how='outer') 

census_data = census_data[(census_data['fips_code'] >= 1000) &
             (census_data['fips_code'] < 57000)].copy()
#%%
outages['fips_code'] = outages['fips_code'].astype('category')
census_data['fips_code'] = census_data['fips_code'].astype(int)
merged_data = outages.merge(
    census_data,
    on='fips_code',
    how='left')
merged_data.dropna(axis = 0, inplace=True)

#%% 
merged_data['run_start_time'] = pd.to_datetime(merged_data['run_start_time'])
merged_data['date'] = merged_data['run_start_time'].dt.date
daily_outages = merged_data.groupby(['fips_code', 'county', 'state', 'date']).agg({
    'customers_out': 'sum',
    'total_customers': 'first', 
    'population_2023': 'first',
    'unemployment_rate_2023': 'first',
    'poverty_rate_2023': 'first'
}).reset_index()

edu_cols = [col for col in merged_data.columns if '2019-23' in str(col)]
if edu_cols:
    for col in edu_cols:
        if col not in daily_outages.columns:
            daily_outages[col] = merged_data.groupby(['fips_code', 'date'])[col].first().reset_index(drop=True)

# %%
daily_outages.to_csv("./data/daily_outages_data.csv")


# %%