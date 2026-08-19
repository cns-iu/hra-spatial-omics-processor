import csv
import requests


def main():
    response = requests.get(
        "https://purl.humanatlas.io/ctann/deepcelltypes-hubmap",
        headers={"Accept": "application/json"},
    )
    data = response.json()
    with open("output-data/ct-lookup.csv", "w") as lookup_file:
        writer = csv.writer(lookup_file)
        writer.writerow(["label", "cl_id", "cl_label"])
        for row in data["data"]["mappings"]:
            writer.writerow(
                [row["subject_label"], row["object_id"], row["object_label"]]
            )


if __name__ == "__main__":
    main()
