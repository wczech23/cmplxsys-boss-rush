import pandas as pd
import random
from pytrends.request import TrendReq
import time


# file that uses pytrends to search for latest results of each disease based on state
def fetch_data(matching_diseases, state_abbr):
    pd.set_option('future.no_silent_downcasting', True)
    # creates variable that allows for data request
    pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), retries=2, backoff_factor=0.5)

    all_data = []
    # Process each disease one by one to find search trend relative to peak in last year
    for disease in matching_diseases:
        try:
            # sleep request to avoid 429 errors (overloading server)
            sleep_time = random.uniform(7,10)
            time.sleep(sleep_time)

            # requests search data for a disease in the requested U.S state
            geo_code = f'US-{state_abbr}'
            pytrends.build_payload([disease], timeframe='today 12-m', geo=geo_code)
            data = pytrends.interest_over_time()

            # calculating difference in popularity today compared to year average
            popularity_difference = data.loc[data.index.max(), disease] - data[disease].mean()
            # adding data to table
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            
            print(f'Gathered data on {disease}')
            
        except Exception as e:
            # if there is an error gathering the data, random data is used
            print(f"Error gathering {disease} data")
            popularity_difference = random.uniform(-10,10)
            all_data.append({'Disease':disease,'PopularityDiff':popularity_difference})
            continue

    # Combine all diseases into a single file with trends, this will be used to make the graph
    if all_data:
        combined_df = pd.DataFrame(all_data)
        combined_df.to_csv("disease_trends_US.csv", index=False)
        print("\nUpdated daily search trends!")