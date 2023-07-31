import pandas as pd
import numpy as np

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