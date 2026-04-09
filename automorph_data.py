"""
Check if environment variable AUTOMORPH_DATA is set.
If yes, creates all sub-folders required for the project.

AUTOMORPH_DATA allows to move all data files away from code base and keep the code base clean.
Plus, it can be used to keep data on writable storage - while code base can be on read-only storage.
"""
import logging
import os
import shutil

from runtime_utils import configure_logging

configure_logging()
LOGGER = logging.getLogger(__name__)

if os.getenv('AUTOMORPH_DATA'):
    data_path = os.getenv('AUTOMORPH_DATA')
    LOGGER.info("Set %s as AutoMorph output directory", data_path)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    if not os.path.exists(os.path.join(data_path, 'images')):
        os.makedirs(os.path.join(data_path, 'images'))   
    if not os.path.exists(os.path.join(data_path, 'Results')):
        os.makedirs(os.path.join(data_path, 'Results'))
