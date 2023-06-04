import os
from datetime import date, datetime
from pathlib import Path
from argparse import ArgumentParser
from timeit import default_timer
from dotenv import load_dotenv

from detectron2.engine import DefaultPredictor
# from detectree2.preprocessing.tiling import tile_data_train, to_traintest_folders, tile_data
from detectree_addons import predict_on_data
# from detectree2.models.predict import predict_on_data
from detectree2.models.train import MyTrainer, setup_cfg, register_train_data, remove_registered_data, predictions_on_data, combine_dicts, get_tree_dicts, load_json_arr
from detectree2.models.outputs import project_to_geojson, stitch_crowns, clean_crowns, to_eval_geojson, clean_predictions
# from detectree2.models.evaluation import site_f1_score2
# from detectron2.utils.visualizer import Visualizer
# from detectron2.evaluation.coco_evaluation import instances_to_coco_json

# from PIL import Image
# import rasterio
# import rioxarray as rxr
# import geopandas as gpd

def predict_on_tiles(run_name, tiles_dir, city='Cambridge'):
    
    # Set up input paths
    models_path = os.getenv('DATA_FOLDER') + "0.25m_160_20_0_models/"
    model_dir = models_path + f"{run_name}/"
    tiles_dir = os.getenv('DATA_FOLDER') + f'/{city}/{tiles_dir}'

    saved_models = list(filter(lambda x: x[-4:] == '.pth', os.listdir(model_dir)))
    trained_model = model_dir + saved_models[-1]

    pred_folder = tiles_dir + f'predictions/{run_name}/predictions/'
    pred_geo_folder = tiles_dir + f'predictions/{run_name}/predictions_geo/'

    # set up config
    cfg = setup_cfg(update_model=trained_model)

    # Predict on all of the tiles
    predict_on_data(tiles_dir, DefaultPredictor(cfg), out_dir=pred_folder)
    project_to_geojson(tiles_dir, pred_folder, pred_geo_folder)
    
    crowns_final = stitch_crowns(pred_geo_folder, 1)
    crowns_final = crowns_final[crowns_final.is_valid]
    crowns_final = clean_crowns(crowns_final, 0.6)
    crowns_final = crowns_final[crowns_final["Confidence_score"] > 0.5]
    # clean = crowns_final.set_geometry(crowns_final.simplify(0.3))
    crowns_final = crowns_final.set_geometry('geometry')
    crowns_final.to_file(model_dir + f"{run_name}_crowns.gpkg")

if __name__ == "__main__":
    
    parser = ArgumentParser(description="Sea Ice Tiling")
    parser.add_argument("--city", default="Cambridge", type=str, choices=["Cambridge", "NY_raw"],
                        help="Origin of the data")
    parser.add_argument("--run_name", default="dandy-sun-104", type=str, help="Model name, usually with wandb standard naming")
    parser.add_argument("--tiles_dir", default="tiles_0.25m_2017_160_20_0/", type=str, help="Origin of the data")
    args = parser.parse_args()
    
    city = args.city
    run_name = args.run_name
    tiles_dir = args.tiles_dir
    load_dotenv()
    
    t_start = default_timer()
    
    predict_on_tiles(run_name, tiles_dir)

    t_end = default_timer()
    print(f"Predicition execution time: {(t_end - t_start)/60.0} minutes")
