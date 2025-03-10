import os
import pandas as pd
import numpy as np

def process_gaze_file(file_path, value_column):
    df = pd.read_csv(file_path, low_memory=False)
    total_rows = len(df)
    low_confidence_rows = len(df[df['confidence'] <= 0.7])

    # Count rows outside the range [0,1]
    out_range_count = len(df[(df[value_column] < 0) | (df[value_column] > 1)])
    out_of_range_percentage = (out_range_count / total_rows) * 100 if total_rows > 0 else np.nan

    # Filter data to exclude values outside the range [0,1]
    df_in_range = df[(df[value_column] >= 0) & (df[value_column] <= 1)]

    low_confidence_rows_in_range = len(df_in_range[df_in_range['confidence'] <= 0.7])
    percentage_in_range = (low_confidence_rows_in_range / len(df_in_range)) * 100 if len(df_in_range) > 0 else np.nan

    below_threshold = df_in_range[df_in_range['confidence'] <= 0.7][value_column]
    above_threshold = df_in_range[df_in_range['confidence'] > 0.7][value_column]

    mean_below = below_threshold.mean()
    std_below = below_threshold.std()

    mean_above = above_threshold.mean()
    std_above = above_threshold.std()

    min_below = below_threshold.min()
    max_below = below_threshold.max()

    min_above = above_threshold.min()
    max_above = above_threshold.max()

    return total_rows, out_range_count, out_of_range_percentage, percentage_in_range, mean_below, std_below, mean_above, std_above, min_below, max_below, min_above, max_above

def process_all_files_in_folder(gaze_folder, output_folder, value_column):
    results = []
    for root, dirs, files in os.walk(gaze_folder):
        if 'gaze_positions.csv' in files:
            file_path = os.path.join(root, 'gaze_positions.csv')

            # Extract patient ID from the root path
            path_parts = root.split(os.path.sep)
            patient_id = None
            state = None
            for part in path_parts:
                if part.startswith('EC'):
                    patient_id = part.split('_')[1]
                    state = 'EC'
                    break
                elif part.startswith('PD'):
                    patient_id = part.split('_')[0]
                    if 'off' in root.lower():
                        state = 'OFF'
                    elif 'on' in root.lower():
                        state = 'ON'
                    else:
                        state = None
                    break

            if patient_id is None or state is None:
                continue  # Skip if patient ID or state can't be determined

            patient_id_state = f"{patient_id}_{state}"
            (total_rows, out_range_count, out_of_range_percentage, percentage_in_range, mean_below, std_below, mean_above, std_above, min_below, max_below,
             min_above, max_above) = process_gaze_file(file_path, value_column)
            results.append({
                'Patient_ID_State_below_or_above': f"{patient_id_state}_below0.7",
                'Low_Confidence_Percentage': percentage_in_range,
                'Mean': mean_below,
                'Std': std_below,
                'Min': min_below,
                'Max': max_below,
                'Total_Rows': total_rows,
                'out_range_count': out_range_count,
                'out_of_range_percentage': out_of_range_percentage
            })
            results.append({
                'Patient_ID_State_below_or_above': f"{patient_id_state}_above0.7",
                'Low_Confidence_Percentage': percentage_in_range,
                'Mean': mean_above,
                'Std': std_above,
                'Min': min_above,
                'Max': max_above,
                'Total_Rows': total_rows,
                'out_range_count': out_range_count,
                'out_of_range_percentage': out_of_range_percentage
            })

    return pd.DataFrame(results)

# Function to extract the group names based on filename patterns
def extract_group(filename):
    if "EC" in filename:
        return "EC_" + ("below0.7" if "below0.7" in filename else "above0.7")
    elif "PD" in filename:
        if "_OFF" in filename:
            return "PD_OFF_" + ("below0.7" if "below0.7" in filename else "above0.7")
        elif "_ON" in filename:
            return "PD_ON_" + ("below0.7" if "below0.7" in filename else "above0.7")
    return None

def create_excel_report(df, output_folder, value_type):
    output_file = os.path.join(output_folder, f'gaze_confidence_report_raw_data_{value_type}.xlsx')

    # Create a Pandas Excel writer using XlsxWriter as the engine
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write the first sheet with individual results
        df.to_excel(writer, sheet_name='Individual Results', index=False)

        # Calculate group statistics
        df['Group'] = df['Patient_ID_State_below_or_above'].apply(extract_group)

        # Define the groups
        groups = ['EC_below0.7', 'EC_above0.7', 'PD_OFF_below0.7', 'PD_OFF_above0.7', 'PD_ON_below0.7', 'PD_ON_above0.7']
        group_stats = []

        for group in groups:
            group_df = df[df['Group'] == group]
            if not group_df.empty:
                mean_low_conf_percentage = group_df['Low_Confidence_Percentage'].mean()
                mean_values = group_df['Mean'].mean()
                std_values = group_df['Std'].mean()
                mean_min = group_df['Min'].mean()
                mean_max = group_df['Max'].mean()
                mean_out_of_range = group_df['out_range_count'].mean()
                mean_out_of_range_percentage = group_df['out_of_range_percentage'].mean()
                mean_num_rows = group_df['Total_Rows'].mean()
                group_stats.append({
                    'Group': group,
                    'mean_Low_Confidence_Percentage': mean_low_conf_percentage,
                    'Mean_values': mean_values,
                    'Std_values': std_values,
                    'Mean_Min': mean_min,
                    'Mean_Max': mean_max,
                    'mean_out_of_range': mean_out_of_range,
                    'mean_out_of_range_percentage': mean_out_of_range_percentage,
                    'mean_num_rows': mean_num_rows
                })
            else:
                group_stats.append({
                    'Group': group,
                    'mean_Low_Confidence_Percentage': np.nan,
                    'Mean_values': np.nan,
                    'Std_values': np.nan,
                    'Mean_Min': np.nan,
                    'Mean_Max': np.nan,
                    'mean_out_of_range': np.nan,
                    'mean_out_of_range_percentage': np.nan,
                    'mean_num_rows': np.nan
                })

        group_stats_df = pd.DataFrame(group_stats)

        # Write the second sheet with group statistics
        group_stats_df.to_excel(writer, sheet_name='Group Statistics', index=False)

    print(f"Excel report saved to: {output_file}")

def main():
    gaze_folder = r"C:\Users\shach\Documents\Shachar's_Thesis1\preproccesing_data\data"
    output_folder = r"C:\Users\shach\Documents\Shachar-s_Thesis2\results\confidence"

    results_y_df = process_all_files_in_folder(gaze_folder, output_folder, 'norm_pos_y')
    create_excel_report(results_y_df, output_folder, 'y')

    results_x_df = process_all_files_in_folder(gaze_folder, output_folder, 'norm_pos_x')
    create_excel_report(results_x_df, output_folder, 'x')

if __name__ == "__main__":
    main()
