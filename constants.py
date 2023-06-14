import os
from dotenv import load_dotenv

load_dotenv()

MODELS = [{'coco': "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"},
          {'paracou': os.getenv('MODELS_FOLDER') + "220723_withParacouUAV.pth"},
          {'randresize': os.getenv('MODELS_FOLDER') + "230103_randresize_full.pth"}]