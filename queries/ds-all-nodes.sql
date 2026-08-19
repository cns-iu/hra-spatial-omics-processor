COPY (
  SELECT x as "X", y as "Y", 
    cell_type as "Cell Type",
    cell_type as "Level Three Cell Type",
    cl_label as "Level Three CL Label",
    cl_id as "Level Three CL ID"
  FROM
    cells
    WHERE dataset_id = '{dataset_id}'
) TO 'output-data/hubmap-mirror-ftu-datasets/{dataset_id}_{tissue}_{modality}-nodes.csv';
