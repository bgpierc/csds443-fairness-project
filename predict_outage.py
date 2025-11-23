import pandas as pd
from datetime import date, timedelta

def outage_history(outages, fips_code, date):
    '''
    Inputs:
    outages - dataframe containing outage and demographic information
    fips_code - unique county indentifier
    date - target date to determine history for

    Outputs:
    history - outage history preceeding target date (1 for outage, 0 for no outage)
    result - target date outage outcome (1 for outage, 0 for no outage)
    '''
    county_outages = outages[outages["fips_code"].isin([fips_code])]["date"].tolist()
    outage_history = []

    for i in range(0, 6):
        if (date - timedelta(days=i)).strftime("%Y-%m-%d") in county_outages:
            outage_history.insert(0, 1)
        else:
            outage_history.insert(0, 0)

    return outage_history[:5], outage_history[5]

if __name__=="__main__":
    outages = pd.read_csv("./data/daily_outages_data.csv")

    print(outage_history(outages, 1001, date(2024, 1, 5)))