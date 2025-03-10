import os
import pandas as pd

def changeScaling(filePath):
    # Read the CSV file
    data = pd.read_csv(filePath)

    # Scaling factors
    old_range = (1 - 0)
    new_range_x = (1280 - 1)
    new_range_y = (720 - 1)

    # Apply scaling to the specified columns
    data["norm_pos_x"] = ((data["norm_pos_x"] - 0) * new_range_x) / old_range + 1
    data["norm_pos_y"] = ((data["norm_pos_y"] - 0) * new_range_y) / old_range + 1

    # Create a new file name
    new_file_path = filePath.replace('.csv', '_new.csv')

    # Save the modified data to a new CSV file
    data.to_csv(new_file_path, index=False)


def main():
    # Set the root directory
    root_dir = 'C:/Users/shach/master/Master/data'  # Update with the correct root directory

    # Iterate over all files in the directory tree
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith("gaze_positions.csv"):
                file_path = os.path.join(root, file)
                changeScaling(file_path)



if "__main__" == __name__:
    main()