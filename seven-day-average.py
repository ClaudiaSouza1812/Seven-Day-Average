import csv
import requests
from itertools import islice


def main():
    # Read NYTimes Covid Database
    download = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv")
    decoded_content = download.content.decode("utf-8")

    # create a file, stabilish the field names that will be the dictionary keys,
    # skip all the rows before the 14 last weeks and read it as a dictionary:
    file = decoded_content.splitlines()
    fieldnames = ["date", "state", "fips", "cases", "deaths"]
    skip_rows = len(file) - 840
    csv_reader = csv.DictReader(islice(file, skip_rows, None), fieldnames=fieldnames)

    # Construct 14 day lists of new cases for each states
    new_cases = calculate(csv_reader)

    # Create a list to store selected states
    states = []
    print("Choose one or more states to view average COVID cases.")
    print("Press enter when done.\n")

    c = 0
    while True:
        state = input("State: ").title().strip()
        if state in new_cases:
            states.append(state)
            c += 1
        elif len(state) == 0 and c > 0:
            break
        elif state not in new_cases and c == 0 or c != 0:
            print("Choose at least one US state")
    print("\nSeven-Day Averages")

    # Print out 7-day averages for this week vs last week
    comparative_averages(new_cases, states)


# TODO: Create a dictionary to store 14 most recent days of new cases by state
def calculate(csv_reader):
    # create a dictionary of current and one with previous cases
    current_cases = dict()
    prev_cases = dict()

    # create two objects to store the keys content
    for row_key in csv_reader:
        state = row_key["state"]
        cases = int(row_key["cases"])

        # populate the dictionary objects using the state as the key and cases as its value,
        # keep new cases updated by subtracting the previous cases from the actual cases,
        # return the last 14 days cases of each one of the 56 states
        if state not in prev_cases:
            prev_cases[state] = cases
            current_cases[state] = []
        else:
            new_case = cases - prev_cases[state]
            prev_cases[state] = cases

            current_cases[state].append(new_case)

    return current_cases


# TODO: Calculate and print out seven day average for given state
def comparative_averages(new_cases, states):
    for state in states:
        this_week = new_cases[state][7:]
        last_week = new_cases[state][:7]

        avg_this_week = round(sum(this_week) / len(this_week))
        avg_last_week = round(sum(last_week) / len(last_week))

        track_evo = avg_this_week - avg_last_week

        try:
            if track_evo > 0:
                percent = round(track_evo / avg_last_week * 100)
                msg = "an increase"
                print(f"{state} had a 7-day average of {avg_this_week} cases and {msg} of {percent}%.")
            else:
                percent_evo = abs(track_evo / avg_last_week * 100)
                msg = "a decrease"
                print(f"{state} had a 7-day average of {avg_this_week} cases and {msg} of {percent_evo:.2f}%.")
        except ZeroDivisionError:
            raise ZeroDivisionError


main()
