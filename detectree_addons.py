import json
import os
import glob
import random
import warnings
from pathlib import Path

import cv2
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.io import DatasetReader
from rasterio.mask import mask
from shapely.geometry import box
from detectron2.engine import DefaultPredictor
from detectree2.models.train import get_tree_dicts
from detectron2.evaluation.coco_evaluation import instances_to_coco_json

def get_features(gdf: gpd.GeoDataFrame) -> list:
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them.
    Args:
      gdf: Input geopandas dataframe
    Returns:
      json style data
    """
    return [json.loads(gdf.to_json())["features"][0]["geometry"]]

def read_multiple_rgb(site_path: str) -> list[DatasetReader]:
    """Reads multiple orthomosaic files from a single location (non-recursive).
    Returns a list of DatasetReader objects

    Args:
        site_path (str): folder where all the raster files are located

    Returns:
        list[DatasetReader]: list of DatasetReader objects
    """
    site_path = Path(site_path)
    
    files = list(Path(site_path).glob("*.tif"))
    
    rasters = [rasterio.open(file) for file in files]
    
    return rasters

def prepare_tiled_data_train(data_lst: list[DatasetReader], out_dir: str, tilename: str, buffer: int, tile_size: int, 
                            crowns: gpd.GeoDataFrame = None, threshold: float = 0, nan_threshold: float = 0.1, dtype_bool: bool = False) -> None:
    
    out_path = Path(out_dir)
    os.makedirs(out_path, exist_ok=True)
    crs = data_lst[0].crs.data["init"].split(":")[1]
    
    for raster in data_lst:
      
        minx = int(raster.bounds[0])
        miny = int(raster.bounds[1])
        out_path_root = out_path / f"{tilename}_{minx}_{miny}_{tile_size}_{buffer}_{crs}"
        
        # Calculate the bounding box coordinates with buffer
        minx_buffered = minx - buffer
        miny_buffered = miny - buffer
        maxx_buffered = minx + tile_size + buffer
        maxy_buffered = miny + tile_size + buffer
      
        bbox = box(minx_buffered, miny_buffered, maxx_buffered, maxy_buffered)
        geo = gpd.GeoDataFrame({"geometry": bbox}, index=[0], crs=data_lst[0].crs)
        coords = get_features(geo)
      
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Warning:
            # _crs_mismatch_warn
            overlapping_crowns = gpd.clip(crowns, geo)

            # Ignore tiles with no crowns
            if overlapping_crowns.empty:
                continue

            # Discard tiles that do not have a sufficient coverage of training crowns
            if (overlapping_crowns.dissolve().area[0] / geo.area[0]) < threshold:
                continue

        out_img, out_transform = mask(raster, shapes=coords, crop=True)
        
        out_sumbands = np.sum(out_img, 0)
        zero_mask = np.where(out_sumbands == 0, 1, 0)
        nan_mask = np.where(out_sumbands == 765, 1, 0)
        sumzero = zero_mask.sum()
        sumnan = nan_mask.sum()
        totalpix = out_img.shape[1] * out_img.shape[2]
        
        if sumzero > nan_threshold * totalpix:  # reject tiles with many 0 cells
                continue
        elif sumnan > nan_threshold * totalpix:  # reject tiles with many NaN cells
            continue
        
        out_meta = raster.meta.copy()
        out_meta.update({
            "driver": "GTiff",
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_transform,
            "nodata": None,
        })
        
        if dtype_bool:
            out_meta.update({"dtype": "uint8"})
        
        out_tif = out_path_root.with_suffix(out_path_root.suffix + ".tif").as_posix()
        with rasterio.open(out_tif, "w", **out_meta) as dest:
            dest.write(out_img)
        
        # read in the tile we have just saved
        clipped = rasterio.open(out_tif)

        # read it as an array
        arr = clipped.read()

        # each band of the tiled tiff is a colour!
        r = arr[0]
        g = arr[1]
        b = arr[2]

        # stack up the bands in an order appropriate for saving with cv2, then rescale to the correct 0-255 range
        # for cv2. BGR ordering is correct for cv2 (and detectron2)
        rgb = np.dstack((b, g, r))

        # Some rasters need to have values rescaled to 0-255
        # TODO: more robust check
        if np.max(g) > 255:
            rgb_rescaled = 255 * rgb / 65535
        else:
            # scale to image
            rgb_rescaled = rgb

        # save this as png, named with the origin of the specific tile
        # potentially bad practice
        cv2.imwrite(
            str(out_path_root.with_suffix(out_path_root.suffix + ".png").resolve()),
            rgb_rescaled,
        )
        
        overlapping_crowns = overlapping_crowns.explode(index_parts=True)

        # # translate to 0,0 to overlay on png
        # # this now works as a universal approach.
        # if minx == raster.bounds[0] and miny == raster.bounds[1]:
        #     # print("We are in the bottom left!")
        #     moved = overlapping_crowns.translate(-minx, -miny)
        # elif miny == raster.bounds[1]:
        #     # print("We are on the bottom, but not bottom left")
        #     moved = overlapping_crowns.translate(-minx + buffer, -miny)
        # elif minx == raster.bounds[0]:
        #     # print("We are along the left hand side, but not bottom left!")
        #     moved = overlapping_crowns.translate(-minx, -miny + buffer)
        # else:
        #     # print("We are in the middle!")
        #     moved = overlapping_crowns.translate(-minx + buffer, -miny + buffer)
        # Translate to 0,0 to overlay on png
        moved = overlapping_crowns.translate(-minx + buffer, -miny + buffer)
        scalingx = 1 / (raster.transform[0])
        scalingy = -1 / (raster.transform[4])
        moved_scaled = moved.scale(scalingx, scalingy, origin=(0, 0))

        impath = {"imagePath": out_path_root.with_suffix(out_path_root.suffix + ".png").as_posix()}

        # Save as a geojson, a format compatible with detectron2, again named by the origin of the tile.
        # If the box selected from the image is outside of the mapped region due to the image being on a slant
        # then the shp file will have no info on the crowns and hence will create an empty gpd Dataframe.
        # this causes an error so skip creating geojson. The training code will also ignore png so no problem.
        try:
            filename = out_path_root.with_suffix(out_path_root.suffix + ".geojson")
            moved_scaled = overlapping_crowns.set_geometry(moved_scaled)
            moved_scaled.to_file(
                driver="GeoJSON",
                filename=filename,
            )
            with open(filename, "r") as f:
                shp = json.load(f)
                shp.update(impath)
            with open(filename, "w") as f:
                json.dump(shp, f)
        except ValueError:
            print("Cannot write empty DataFrame to file.")
            continue
        # Repeat and want to save crowns before being moved as overlap with lidar data to get the heights
        # can try clean up the code here as lots of reprojecting and resaving but just going to get to
        # work for now
        out_geo_file = out_path_root.parts[-1] + "_geo"
        out_path_geo = out_path / Path(out_geo_file)
        try:
            filename_unmoved = out_path_geo.with_suffix(out_path_geo.suffix + ".geojson")
            overlapping_crowns.to_file(
                driver="GeoJSON",
                filename=filename_unmoved,
            )
            with open(filename_unmoved, "r") as f:
                shp = json.load(f)
                shp.update(impath)
            with open(filename_unmoved, "w") as f:
                json.dump(shp, f)
        except ValueError:
            print("Cannot write empty DataFrame to file.")
            continue
        
def get_filenames(directory: str):
    """Get the file names if no geojson is present.
    Allows for predictions where no delinations have been manually produced.
    Args:
        directory (str): directory of images to be predicted on
    """
    dataset_dicts = []
    files = glob.glob(directory + "*.png")
    for filename in [file for file in files]:
        file = {}
        # filename = os.path.join(directory, filename)
        file["file_name"] = filename

        dataset_dicts.append(file)
    return dataset_dicts

def predict_on_data(
    directory: str = "./",
    predictor=DefaultPredictor,
    eval=False,
    save: bool = True,
    num_predictions=0,
    out_dir: str = './'):
    """Make predictions on tiled data.
    Predicts crowns for all png images present in a directory and outputs masks as jsons.
    """
    
    pred_dir = os.path.join(directory, "predictions")
    if directory != out_dir:
      pred_dir = out_dir

    Path(pred_dir).mkdir(parents=True, exist_ok=True)

    if eval:
        dataset_dicts = get_tree_dicts(directory)
    else:
        dataset_dicts = get_filenames(directory)

    # Works out if all items in folder should be predicted on
    if num_predictions == 0:
        num_to_pred = len(dataset_dicts)
    else:
        num_to_pred = num_predictions

    for d in random.sample(dataset_dicts, num_to_pred):
        img = cv2.imread(d["file_name"])
        outputs = predictor(img)

        # Creating the file name of the output file
        file_name_path = d["file_name"]
        # Strips off all slashes so just final file name left
        file_name = os.path.basename(os.path.normpath(file_name_path))
        file_name = file_name.replace("png", "json")
        output_file = os.path.join(pred_dir, f"Prediction_{file_name}")
        print(output_file)

        if save:
            # Converting the predictions to json files and saving them in the
            # specfied output file.
            evaluations = instances_to_coco_json(outputs["instances"].to("cpu"), d["file_name"])
            with open(output_file, "w") as dest:
                json.dump(evaluations, dest)