import sys

from helpers.data import data_root
from helpers.resolution import write_global_resolution_csv

# read pixel_resolution from cli arg if defined, otherwise use default value 0.008
pixel_resolution = float(sys.argv[1]) if len(sys.argv) > 1 else 0.008
root = data_root()

write_global_resolution_csv(
    root / "images",
    root / "resolution_information.csv",
    pixel_resolution,
)
