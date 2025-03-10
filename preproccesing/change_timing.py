import pandas as pd
import os

def createNewCSV():
    root_dir = os.path.join(os.getcwd(), 'data')  # Update with the correct root directory

    # Iterate over all the files in the directory
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Check if the file is a CSV file
            if file.endswith("gaze_positions_new.csv"):
                # Get the full path to the CSV file
                file_path = os.path.join(root, file)

                # Read the first column of the CSV file into a DataFrame
                df = pd.read_csv(file_path, usecols=[0])

                # Add a new column 'time' that shows the time in minutes
                df['time'] = df.iloc[:, 0] / 60

                # Save the updated DataFrame to a new CSV file in the same directory as the original file
                output_file_path = os.path.join(root, 'turns.csv')
                df.to_csv(output_file_path, index=False, columns=['time'])


def dropNaN():
    root_dir = os.path.join(os.getcwd(), 'data') # Update with the correct root directory
    # itaret over all the files in the directory
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # check if the file is csv
            if file.endswith("gaze_positions_new.csv"):
                # set the file path
                file_path = os.path.join(root, file)
                # read the csv file into a dataframe
                df = pd.read_csv(file_path)
                # drop rows where all columns except the first one have NaN values
                df = df.dropna(subset=df.columns[1:], how='all')
                # save the updated dataframe back to the csv file
                df.to_csv(file_path, index=False)
def main():
    # dropNaN()
    createNewCSV()

if __name__ == "__main__":
    main()
