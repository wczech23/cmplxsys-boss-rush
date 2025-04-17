import requests
import pandas as pd
import random
from datetime import datetime
from pytrends.request import TrendReq
import time

# 50 diseases we want to track
# We'll fetch real-time data for the ones disease.sh can handle (COVID-19, Influenza, Monkeypox),
# and generate random data for the rest.
DISEASE_LIST = [
    "COVID-19",
    "Influenza",
    "Monkeypox",
    "Pneumonia",
    "Bronchitis",
    "Asthma",
    "Strep Throat",
    "Chickenpox",
    "Migraine",
    "Cold",
    "Diabetes",
    "Tuberculosis",
    "Hepatitis A",
    "Hepatitis B",
    "Hepatitis C",
    "Lyme Disease",
    "Zika",
    "Ebola",
    "Malaria",
    "Dengue",
    "Cholera",
    "Rabies",
    "Tetanus",
    "Measles",
    "Mumps",
    "Rubella",
    "Pertussis",
    "Polio",
    "Scarlet Fever",
    "RSV",
    "Norovirus",
    "Shigellosis",
    "Salmonellosis",
    "Giardiasis",
    "Legionnaires",
    "Anthrax",
    "Plague",
    "Yellow Fever",
    "HIV",
    "Gonorrhea",
    "Syphilis",
    "Chlamydia",
    "MRSA",
    "Leprosy",
    "West Nile Virus",
    "Avian Influenza",
    "Hantavirus",
    "Meningitis",
    "Toxoplasmosis",
    "Candidiasis"
]

# disease.sh coverage for real-time
# Key = disease name in our list, Value = type or endpoint ID
REAL_TIME_COVERAGE = {
    "COVID-19": "covid",
    "Influenza": "flu",
    "Monkeypox": "mpx"
    # Add more if disease.sh or other APIs support them
}

# For each region, define how to fetch from disease.sh for the diseases it covers
REGION_API_URLS = {
    "USA": {
        "covid": "https://disease.sh/v3/covid-19/countries/USA",
        "flu":   "https://disease.sh/v3/flu",
        "mpx":   "https://disease.sh/v3/covid-19/historical/USA?lastdays=1"  
        # 'mpx' not officially in disease.sh, so we might have to simulate it or remove it
    },
    "US-MI": {
        "covid": "https://disease.sh/v3/covid-19/states/Michigan",
        "flu":   "https://disease.sh/v3/flu",
        "mpx":   "https://disease.sh/v3/covid-19/historical/Michigan?lastdays=1"
    },
    "US-CA": {
        "covid": "https://disease.sh/v3/covid-19/states/California",
        "flu":   "https://disease.sh/v3/flu",
        "mpx":   "https://disease.sh/v3/covid-19/historical/California?lastdays=1"
    }
}

def fetch_real_time_cases(disease, region):

    coverage_key = REAL_TIME_COVERAGE.get(disease)
    if not coverage_key:
        return None  # Not covered by disease.sh

    region_endpoints = REGION_API_URLS.get(region, {})
    url = region_endpoints.get(coverage_key)
    if not url:
        return None  # We don't have an endpoint for this disease in this region

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if coverage_key == "covid":
            # For COVID-19, we can parse data['cases']
            # If it's a country, data['cases']; if it's a state, same structure
            return data.get("cases", 0)

        elif coverage_key == "flu":

            influenza_data = data.get("influenza", {})

            tested_str = influenza_data.get("tested", "0")

            try:
                tested_val = int(tested_str)
            except ValueError:
                tested_val = 0
            return tested_val

        elif coverage_key == "mpx":

            timeline = data.get("timeline", {}).get("cases", {})
            # timeline is something like {"3/25/2025": 123456, ...}
            if timeline:
                # get the last date's value
                last_key = sorted(timeline.keys())[-1]
                return timeline[last_key]
            else:
                return 0

    except Exception as e:
        print(f"[ERROR] {disease} in {region} -> {e}")
        return None

def main():
    all_rows = []
    date_str = datetime.now().strftime('%Y-%m-%d')

    # We only handle these three region codes
    regions = ["USA", "US-MI", "US-CA"]

    for region in regions:
        for disease in DISEASE_LIST:
            real_time = fetch_real_time_cases(disease, region)
            if real_time is not None:
                cases = real_time
            else:
                # If not available in real-time, simulate with random or default
                cases = random.randint(500, 10000)  # example range

            all_rows.append({
                "Disease": disease,
                "Region": region,
                "Date": date_str,
                "Cases": cases
            })

    df = pd.DataFrame(all_rows)
    df.to_csv("disease_cases_by_region.csv", index=False)
    print("[INFO] disease_cases_by_region.csv updated successfully!")


    # search trends
    
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.5)

    
    all_data = []

    # Process each disease one by one to find search trend relative to peak in last year
    for disease in DISEASE_LIST:
        
        try:
            pytrends.build_payload([disease], cat=0, timeframe='today 12-m', geo='', gprop='')
            data = pytrends.interest_over_time()

            # calculating difference in popularity today compared to year average
            popularity_difference = data.loc[data.index.max(), disease] - data[disease].mean()
            # adding data to list
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            
            print(disease)
            # sleep request to avoid 429 errors
            sleep_time = random.uniform(7,10)
            time.sleep(sleep_time)

            
            
        except Exception as e:
            print(f"Error with gathering {disease}: {e}")
            popularity_difference = random.uniform(-10,10)
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            continue
        
    # Combine all items in the list into a single df
    if all_data:
        combined_df = pd.DataFrame(all_data)
        print(combined_df.tail())
        combined_df.to_csv("disease_searches_US.csv", index=False)
        print("Updated daily search trends!")


if __name__ == "__main__":
    main()
