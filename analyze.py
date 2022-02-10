#! /usr/local/bin/python3

import logging

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

logging.basicConfig(level=logging.NOTSET)

DEFAULT_CITIES = ["austin", "tampa", "columbus", "phoenix", "releigh"]
ZHVI_PATH = "data/zhvi_dec_2021.csv"
ZORI_PATH = "data/zori_dec_2021.csv"


def main() -> None:
    logging.info("Processing data...")

    duplicate_cities = {}
    city_to_data = {}
    # see https://www.zillow.com/research/data/ for more details on the data
    zhvi_df = pd.read_csv(ZHVI_PATH)
    zori_df = pd.read_csv(ZORI_PATH)
    zhvi_df_raw = zhvi_df.drop(
        ["RegionName", "RegionID", "RegionType", "StateName", "SizeRank"], axis=1
    )
    # consistent data format with ZORI
    zhvi_df_raw = zhvi_df_raw.rename(columns=lambda col: col[:-3])
    zori_df_raw = zori_df.drop(["RegionName", "RegionID", "SizeRank"], axis=1)

    for idx, row in zhvi_df.iterrows():
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
        # re: 98, ZORI only contains 100 rows of ZHVI (including labels row and "United States")
        city_to_data[city] = {
            "size_rank": row["SizeRank"],
            "state": state,
            "zhvi": zhvi_df_raw.iloc[idx],
            "zori": zori_df_raw.iloc[idx] if idx < 98 else None,
            "price-to-rent": zhvi_df_raw.iloc[idx].div(zori_df_raw.iloc[idx]).div(12)
            if idx < 98
            else None,
        }

    logging.info("Finished processing data.")

    logging.info("Starting interactive loop...")
    figure, axis = plt.subplots(2, 2, figsize=(12, 10))
    plt.ion()
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

        logging.info("Plotting data...")
        for city in city_list:
            if not city.lower() in city_to_data:
                logging.warning(f"{city} does not exist in data.")
                continue
            if city.lower() in duplicate_cities:
                logging.warning(f"{city} has duplicate entries in dataset.")

            city_to_data[city]["zhvi"].plot(ax=axis[0, 0])
            axis[0, 0].yaxis.set_major_locator(ticker.MultipleLocator(25000))
            axis[0, 0].yaxis.grid()
            axis[0, 0].set_title("Home value index")

            city_to_data[city]["zori"].plot(ax=axis[0, 1])
            axis[0, 1].yaxis.set_major_locator(ticker.MultipleLocator(125))
            axis[0, 1].yaxis.grid(True)
            axis[0, 1].set_title("Rental index")

            city_to_data[city]["price-to-rent"].plot(ax=axis[1, 0])
            axis[1, 0].yaxis.set_major_locator(ticker.MultipleLocator(2.5))
            axis[1, 0].yaxis.grid(True)
            axis[1, 0].set_title("Price-to-rent")

            new_city_list.append(city)
            figure.legend(new_city_list)
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
