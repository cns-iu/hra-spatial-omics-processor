#!/bin/bash

if [ ! -e output-data/hubmap.zarr.zip ]; then
  download-data
fi
