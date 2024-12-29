<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>README - TOPSIS Method for Raster Data</title>
</head>
<body>
    <h1>README - TOPSIS Method for Raster Data</h1>

    <p>This project implements the TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) method for raster data analysis. The goal is to process multiple raster datasets (e.g., NDVI, EVI, NDWI, NIR, RED, GREEN), normalize them, and apply the TOPSIS method to rank and evaluate the data based on specified criteria. The process includes reading raster files, normalizing the data, applying weights and criterion types (maximize or minimize), and calculating the closeness coefficients for each pixel. The result is saved as a new raster file that contains the closeness values, which can be used for further analysis or decision-making. Required libraries include rasterio, numpy, and matplotlib.</p>

    <p>To use the project, ensure that you have the required libraries installed. Then, modify the file paths to your raster data, adjust the weights and criterion types as needed, and run the script. The output will be a raster file that represents the evaluated results, which can be interpreted or visualized further. This project is ideal for applications in remote sensing, land use analysis, and other fields that involve raster data processing and decision-making based on multiple criteria.</p>

</body>
</html>
