import pandas as pd
import numpy as np
from datetime import date, timedelta
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

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
    # outage_history = []
    outage_history = [outages.loc[outages["fips_code"] == fips_code, "poverty_rate_2023"].iloc[0]]

    for i in range(0, 6):
        if (date - timedelta(days=i)).strftime("%Y-%m-%d") in county_outages:
            outage_history.insert(0, 1)
        else:
            outage_history.insert(0, 0)

    return outage_history[:5], outage_history[5]

def generate_data(outages, start_date=date(2024, 1, 6), end_date=date(2024, 12, 31)):
    '''
    Inputs:
    outages - dataframe containing outage and demographic information
    start_date - earliest date to predict outage for (defaults to earliest date with full history)
    end_date - latest date to predict outage for (defaults to latest date with full history)

    Outputs:
    X - history of a random date for every county
    y - outage result of a random date for every county
    '''
    X = []
    y = []
    fips_codes = np.unique(outages["fips_code"])

    for code in fips_codes:
        for _ in range(5):
            target_date = start_date + timedelta(days=np.random.randint((end_date - start_date).days))
            data = outage_history(outages, code, target_date)
            X.append(data[0])
            y.append(data[1])

    return X, y

if __name__=="__main__":
    outages = pd.read_csv("./data/daily_outages_data.csv")

    X, y = generate_data(outages)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    print("Accuracy:", model.score(X_test, y_test))
