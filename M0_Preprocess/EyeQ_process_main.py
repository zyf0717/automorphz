import fundus_prep as prep
import logging
import os
import pandas as pd
import sys
from pathlib import Path
from PIL import ImageFile

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from helpers.runtime import configure_logging

ImageFile.LOAD_TRUNCATED_IMAGES = True

AUTOMORPH_DATA = os.getenv('AUTOMORPH_DATA','..')
configure_logging()
LOGGER = logging.getLogger(__name__)

def process(image_list, save_path):
    
    radius_list = []
    centre_list_w = []
    centre_list_h = []
    name_list = []
    list_resolution = []
    scale_resolution = []
    processed_count = 0
    
    resolution_list = pd.read_csv(f'{AUTOMORPH_DATA}/resolution_information.csv')
    
    # TODO(parallelism): This per-image preprocessing loop is independent work.
    # Move it to a worker pool and merge the returned crop metadata before
    # writing crop_info.csv, similar to the M3 per-image process pool.
    for image_path in image_list:
        
        dst_image = f'{AUTOMORPH_DATA}/images/' + image_path
        try:
            resolution_ = resolution_list['res'][resolution_list['fundus']==image_path].values[0]
            list_resolution.append(resolution_)
            img = prep.imread(dst_image)
            r_img, borders, mask, r_img, radius_list,centre_list_w, centre_list_h = prep.process_without_gb(img,img,radius_list,centre_list_w, centre_list_h)
            prep.imwrite(save_path + image_path.split('.')[0] + '.png', r_img)
            name_list.append(image_path.split('.')[0] + '.png')
            processed_count += 1
        
        except Exception:
            LOGGER.exception("Failed to preprocess image: %s", image_path)

    if processed_count == 0:
        raise RuntimeError("No images were successfully preprocessed")

    scale_list = [a*2/912 for a in radius_list]
    scale_resolution = [a*b*1000 for a,b in zip(list_resolution,scale_list)]
    Data4stage2 = pd.DataFrame({'Name':name_list, 'centre_w':centre_list_w, 'centre_h':centre_list_h, 'radius':radius_list, 'Scale':scale_list, 'Scale_resolution':scale_resolution})
    Path(f'{AUTOMORPH_DATA}/Results/M0').mkdir(parents=True, exist_ok=True)
    Data4stage2.to_csv(f'{AUTOMORPH_DATA}/Results/M0/crop_info.csv', index = None, encoding='utf8')


if __name__ == "__main__":
    image_list = sorted(os.listdir(f'{AUTOMORPH_DATA}/images'))
    save_path = f'{AUTOMORPH_DATA}/Results/M0/images/'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    process(image_list, save_path)

        
