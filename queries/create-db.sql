
CREATE TABLE ct_lookup AS SELECT * FROM 'output-data/ct-lookup.csv';
CREATE TABLE datasets AS SELECT * FROM 'output-data/datasets.csv';
CREATE TABLE ftu_lookup AS SELECT * FROM 'output-data/ftu-lookup.csv';
CREATE TABLE spatial_cells AS SELECT * FROM read_csv('output-data/spatial-cells-ftus.csv', ignore_errors=true);

CREATE TABLE cells AS
  SELECT datasets.*, 
    spatial_cells.* EXCLUDE (dataset_id),
    ct_lookup.* EXCLUDE (label),
    ftu_lookup.* EXCLUDE (label)
  FROM spatial_cells
    INNER JOIN datasets USING (dataset_id)
    LEFT OUTER JOIN ct_lookup ON (spatial_cells.cell_type = ct_lookup.label)
    LEFT OUTER JOIN ftu_lookup ON (spatial_cells.ftu = ftu_lookup.label)
  ORDER BY dataset_id;

COPY cells TO 'output-data/spatial-cells-ftus.parquet';
