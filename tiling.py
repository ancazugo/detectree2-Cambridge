import os
from pathlib import Path
from argparse import ArgumentParser
from timeit import default_timer
from dotenv import load_dotenv

from detectree2.preprocessing.tiling import tile_data

import rasterio

def tile_rgb_by_year(city='Cambridge', year=2017, buffer=20, tile_size=160, threshold=0):

    # Set up paths
    appends = str(tile_size) + "_" + str(buffer) + "_" + str(threshold)
    site_path = os.getenv('DATA_FOLDER') + f'/{city}/'
    img_dir = site_path + f'Aerial_RGB_25cm_{year}_32630/'
    tiles_dir = site_path + f'tiles_0.25m_{year}_{appends}/'
    
    img_paths = list(Path(img_dir).glob('*.tif'))
    
    for i in range(len(img_paths)):
        
        t_1 = default_timer()
        # Read in the tiff file
        data = rasterio.open(str(img_paths[i]))

        # Tile RGB imagery
        tile_data(data, tiles_dir, buffer, tile_size, tile_size)
        
        t_2 = default_timer()
        print(f"{(t_2 - t_1)/60.0} minutes for {str(img_paths[i])}")
        
    return len(img_paths)
        
if __name__ == "__main__":
    
    parser = ArgumentParser(description="Sea Ice Tiling")
    parser.add_argument("--city", default="Cambridge", type=str, choices=["Cambridge", "NY_raw"],
                        help="Origin of the data")
    parser.add_argument("--year", default=2017, type=int, help="Date of data acquisition")
    parser.add_argument("--buffer", default=20, type=int, help="Buffer of the tiles")
    parser.add_argument("--tile_size", default=160, type=int, help="Size of the tiles (squared tiles)")
    parser.add_argument("--threshold", default=0, type=int, help="Threshold for cover of trees in the tiles")
    args = parser.parse_args()

    city = args.city
    year = args.year
    buffer = args.buffer
    tile_size  =args.tile_size
    threshold = args.threshold
    load_dotenv()
    
    t_start = default_timer()
    
    n_rgb_files = tile_rgb_by_year(city, year, buffer, tile_size, threshold)

    t_end = default_timer()
    print(f"Tiling execution time: {(t_end - t_start)/60.0} minutes for {n_rgb_files} images")
