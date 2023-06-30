import os, yaml
from datetime import datetime
from argparse import ArgumentParser
from timeit import default_timer
from dotenv import load_dotenv
from constants import MODELS
from detectree2.models.train import MyTrainer, setup_cfg, register_train_data
from detectree_addons import read_multiple_rgb
from sweep_config import sweep_config
import wandb
import geopandas as gpd

def train_sweep(site_path, data_name, model_i):

    # Set up input paths
    site_path = os.getenv('DATA_FOLDER') + site_path
    crown_path = site_path + "crowns/tiles_0.25m_160_20_0_train_crowns.shp"
    rgb_path = site_path + "rgb/"
    train_dir = site_path + "train/"


    imgs = read_multiple_rgb(rgb_path)

    # Read in crowns (then filter by an attribute if required)
    crowns = gpd.read_file(crown_path)
    crowns = crowns.to_crs(imgs[0].crs.data)

    # remove_registered_data(data_name)
    register_train_data(train_dir, data_name, val_fold=5)

    # Set the base (pre-trained) model from the detectron2 model_zoo
    time_now = datetime.now().strftime("%Y%m%dT%H%M%S")



    model_name = list(MODELS[model_i].keys())[0]
    base_model = list(MODELS[model_i].values())[0]
    output_dir = os.getenv('DATA_FOLDER') + "0.25m_160_20_0_models/"
    train_out_dir = output_dir + f"{time_now}_{model_name}/"
    # train_out_dir = output_dir + f"{time_now}_{data_name}/"

    trains = (f"{data_name}_train",) # Registered train data
    tests = (f"{data_name}_val",) # Registered validation data

    if model_name == 'coco':
        cfg = setup_cfg(base_model, trains, tests, workers=4, eval_period=100, 
                        max_iter=3000, out_dir=train_out_dir)
    else:
        cfg = setup_cfg(update_model=base_model, trains=trains, tests=tests, workers=4, #base_lr=0.01123,
                        # gamma = 0.2394, warm_iter = 198, weight_decay = 0.03563, backbone_freeze = 4, batch_size_per_im=1007,
                        eval_period=100, max_iter=10000, out_dir=train_out_dir)
        
    cfg_wandb = yaml.safe_load(cfg.dump())

    #initialize the sweep
    #Running this line will ask you to log into your W&B account
    sweep_id = wandb.sweep(sweep_config, project="detectree2-Cambridge")

    def run():
        run = wandb.init(
        # set the wandb project where this run will be logged
            project="detectree2-Cambridge",
            sync_tensorboard=True,
            # track hyperparameters and run metadata
            config = cfg_wandb)

        trainer = MyTrainer(cfg, patience=5)
        trainer.resume_or_load(resume=False)
        trainer.train()
        
    wandb.agent(sweep_id, run, count=50)

if __name__ == "__main__":
    
    parser = ArgumentParser(description="Sea Ice Tiling")
    parser.add_argument("--site_path", default="Cambridge/0.25m_160_20_0_half/", type=str, help="Path to folder where training data is stored")
    parser.add_argument("--data_name", default="city_center", type=str, help="Name of dataset for registration")
    
    parser.add_argument("--model_i", default=0, type=int, help="Index of models in model garden")
    args = parser.parse_args()
    site_path = args.site_path
    data_name = args.data_name
    model_i = args.model_i
    
    load_dotenv()
    
    t_start = default_timer()
    
    train_sweep(site_path, data_name, model_i)

    t_end = default_timer()
    print(f"Training execution time: {(t_end - t_start)/60.0} minutes")
