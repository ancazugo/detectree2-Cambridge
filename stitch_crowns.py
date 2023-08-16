from detectree2.models.outputs import project_to_geojson, stitch_crowns, clean_crowns, to_eval_geojson, clean_predictions
import geopandas as gpd

# exec(open('drive/Shareddrives/detectree2_Cambridge/scripts/detectree2_addons.py').read())
data_path = "/home/users/acz25/detectree2_Cambridge/data/Cambridge/getmapping-rgb-25cm-2017_5101375/"
crowns = gpd.read_file(data_path + 'Cambridge_full_crowns.gpkg')

# crowns_final = clean_crowns(crowns, 0.5)

import geopandas as gpd
import pandas as pd
from shapely.geometry import shape

def calc_iou(shape1, shape2):
    """Calculate the IoU of two shapes."""
    iou = shape1.intersection(shape2).area / shape1.union(shape2).area
    return iou

def clean_crowns2(crowns: gpd.GeoDataFrame, iou_threshold=0.7, confidence=0.2):
    """Clean overlapping crowns.
    
    Args:
        crowns (gpd.GeoDataFrame): Crowns to be cleaned.
        iou_threshold (float, optional): IoU threshold that determines whether crowns are overlapping.
        confidence (float, optional): Minimum confidence score for crowns to be retained. Defaults to 0.2.

    Returns:
        gpd.GeoDataFrame: Cleaned crowns.
    """
    # Filter any rows with empty or invalid geometry
    crowns = crowns[~crowns.is_empty & crowns.is_valid]
    # Reset the index
    crowns = crowns.reset_index(drop=True)

    # Use spatial join to find overlapping polygons
    overlaps = gpd.sjoin(crowns, crowns, how='inner', op='intersects')

    # Only keep rows where the polygons are different (i.e., not overlapping with itself)
    overlaps = overlaps[overlaps.index_left != overlaps.index_right]

    # Calculate IoU
    overlaps['iou'] = overlaps.apply(lambda x: calc_iou(x.geometry_left, x.geometry_right), axis=1)

    # Filter rows based on IoU threshold
    overlaps = overlaps[overlaps['iou'] > iou_threshold]

    # Sort rows based on Confidence_score and drop duplicates (keep first)
    overlaps = overlaps.sort_values('Confidence_score', ascending=False).drop_duplicates(subset='index_left', keep='first')

    # Check if the most confident is not the initial crown
    overlaps = overlaps[overlaps["iou"] < 1]

    # Remove 'iou' column
    overlaps = overlaps.drop("iou", axis=1)

    # If not already geopandas, convert pandas into back geopandas
    if not isinstance(overlaps, gpd.GeoDataFrame):
        overlaps = gpd.GeoDataFrame(overlaps, crs=crowns.crs)

    # Filter remaining crowns based on confidence score
    if confidence != 0:
        overlaps = overlaps[overlaps["Confidence_score"] > confidence]

    return overlaps.reset_index(drop=True)

crowns_final = clean_crowns2(crowns, 0.5)

crowns_final.to_file(data_path + 'Cambridge_full_crowns_no_overlap2.gpkg')
