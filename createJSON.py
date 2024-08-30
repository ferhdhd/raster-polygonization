import json
import os

def main():
    data = []
    filename = "config.json"
    
    # Insert here the path to the folder where the rasters are
    raster_folder = "/home/gbur/Documentos/polygonization-script/raster_og"

    with os.scandir(raster_folder) as raster_files:
        for raster_file in raster_files:
            if raster_file.name.endswith('.tif'):
                frame = {
                    "raster_path": raster_file.path,
                    "vector": ""
                }
                data.append(frame)
    
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

main()