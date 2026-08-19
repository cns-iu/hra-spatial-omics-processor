
import numpy as np
import skimage


def repair_zarr_mask(mask):
    """
    Read a Zarr mask into memory, replacing unreadable chunks with zeros.

    Returns
    -------
    repaired : np.ndarray
        Repaired mask held entirely in memory.
    bad_chunks : list
        Indices of chunks that could not be read.
    """
    repaired = np.zeros(mask.shape, dtype=mask.dtype)
    bad_chunks = []

    for idx in np.ndindex(*mask.cdata_shape):
        slices = tuple(
            slice(
                i * chunk_size,
                min((i + 1) * chunk_size, array_size),
            )
            for i, chunk_size, array_size in zip(idx, mask.chunks, mask.shape)
        )

        try:
            repaired[slices] = mask.blocks[idx]
        except Exception as e:
            bad_chunks.append(idx)
            print(f"Replacing bad chunk {idx} with zeros: {e}")

    return repaired, bad_chunks


def get_ftu_dataset_ids(store):
    return [k for k in store.group_keys() if "ftus" in store[k].group_keys()]


def get_ftu_data(
    store, dataset_id, predictions="deecell_types_deepcell-types_2026-06-15_resmlp"
):
    ds = store[dataset_id]

    cell_segmenter = next(ds["segmentations"].keys())
    cell_mask = repair_zarr_mask(ds[f"segmentations/{cell_segmenter}"])[0]

    # Extract the cell centroids, rounding to the nearest whole pixel, and create
    # a mapping from cell centroid to the corresponding cell index
    cell_props = skimage.measure.regionprops(cell_mask)
    cell_centroids = {
        tuple(int(coord) for coord in p.centroid): int(p.label) for p in cell_props
    }

    idx_to_centroid = {
        int(p.label): tuple(int(coord) for coord in p.centroid) for p in cell_props
    }

    # Start by loading the celltype predictions from the archive
    if predictions not in ds[f"cell_types/predictions"].attrs:
        print(f"{dataset_id} is missing cell type predictions!")
        return

    celltypes_to_idx = ds["cell_types/predictions"].attrs[predictions]

    # These are stored in a celltype: [idx] format to save space in the archive.
    # Let's invert that so we have flat idx: celltype mapping...
    idx_to_celltype = {
        idx: ct for ct in celltypes_to_idx for idx in celltypes_to_idx[ct]
    }

    ftu_cell_ids = set()
    for ftu in ds["ftus"].keys():
        ftu_mask = repair_zarr_mask(ds[f"ftus/{ftu}/predictions"])[0]

        ### An extremely rudimentary procedure for finding cells inside of FTUs
        # Start by converting the per-FTU predictions into a binary selection of
        # which pixels correspond to an FTU and which don't
        ftu_pixels = {(x, y) for x, y in zip(*np.where(ftu_mask > 0))}

        # Now find the intersection of the cell centroids with the FTU pixels
        cell_ids_in_ftus = [
            cell_centroids[coord] for coord in cell_centroids.keys() & ftu_pixels
        ]

        # ID,X,Y,Cell Type,FTU
        for idx in cell_ids_in_ftus:
            cell_type = idx_to_celltype.get(idx, "Cell")
            x, y = idx_to_centroid[idx]
            ftu_cell_ids.add(idx)
            yield {
                "dataset_id": dataset_id,
                "x": x,
                "y": y,
                "cell_type": cell_type,
                "ftu": ftu,
            }

    # Write out all cells that were not part of FTUs
    for idx, (x, y) in idx_to_centroid.items():
        if idx not in ftu_cell_ids:
            cell_type = idx_to_celltype.get(idx, "Cell")
            yield {
                "dataset_id": dataset_id,
                "x": x,
                "y": y,
                "cell_type": cell_type,
                "ftu": "",
            }
