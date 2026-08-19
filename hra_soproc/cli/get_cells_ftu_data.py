import csv
from random import shuffle

from hra_soproc.ftu_data import get_ftu_data
from hra_soproc.store import get_store


def main():
    output = "output-data/spatial-cells-ftus.csv"
    fields = "dataset_id,x,y,cell_type,ftu".split(",")

    print("Loading HuBMAP data store...")
    store = get_store()
    with open("output-data/datasets.csv", newline="", encoding="utf-8") as dataset_file:
        ftu_dataset_ids = [ds["dataset_id"] for ds in csv.DictReader(dataset_file)]
    shuffle(ftu_dataset_ids)

    with open(output, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fields)
        writer.writeheader()
        for idx, dataset_id in enumerate(ftu_dataset_ids):
            print(f"Processing {dataset_id} ({idx+1}/{len(ftu_dataset_ids)})...")
            for row in get_ftu_data(store, dataset_id):
                writer.writerow(row)
                csv_file.flush()


if __name__ == "__main__":
    main()
