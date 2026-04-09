import os
import sys

from helpers.resolution import write_global_resolution_csv

AUTOMORPH_DATA = os.getenv('AUTOMORPH_DATA','.')

# read pixel_resolution from cli arg if defined, otherwise use default value 0.008
pixel_resolution = float(sys.argv[1]) if len(sys.argv) > 1 else 0.008

write_global_resolution_csv(
    f"{AUTOMORPH_DATA}/images",
    f"{AUTOMORPH_DATA}/resolution_information.csv",
    pixel_resolution,
)
