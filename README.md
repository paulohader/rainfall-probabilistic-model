## Rainfall-triggering Landslide Probabilistic Model 
This project aimed to produce the rainfall induced landslides from a raingauge station in a municipality of the São Paulo State, Brazil. The data is provided in two CSV files: raingauge-hb.csv and landslides.csv.

## Data Transformation
The rainfall data is in a wide format, with each column representing a month and year, and each row representing a day of the month. The rainfall values are in millimeters. The landslide data is in a long format, with each row representing a landslide event, and the columns containing information such as date and location (neighbourhood).

The first step is to reshape the rainfall data into a long format, with each row containing the date and rainfall value for that day. This is done by using the RainfallData class, which has a constructor that takes the CSV file name as an argument, and a method called reshape that performs the reshaping operation. The reshaped data is saved to a new CSV file called reshaped_data.csv.

The second step is to prepare the landslide data for merging with the rainfall data. This is done by using the LandslideData class, which has a constructor that takes the CSV file name as an argument, and a method called prepare_landslides that converts the date column to datetime type and sets it as the index. The method also returns both the landslide and rainfall DataFrames.

## Data Preparation
The next step is to calculate the temporal windows, in which besides daily, the rainfall for 3 and 7 days that are potential time window predictors of landslide occurrence within the climate context of the region. This is done by using the rolling method on the rainfall column of the reshaped DataFrame, and creating two new columns called rainfall_3days and rainfall_7days that contain the sum of rainfall for 3 and 7 days, respectively.

## Data Modelling
The final step is to merge the rainfall and landslide DataFrames on the date index, and perform the probabilistic calculations to find out the relationship between rainfall thresholds and landslide events.

# Probabilistic Rainfall Model
As the probability calculation only includes wet periods, only values > 0.0 mm were considered. In this way it was possible to 
i) perform the Sturges calculation to define the amplitude of the intervals based on the size of the landslide data
ii) count the number of rainfall events within an interval
iii) assign the landslides that occurred within each interval to their respective time window (daily, 3-day cumulative and 7-day cumulative)
iv) Finally, calculate the probability based on R=O/N, where R is the amount of rainfall, O is the number of landslide events within a rainfall interval, and N is the amount of rainfall within an interval for the period between 2000 and 2016.