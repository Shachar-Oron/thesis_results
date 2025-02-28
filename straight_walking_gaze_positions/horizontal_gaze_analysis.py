import os
import pandas as pd
import matplotlib.pyplot as plt

# Path to the folder containing gaze position files
folder_path = r'C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\new_clean_outputs\non_turns_data'

# Create a directory to save the graphs
output_dir = r'C:\Users\shach\Documents\Shachar-s_Thesis2\דטה בסיבובים\non_turns_data\gaze_data\gaze_analysis_graphs'
os.makedirs(output_dir, exist_ok=True)
i = 1
state = " "

# Process each Excel file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.xlsx'):
        file_path = os.path.join(folder_path, file_name)
        data = pd.read_excel(file_path)

        # Extract patient ID from the file name
        patient_id = file_name.split('_', 2)[2].replace('.xlsx', '')
        if 'EC' in patient_id:
            state = "EC"
        elif 'OFF' in patient_id:
            state = "PD_OFF"
        else:
            state = "PD_ON"
        name = state + "_" + str(i)
        i += 1

        # Use percentiles to determine the "good" range, avoiding extreme values
        lower_percentile = data['norm_pos_x'].quantile(0.1)
        upper_percentile = data['norm_pos_x'].quantile(0.9)

        # Filter out extreme values for the pivot calculation only (data itself remains unchanged)
        filtered_data = data[(data['norm_pos_y'] >= lower_percentile) & (data['norm_pos_y'] <= upper_percentile)]

        # Calculate the new pivot as the middle point between min and max values
        pivot = (filtered_data['norm_pos_x'].min() + filtered_data['norm_pos_x'].max()) / 2

        # Analyze "norm_pos_y" to determine left vs. right gazes based on the new pivot
        left_gazes = data[data['norm_pos_x'] < pivot].shape[0]
        right_gazes = data[data['norm_pos_x'] >= pivot].shape[0]

        # Determine whether the patient looked more left or more right
        if left_gazes > right_gazes:
            result = 'More Left'
        else:
            result = 'More Right'

        # Plot the gaze distribution (original data, without changes)
        plt.figure(figsize=(10, 6))
        plt.hist(data['norm_pos_x'], bins=20, color='skyblue', edgecolor='black')
        plt.title(f'Gaze Analysis for Patient {name}\n{result}', fontsize=14)
        plt.xlabel('norm_pos_x')
        plt.ylabel('Frequency')
        plt.axvline(pivot, color='red', linestyle='--', label=f'Median Pivot ({pivot:.2f})')
        plt.legend()

        # Save the graph
        output_file = os.path.join(output_dir, f'{patient_id}_gaze_analysis.png')
        plt.savefig(output_file)
        plt.close()

        print(f'Graph saved for Patient {patient_id} - {result}')

print("Analysis completed.")
