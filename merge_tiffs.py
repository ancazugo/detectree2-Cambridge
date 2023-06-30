import os
# import dask
# import dask.array as da
import rioxarray as rxr
import xarray as xr
from dotenv import load_dotenv

load_dotenv()

# Directory path containing the GeoTIFF files
folder_path = os.getenv('DATA_FOLDER') + "Cambridge/Aerial_RGB_25cm_2013_32630/"
reference_raster_path = os.getenv('DATA_FOLDER') + "Cambridge/CityCentre_2017_32630.tif"
output_path = os.getenv('DATA_FOLDER') + "Cambridge/CityCentre_2013_32630.tif"

# # Get a list of all GeoTIFF files in the folder
# file_list = [file for file in os.listdir(folder_path) if file.endswith(".tif")]

# # Define a custom dask chunk size
# chunk_size = "256 MiB"  # Adjust the value based on your available memory

# # Load the first GeoTIFF file as the base dataset
# base_ds = rxr.open_rasterio(
#     os.path.join(folder_path, file_list[0]),
#     chunks={"band": 1, "x": chunk_size, "y": chunk_size},
# )

# # Iterate over the remaining GeoTIFF files and merge them into the base dataset
# for file in file_list[1:]:
#     ds = rxr.open_rasterio(
#         os.path.join(folder_path, file),
#         chunks={"band": 1, "x": chunk_size, "y": chunk_size},
#     )
#     base_ds = xr.concat([base_ds, ds], dim="band")

# # Open the reference raster for cropping
# reference_ds = rxr.open_rasterio(reference_raster_path)

# # Extract the bands as separate arrays
# band_arrays = []
# for band in range(3):
#     band_array = base_ds.sel(band=band + 1).data
#     band_arrays.append(band_array)

# # Create a dask array representing the cropped data for each band
# cropped_arrays = []
# for band_array in band_arrays:
#     chunks = da.from_array(band_array).chunks
#     cropped_array = da.from_array(band_array).map_blocks(
#         lambda x: rxr.clip_box(x, *reference_ds.rio.bounds()).data,
#         chunks=chunks,
#         dtype=band_array.dtype,
#     )
#     cropped_arrays.append(cropped_array)

# # Convert the dask arrays to xarray datasets
# cropped_datasets = []
# for band, cropped_array in enumerate(cropped_arrays, start=1):
#     cropped_ds = xr.DataArray(
#         cropped_array,
#         dims=("y", "x"),
#         coords={"y": base_ds.y, "x": base_ds.x},
#         attrs=base_ds.attrs,
#     ).to_dataset(name=f"band{band}")
#     cropped_datasets.append(cropped_ds)

# # Merge the cropped datasets into a single RGB dataset
# cropped_rgb_ds = xr.merge(cropped_datasets)

# # Save the cropped RGB dataset as a new GeoTIFF file
# cropped_rgb_ds.rio.to_raster(output_path)


# Get a list of all GeoTIFF files in the folder
file_list = [file for file in os.listdir(folder_path) if file.endswith(".tif")]

# Load the first GeoTIFF file as the base dataset
base_ds = rxr.open_rasterio(os.path.join(folder_path, file_list[0]))

# Iterate over the remaining GeoTIFF files and merge them into the base dataset
for file in file_list[1:]:
    ds = rxr.open_rasterio(os.path.join(folder_path, file))
    base_ds = xr.concat([base_ds, ds], dim="band")
    
reference_ds = rxr.open_rasterio(reference_raster_path)

# Crop the merged dataset to the extent of the reference raster
cropped_ds = base_ds.rio.clip(reference_ds.rio.bounds())

# Save the merged dataset as a new GeoTIFF file
base_ds.rio.to_raster(output_path)
