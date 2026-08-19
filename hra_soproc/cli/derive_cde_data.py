import json
from pathlib import Path

import duckdb

REPO_ROOT = Path(__file__).resolve().parents[2]
QUERY_PATH = REPO_ROOT / "queries"


def query(conn, fname, **kwargs):
    sql = (QUERY_PATH / fname).read_text(encoding="utf-8")
    return conn.execute(sql.format(**kwargs))


def init_db():
    """Create an in-memory DuckDB database and load the project schema SQL."""
    conn = duckdb.connect(database=":memory:")
    query(conn, "create-db.sql")
    return conn


def write_nodes(conn, iri, dataset_id, tissue, modality):
    context = {
        "iri": iri,
        "dataset_id": dataset_id,
        "tissue": tissue,
        "modality": modality,
    }
    write_ds_json("hubmap-mirror-ftu-datasets", iri, dataset_id, tissue, modality)
    write_ds_json("hubmap-mirror-ftu-cells-only", iri, dataset_id, tissue, modality)
    query(conn, "ds-all-nodes.sql", **context)
    query(conn, "ds-ftu-nodes.sql", **context)


def write_ds_json(dir, iri, dataset_id, tissue, modality):
    json_file = f"output-data/{dir}/{dataset_id}_{tissue}_{modality}-dataset.json"
    with open(json_file, "w") as out:
        out.write(json.dumps({"@id": iri}, indent=2))


def main():
    conn = init_db()
    ftu_datasets = query(conn, "get-ftu-datasets.sql").fetchall()
    for iri, dataset_id, tissue, modality in ftu_datasets:
        write_nodes(conn, iri, dataset_id, tissue, modality)
    conn.close()


if __name__ == "__main__":
    main()
