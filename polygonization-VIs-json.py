from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsRasterLayer
from osgeo import gdal, ogr
from pathlib import Path
from qgis import processing
import json
import os

def NDVIRaster(raster_file):
    polarized_name = os.path.join(output_folder, raster_file.name.split(".tif")[0] + "-polarized.tif")
    
    lyr1 = QgsRasterLayer(str(raster_file))
    print(polarized_name)
    print(str(raster_file))
    entries = []
    
    band_1 = QgsRasterCalculatorEntry()
    band_1.ref = 'band_1@1'
    band_1.raster = lyr1
    band_1.bandNumber = 5
    entries.append(band_1)
     
    band_2 = QgsRasterCalculatorEntry()
    band_2.ref = 'band_2@1'
    band_2.raster = lyr1
    band_2.bandNumber = 7
    entries.append(band_2)
        
    calc = QgsRasterCalculator(f'((band_2@1 - band_1@1) / (band_2@1 + band_1@1) >= {VEGETATIVE_INDEX_NDVI})', \
    polarized_name, 'GTiff', lyr1.extent(), lyr1.width(), lyr1.height(), entries)
    
    calc.processCalculation()
    
    return polarized_name, 0

def GNDVIRaster(raster_file):
    polarized_name = os.path.join(output_folder, raster_file.name.split(".tif")[0] + "-polarized.tif")
    
    lyr1 = QgsRasterLayer(str(raster_file))
    print(polarized_name)
    print(str(raster_file))
    entries = []
    

    band_1 = QgsRasterCalculatorEntry()
    band_1.ref = 'band_1@1'
    band_1.raster = lyr1
    band_1.bandNumber = 4
    entries.append(band_1)
     
    band_2 = QgsRasterCalculatorEntry()
    band_2.ref = 'band_2@1'
    band_2.raster = lyr1
    band_2.bandNumber = 7
    entries.append(band_2)
        
    calc = QgsRasterCalculator(f'((band_2@1 - band_1@1) / (band_2@1 + band_1@1) >= {VEGETATIVE_INDEX_GNDVI})', \
    polarized_name, 'GTiff', lyr1.extent(), lyr1.width(), lyr1.height(), entries)
    
    calc.processCalculation()
    
    return polarized_name, 1

def SAVIRaster(raster_file):
    polarized_name = os.path.join(output_folder, raster_file.name.split(".tif")[0] + "-polarized.tif")
    
    lyr1 = QgsRasterLayer(str(raster_file))
    print(polarized_name)
    print(str(raster_file))
    entries = []
    

    band_1 = QgsRasterCalculatorEntry()
    band_1.ref = 'band_1@1'
    band_1.raster = lyr1
    band_1.bandNumber = 1
    entries.append(band_1)
     
    band_2 = QgsRasterCalculatorEntry()
    band_2.ref = 'band_2@1'
    band_2.raster = lyr1
    band_2.bandNumber = 7
    entries.append(band_2)
        
    calc = QgsRasterCalculator(f'(1.5 * ((band_2@1 - band_1@1) / (band_2@1 + band_1@1 + 0.5)) >= {VEGETATIVE_INDEX_SAVI})', \
    polarized_name, 'GTiff', lyr1.extent(), lyr1.width(), lyr1.height(), entries)
    
    calc.processCalculation()
    
    return polarized_name, 2

def clipRaster(polarized_name, vector_path):
    raster = gdal.Open(polarized_name)

    options = gdal.WarpOptions(cutlineDSName=vector_path, cropToCutline=True, dstNodata=0)
    gdal.Warp(polarized_name, raster, options=options)

    raster = None
    
def polygonizeRaster(polarized_name, opt):
    raster = gdal.Open(polarized_name)
    
    polygonized_name = polarized_name.split("polarized.tif")[0]
    
    if opt == 0:
        polygonized_name += "polygonized-NDVI.shp"
    elif opt == 1:
        polygonized_name += "polygonized-GNDVI.shp"
    elif opt == 2:
        polygonized_name += "polygonized-SAVI.shp"

    band = raster.GetRasterBand(1)
    band.SetNoDataValue(0)

    mask_band = band.GetMaskBand()

    driver = ogr.GetDriverByName('ESRI Shapefile')

    out_ds = driver.CreateDataSource(polygonized_name)
    out_layer = out_ds.CreateLayer('polygons', geom_type=ogr.wkbPolygon)

    field_def = ogr.FieldDefn('DN', ogr.OFTInteger)
    out_layer.CreateField(field_def)

    gdal.Polygonize(band, mask_band, out_layer, 0)

    out_ds = None
    raster = None
    
def main():
    
    with open(json_file, 'r') as file:
        data = json.load(file)
    
    # Opens the directory and saves its files in a list
    for item in data:
        raster_file = Path(item['raster_path'])
        vector_path = item['vector']
        if raster_file.name.endswith(".tif"):
            # Just change this line function name to use a different VI (NDVIRaster, GNDVIRaster or SAVIRaster)
            polarized_name, opt = NDVIRaster(raster_file)
            print("raster polarized")
            clipRaster(polarized_name, vector_path)
            print("raster clipped")
            polygonizeRaster(polarized_name, opt)
            print("raster polygonized")
            os.remove(polarized_name)

VEGETATIVE_INDEX_NDVI = 0.60
VEGETATIVE_INDEX_GNDVI = 0.60
VEGETATIVE_INDEX_SAVI = 0.60

json_file = "/home/gbur/Documentos/scripts-qgis/config.json"
output_folder = "/home/gbur/Documentos/polygonization-script/raster_polygonized/"

main()