import pandas as pd
import numpy as np
import math 


#######################
#1. Data Transformation
class RainfallData:

    # Define the constructor to initialize the DataFrame and the month map
    def __init__(self, csv_file):
        # Read in the data from the CSV file
        self.df = pd.read_csv(csv_file, delimiter=';', index_col=0)
        # Create a dictionary to map Portuguese month names to month numbers
        self.month_map = { 'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12 }
    
    # 1.1 Reshape the rainfall data
    def reshape(self):
        # Drop the ‘Dia’ columns
        self.df.drop(list(self.df.filter(regex='Dia')), axis=1, inplace=True)
        # Create a list of tuples containing date and rainfall values
        data = [(f'20{col.split("-")[1]}-{self.month_map[col.split("-")[0]]:02d}-{day:02d}', rainfall) for col in self.df.columns for day, rainfall in self.df[col].items()]
        # Create a new DataFrame from the list of tuples
        reshaped_df = pd.DataFrame(data, columns=['date', 'rainfall'])
        # Remove rows with missing rainfall values
        reshaped_df = reshaped_df.dropna(subset=['rainfall'])
        # Save the reshaped DataFrame to a new CSV file
        reshaped_df.to_csv('reshaped_data.csv', index=False)
        
        #################################################################
        #1.1 Data Preparation 
        # Calculating the temporal windows of Rainfall for 3 and 7 days
        
        # Convert the date column to datetime type
        reshaped_df['date'] = pd.to_datetime(reshaped_df['date'])
        # Set the date column as the index
        reshaped_df.set_index('date', inplace=True)
        # Use the rolling method to calculate the sum of 3 days of rainfall
        reshaped_df['rainfall_3days'] = reshaped_df['rainfall'].rolling('3D').sum()
        # Use the rolling method to calculate the sum of 7 days of rainfall
        reshaped_df['rainfall_7days'] = reshaped_df['rainfall'].rolling('7D').sum()
        
        # Return the updated DataFrame
        return reshaped_df

# Create an instance of the RainfallData class with the CSV file name
rainfall_data = RainfallData('raingauge-hb.csv')
# Call the reshape method to get the reshaped DataFrame
reshaped_df = rainfall_data.reshape()
# Print the first 5 rows of the reshaped DataFrame
print(reshaped_df.head(5))

#################################################################
#2. Landslide Data Transformation
class LandslideData:

    # Define the constructor to initialize the DataFrame and the month map
    def __init__(self, csv_file):
        # Read in the external data from the CSV file
        self.landslide_df = pd.read_csv(csv_file, delimiter=';')
        
    # Define a method to prepare external data
    def prepare_landslides(self):
        # Convert the date column to datetime type and format it as YYYY-MM-DD to match Rainfall data date
        self.landslide_df['date'] = pd.to_datetime(self.landslide_df['date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        # Set the date column as the index
        self.landslide_df.set_index('date', inplace=True)
        # Return both DataFrames
        return self.landslide_df, reshaped_df # return both DataFrames

# Create an instance of the RainfallData class with the CSV file name
rainfall_data = RainfallData('raingauge-hb.csv')
# Call the reshape method to get the reshaped DataFrame
reshaped_df = rainfall_data.reshape()
# Print the first 5 rows of the reshaped DataFrame
print(reshaped_df.head(5))


# Create an instance of the LandslideData class with the CSV file name
landslide_df = LandslideData('landslides.csv')
# Call the prepare_landslides method 
landslide_df2, reshaped_df2 = landslide_df.prepare_landslides() # assign to two separate variables

# Convert both date columns to datetime64[ns, UTC]
landslide_df2.index = pd.to_datetime(landslide_df2.index, utc=True) # convert index to datetime64[ns, UTC]
reshaped_df.index = pd.to_datetime(reshaped_df.index, utc=True) # convert index to datetime64[ns, UTC]

# Join the Rainfall and Landslide data in order to get landslide and non-landslide event
# Merge both DataFrames on the date index
rainls_df = reshaped_df.merge(landslide_df2, how='left', on='date') # use landslide_df2 instead of landslide_df.landslide_df

# Print the first 5 rows of the merged DataFrame
print(rainls_df.head(5))


####################################
#3. Rainfall probabilistic modelling

#################
#3.1 Sturges rule
# First of all, we need to define the rainfall ranges
# this procedure allow the probability calculation of each range cause landslides
# Here we will do so through Sturges (K = 1 + 3,322 logN)
# N is the data lenght (total landslides = 471), and K is the number of intervals
class Modelling:
    """A class to handle the modelling of rainfall and landslides data."""

    # Define the constructor to initialize the DataFrame and the rainfall column
    def __init__(self, df, rainfall_col):
        """Initialize the DataFrame and the rainfall column."""
        # Save the DataFrame as an attribute
        self.df = df
        # Save the rainfall column as an attribute
        self.rainfall_col = rainfall_col

    # Define a method to perform the analysis
    def analyse(self):
        """Perform the analysis and return a DataFrame with intervals, counts, landslides and weights."""
        # Get the sample size (total landslides)
        N = landslide_df2['landslides'].count() 
        # Get the number of bins using Sturges rule
        K = round(1 + 3.322 * math.log10(N)) 
        print(K) # K = 10
        
        #####################
        #3.2 Define intervals
        # Get the max value of the rainfall data
        max_rainfall = self.df[self.rainfall_col].max()
        print(max_rainfall) 

        # Divide by K to get the rainfall range
        rainfall_range = max_rainfall / K
        print(rainfall_range) 

        ##########################
        #3.3 Generate the Ranges
        # We need to generate the ranges with the width of 30.23
        # Initialize an empty list to store the intervals
        intervals = [] 
        # Loop from 0 to 10
        for i in range(10):
            # Calculate the lower and upper bounds of the interval
            lower = i * rainfall_range
            upper = (i + 1) * rainfall_range
            # Append the interval as a tuple to the list
            intervals.append((lower, upper))
        print(intervals) # check list of intervals

        # Convert the intervals list into an array of scalars
        intervals_array = np.array(intervals).flatten()
        # Remove the duplicate edges from the array
        intervals_array = np.unique(intervals_array)
        print(intervals_array) # check the intervals array
        
        ############################
        #3.4 Assign rainfall values for its respective ranges
        # Here we build a df to assign the daily rainfall per range
        # Use the cut method to assign each rainfall value to a bin with right=False parameter
        self.df['bin'] = pd.cut(self.df[self.rainfall_col], bins= intervals_array, right=False)
        print(self.df.head(10))# check the first 10 rows of the df

        # Convert the bin column to a string type
        self.df['bin'] = self.df['bin'].astype(str)

        # Use the value_counts method on the bin column with sort=False and dropna=False parameters
        result_df = self.df['bin'].value_counts(sort=False, dropna=False)
        # Convert the result to a df 
        result_df = result_df.to_frame()
        # Rename the index as 'interval'
        result_df.rename_axis('interval', inplace=True)
        # Rename the column as 'count'
        result_df.columns = ['count']
        
        # Count only non-NaN values for each bin using groupby and count methods on landslides column 
        result_df['landslides'] = self.df.groupby('bin')['landslides'].count() 
       
       # Replace NaN values with zeros using fillna method
        result_df.fillna(0, inplace=True)

        # Divide the landslides column by the count column (without NaN values) to get the weight for each bin using / operator
        result_df['weight'] = result_df['landslides'] / result_df['count']
        
        return result_df


############################
#3.5 Assign rainfall-triggering landslides probability for each temporal resolution
# A. Daily probability
# Create an instance of the Modelling class with rainls_df and 'rainfall' as arguments
modelling_daily = Modelling(rainls_df, 'rainfall')
# Call the analyse method to get the result DataFrame for daily rainfall
df_daily = modelling_daily.analyse()
print(df_daily) # check df

# B. 3 days of accumulated rain probability
# Create an instance of the Modelling class with rainls_df and 'rainfall_3days' as arguments
modelling_3days = Modelling(rainls_df, 'rainfall_3days')
# Call the analyse method to get the result DataFrame for 3 days rainfall
df_3days = modelling_3days.analyse()
print(df_3days) # check df

# C. 7 days of accumulated rain probability
# Create an instance of the Modelling class with rainls_df and 'rainfall_7days' as arguments
modelling_7days = Modelling(rainls_df, 'rainfall_7days')
# Call the analyse method to get the result DataFrame for 7 days rainfall
df_7days = modelling_7days.analyse()
print(df_7days) # check df

# 4. Getting the Probability Level
# Define a function to assign the rainfall levels
def assign_rainfall_level(df):
    # Define the labels for the rainfall levels
    labels = ['R1', 'R2', 'R3', 'R4', 'R5']
    # Use the pd.cut function to assign each weight value to a rainfall level
    df['rainfall_level'] = pd.cut(df['weight'], bins=5, labels=labels)
    # Return the updated DataFrame
    return df

# Call the function on df_daily, df_3days and df_7days
df_daily = assign_rainfall_level(df_daily)
df_3days = assign_rainfall_level(df_3days)
df_7days = assign_rainfall_level(df_7days)