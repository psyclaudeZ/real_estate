#! /usr/local/bin/python3

import logging

import matplotlib.pyplot as plt
import pandas as pd

logging.basicConfig(level=logging.NOTSET)

DEFAULT_CITIES = ["austin", "tampa", "columbus", "phoenix", "releigh"]
ZHVI_PATH = "data/zhvi_dec_2021.csv"


def main() -> None:
    logging.info("Processing data...")

    duplicate_cities = {}
    city_to_data = {}
    # see https://www.zillow.com/research/data/ for more details
    df = pd.read_csv(ZHVI_PATH)
    df_raw = df.drop(
        ["RegionName", "RegionID", "RegionType", "StateName", "SizeRank"], axis=1
    )
    for idx, row in df.iterrows():
        full_name = row["RegionName"]
        if full_name == "United States":
            continue
        city, state = row["RegionName"].split(", ")
        city = city.lower()
        if city in city_to_data:
            logging.warning(
                f"{city} already exists! new: {state}, existing: {city_to_data[city]['state']}"
            )
            duplicate_cities[city] = 1
            if should_skip_duplicate(city, state):
                continue
        city_to_data[city] = {
            "size_rank": row["SizeRank"],
            "state": state,
            "zhvi": df_raw.iloc[idx],
        }

    logging.info("Finished processing data.")

    logging.info("Starting interactive loop...")
    plt.ion()
    plt.show()
    new_city_list = []
    while True:
        raw_input = input("Cities or q?\n")
        if raw_input == "q":
            logging.info("Bye")
            return
        elif raw_input == "clear":
            new_city_list = []
            plt.clf()
            continue
        elif raw_input == "D":
            city_list = DEFAULT_CITIES
        elif raw_input == "":
            continue
        else:
            city_list = [c.strip() for c in raw_input.split(",")]
        ax = None
        for city in city_list:
            if not city.lower() in city_to_data:
                logging.warning(f"{city} does not exist in data.")
                continue
            if city.lower() in duplicate_cities:
                logging.warning(f"{city} has duplicate entries in dataset.")
            new_city_list.append(city)
            if ax is None:
                ax = city_to_data[city]["zhvi"].plot()
            else:
                ax = city_to_data[city]["zhvi"].plot(ax=ax)
        logging.info("Plotting data...")
        plt.legend(new_city_list)
        plt.draw()
        plt.pause(0.001)


def should_skip_duplicate(city: str, state: str) -> bool:
    if city == "austin" and state != "TX":
        return True
    if city == "columbus" and state != "OH":
        return True
    if city == "dayton" and state != "OH":
        return True
    return False


if __name__ == "__main__":
    main()
