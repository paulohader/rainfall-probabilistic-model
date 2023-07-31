import pandas as pd
import numpy as np
import math 

# Define a class to handle the rainfall data
class RainfallData:

    # Define the constructor to initialize the DataFrame and the month map
    def __init__(self, csv_file):
        # Read in the data from the CSV file
        self.df = pd.read_csv(csv_file, delimiter=';', index_col=0)
        # Create a dictionary to map Portuguese month names to month numbers
        self.month_map = { 'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12 }

    # Define a method to reshape the data
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

class LandslideData:

    # Define the constructor to initialize the DataFrame and the month map
    def __init__(self, csv_file):
        # Read in the external data from the CSV file
        self.landslide_df = pd.read_csv(csv_file, delimiter=';')
        
    # Define a method to prepare external data
    def prepare_landslides(self):
        # Convert the date column to datetime type and format it as YYYY-MM-DD
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

# Merge both DataFrames on the date index
rainls_df = reshaped_df.merge(landslide_df2, how='left', on='date') # use landslide_df2 instead of landslide_df.landslide_df

# Print the first 5 rows of the merged DataFrame
print(rainls_df.head(5))


# Define a class to handle the modelling
class Modelling:

    # Define the constructor to initialize the DataFrame and the rainfall column
    def __init__(self, df, rainfall_col):
        # Save the DataFrame as an attribute
        self.df = df
        # Save the rainfall column as an attribute
        self.rainfall_col = rainfall_col

    # Define a method to perform the analysis
    def analyse(self):
        # Get the sample size (total landslides)
        N = landslide_df2['landslides'].count() 
        # Get the number of bins using Sturges rule
        K = round(1 + 3.322 * math.log10(N)) 
        print(K) # K = 10

        # Get the max value of the rainfall data
        max_rainfall = self.df[self.rainfall_col].max()
        print(max_rainfall) 

        # Divide by K to get the rainfall range
        rainfall_range = max_rainfall / K
        print(rainfall_range) 

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

        # Use the cut method to assign each rainfall value to a bin
        self.df['bin'] = pd.cut(self.df[self.rainfall_col], bins= intervals_array)
        print(self.df.head(10))# check the first 10 rows of the df

        # Convert the bin column to a string type
        self.df['bin'] = self.df['bin'].astype(str)

        # Use the value_counts method on the bin column
        df_result = self.df['bin'].value_counts()
        # Convert the result to a df 
        df_result = df_result.to_frame()
        # Reset the index to make the bin column a regular column
        df_result.reset_index(inplace=True)
        # Rename the columns
        df_result.columns = ['interval', 'count']
        
        return df_result


# Create an instance of the Modelling class with rainls_df and 'rainfall' as arguments
modelling_daily = Modelling(rainls_df, 'rainfall')
# Call the analyse method to get the result DataFrame for daily rainfall
df_daily = modelling_daily.analyse()
print(df_daily) # check df

# Create an instance of the Modelling class with rainls_df and 'rainfall_3days' as arguments
modelling_3days = Modelling(rainls_df, 'rainfall_3days')
# Call the analyse method to get the result DataFrame for 3 days rainfall
df_3days = modelling_3days.analyse()
print(df_3days) # check df

# Create an instance of the Modelling class with rainls_df and 'rainfall_7days' as arguments
modelling_7days = Modelling(rainls_df, 'rainfall_7days')
# Call the analyse method to get the result DataFrame for 7 days rainfall
df_7days = modelling_7days.analyse()
print(df_7days) # check df