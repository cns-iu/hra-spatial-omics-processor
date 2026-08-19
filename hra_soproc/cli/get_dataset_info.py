import csv

import requests

from hra_soproc.ftu_data import get_ftu_dataset_ids
from hra_soproc.store import get_store


def get_uuid(dataset_id):
    hubmap_id = dataset_id[0:15].replace("_", ".")
    query_dict = {
        "query": {"match": {"hubmap_id": hubmap_id}},
        "_source": {"includes": ["uuid"]},
    }
    response = requests.post(
        "https://search.api.hubmapconsortium.org/v3/search", json=query_dict
    )
    hits = response.json()["hits"]["hits"]
    uuid = hits[0]["_source"]["uuid"]
    return hubmap_id, uuid, f"https://entity.api.hubmapconsortium.org/entities/{uuid}"


def main():
    output = "output-data/datasets.csv"
    fields = "iri,dataset_id,hubmap_id,uuid,tissue,modality".split(",")

    store = get_store()
    ftu_dataset_ids = get_ftu_dataset_ids(store)

    with open(output, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fields)
        writer.writeheader()
        for dataset_id in sorted(ftu_dataset_ids):
            hubmap_id, uuid, iri = get_uuid(dataset_id)
            ds = store[dataset_id]
            row = {
                "iri": iri,
                "dataset_id": dataset_id,
                "hubmap_id": hubmap_id,
                "uuid": uuid,
                "tissue": ds.attrs["tissue"],
                "modality": ds.attrs["modality"],
            }
            writer.writerow(row)


if __name__ == "__main__":
    main()
