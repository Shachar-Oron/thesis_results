import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb


def createGraphs(data, output_dir):
    # Plotting the first column with "norm_pos_x" and confidence
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(data.iloc[:, 0], data['norm_pos_x'], marker='o', label='norm_pos_x')
    plt.scatter(data.iloc[:, 0], data['confidence'], color='red', label='confidence')
    plt.title('First Column with norm_pos_x and Confidence')
    plt.xlabel('First Column')
    plt.ylabel('norm_pos_x')
    plt.legend()

    # Plotting the first column with "norm_pos_y" and confidence
    plt.subplot(2, 1, 2)
    plt.plot(data.iloc[:, 0], data['norm_pos_y'], marker='o', label='norm_pos_y')
    plt.scatter(data.iloc[:, 0], data['confidence'], color='red', label='confidence')
    plt.title('First Column with norm_pos_y and Confidence')
    plt.xlabel('First Column')
    plt.ylabel('norm_pos_y')
    plt.legend()

    plt.tight_layout()

    # Save the plot as a PNG file with a unique name
    file_name = f"graph_{data.iloc[0, 0]}.png"
    file_path = os.path.join(output_dir, file_name)
    plt.savefig(file_path)
    plt.close()  # Close the plot to free up resources


def createHeatMap(data, output_dir):
    plt.figure(figsize=(10, 6))
    sb.heatmap(data.isnull(), cbar=False, cmap='magma')
    plt.title('Heatmap of Missing Values')
    plt.xlabel('Columns')
    plt.ylabel('Rows')

    # Use a combination of timestamp and sanitized column names for the file name
    timestamp = pd.Timestamp.now().strftime('%Y%m%d%H%M%S')
    columns_str = '_'.join(data.columns)

    # Sanitize column names for the file name
    sanitized_columns = ''.join(c if c.isalnum() or c in ['_', '-'] else '_' for c in columns_str)

    # Save the plot as a PNG file with a unique name
    file_name = f"heatmaps_{data.iloc[0, 0]}.png"
    file_path = os.path.join(output_dir, file_name)
    plt.savefig(file_path)
    plt.close()


def main():
    # Set the root directory
    root_dir = 'C:/Users/shach/Documants/Master/data'  # Update with the correct root directory

    # Iterate over all files in the directory tree
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith("gaze_positions_new.csv"):
                file_path = os.path.join(root, file)
                data = pd.read_csv(file_path)
                # Dropping the missing rows.
                data_cleaned = data.dropna(how='any')

                # Create a directory to save PNG files in the same directory as the data file
                output_dir = os.path.join(root, 'graphs_cleaned')
                os.makedirs(output_dir, exist_ok=True)

                createGraphs(data_cleaned, output_dir)

                # # For the second call to createGraphs, add a suffix to the directory name
                # output_dir = os.path.join(root, 'graphs')
                # os.makedirs(output_dir, exist_ok=True)
                #
                # createGraphs(data, output_dir)

                # output_dir = os.path.join(root, 'heatmaps')
                # os.makedirs(output_dir, exist_ok=True)
                # createHeatMap(data, output_dir)

                # output_dir = os.path.join(root, 'heatmaps_cleaned')
                # os.makedirs(output_dir, exist_ok=True)
                # createHeatMap(data_cleaned, output_dir)


if "__main__" == __name__:
    main()
