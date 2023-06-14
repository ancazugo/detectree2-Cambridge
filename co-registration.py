import os
from arosics import COREG
from dotenv import load_dotenv
# import geowombat as gw

load_dotenv()

im_reference = os.getenv('DATA_FOLDER') + '/Cambridge/CityCentre_2017_32630.tif'
im_target    = os.getenv('DATA_FOLDER') + '/Cambridge/WV2_2018_32630.tif'

CR = COREG(im_reference, im_target, path_out=os.getenv('DATA_FOLDER') + '/Cambridge/WV2_2018_32630_clipped_arosics.tif')
CR.calculate_spatial_shifts()

# with gw.open(im_target) as target, gw.open(im_reference) as reference:
#     target_shifted = gw.coregister(
#         target=target,
#         reference=reference,
#         ws=(256, 256),
#         r_b4match=1,
#         s_b4match=1,
#         max_shift=5,
#         resamp_alg_deshift='nearest',
#         resamp_alg_calc='cubic',
#         out_gsd=[target.gw.celly, reference.gw.celly],
#         q=True,
#         nodata=(0, 0),
#         CPUs=1,
#     )
    
# print(target_shifted)