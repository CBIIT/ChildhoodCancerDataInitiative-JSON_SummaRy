#!/usr/bin/env python3

# JSON_SummaRy.py

##############
#
# Env. Setup
#
##############

import json
from collections import defaultdict
import argparse
import argcomplete
import os
from datetime import date

parser = argparse.ArgumentParser(
    prog="JSON_SummaRy.py",
    description="This script will take a JSON metadata file and return a summary file for key-value counts.",
)

parser._action_groups.pop()
required_arg = parser.add_argument_group("required arguments")
# optional_arg = parser.add_argument_group("optional arguments")

required_arg.add_argument(
    "-f", "--filename", type=str, help="A JSON file", required=True
)

argcomplete.autocomplete(parser)

args = parser.parse_args()

# pull in args as variables
json_file_path = args.filename

print("\nThe JSON summary has begun.\n\n")

# READ IN FILE
with open(json_file_path, "r") as file:
    data = json.load(file)


##############
#
# File name rework
#
##############

# Determine file ext and abs path
file_name = os.path.splitext(os.path.split(os.path.relpath(json_file_path))[1])[0]
file_ext = os.path.splitext(json_file_path)[1]
file_dir_path = os.path.split(os.path.abspath(json_file_path))[0]

if file_dir_path == "":
    file_dir_path = "."


# obtain the date
def refresh_date():
    today = date.today()
    today = today.strftime("%Y%m%d")
    return today


todays_date = refresh_date()

# Output file name based on input file name and date/time stamped.
output_file = file_name + "_SummaRy" + todays_date


# For each item, for each key, count the instances of that value and record the total number for each value and total in the key.
def count_values_per_key(data):
    key_counts = defaultdict(lambda: defaultdict(int))
    key_sums = defaultdict(int)

    def process_item(item):
        if isinstance(item, list):
            for sub_item in item:
                process_item(sub_item)
        elif isinstance(item, dict):
            for key, value in item.items():
                key_counts[key][json.dumps(value, sort_keys=True)] += 1
                key_sums[key] += 1  # Increment count for the key
                process_item(value)

    for record_type, records in data.items():
        for record in records:
            process_item(record)

    return key_counts, key_sums


result_counts, result_sums = count_values_per_key(data)

# Output to a text file
output_file_path = file_dir_path + "/" + output_file + ".txt"

with open(output_file_path, "w") as output_file:
    output_file.write(
        f"The following is a summary for the file: {json_file_path}.\nThe keys for '_id' and 'age_at_' were removed for readability, as these values are often unique per entry and thus would list each entry in the study.\n\n"
    )
    for key, value_counts in result_counts.items():
        # skip all _id props
        if "_id" not in key:
            # skip all age_at props
            if "age_" not in key:
                output_file.write(f"Key: {key}, Total Count: {result_sums[key]}\n")
                for value, count in value_counts.items():
                    output_file.write(f"\t{value}: {count} occurrences\n")
                output_file.write("\n")

print(f"Results have been written to {output_file_path}")
