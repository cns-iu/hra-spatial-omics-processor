import zarr
import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL = os.getenv("USE_REMOTE_STORE") != "true"
S3_URL = "s3://hubmap-mirror-demo/hubmap.zarr"
LOCAL_FILE = "output-data/hubmap.zarr.zip"


def get_store(local=USE_LOCAL, s3_url=S3_URL, local_file=LOCAL_FILE):
    if local:
        return zarr.open_group(
            store=zarr.storage.ZipStore(local_file, mode="r"), mode="r"
        )
    else:
        return zarr.open_group(
            store=s3_url,
            mode="r",
            storage_options={
                "anon": False,
                "client_kwargs": dict(region_name="us-east-2"),
            },
        )
