import posixpath
import zipfile

import fsspec
from hra_soproc.store import LOCAL_FILE, S3_URL
from tqdm import tqdm

BUFFER_SIZE = 8 * 1024 * 1024  # 8 MiB


def main():
    fs, root = fsspec.core.url_to_fs(S3_URL)
    root = root.rstrip("/")

    # Get object metadata so tqdm can show total bytes.
    entries = fs.find(root, detail=True)

    files = [
        (path, info) for path, info in entries.items() if info.get("type") == "file"
    ]

    total_bytes = sum(info.get("size", 0) for _, info in files)

    with zipfile.ZipFile(
        LOCAL_FILE,
        mode="w",
        compression=zipfile.ZIP_STORED,
        allowZip64=True,
    ) as zf:
        with tqdm(
            total=total_bytes,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="Downloading Zarr",
            dynamic_ncols=True,
        ) as progress:
            for source_path, _ in files:
                archive_path = posixpath.relpath(source_path, root)

                progress.set_postfix_str(archive_path, refresh=False)

                # Stream directly from S3 into the ZIP.
                with fs.open(source_path, "rb") as src:
                    with zf.open(archive_path, "w") as dst:
                        while chunk := src.read(BUFFER_SIZE):
                            dst.write(chunk)
                            progress.update(len(chunk))

    print(f"Wrote {LOCAL_FILE}")


if __name__ == "__main__":
    main()
