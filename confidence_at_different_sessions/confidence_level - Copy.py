from pupil_diameter import filter_file_path
import os
import pandas as pd


def process_gaze_file(file_path, confidence_threshold):
    df = pd.read_csv(file_path, low_memory=False)
    total_rows = len(df)
    low_confidence_rows = len(df[df['confidence'] <= confidence_threshold])
    percentage = (low_confidence_rows / total_rows) * 100
    return percentage

def process_patient_data(folders, group_name, filter_option, max_patients=10):
    patient_files = []
    processed_patients = set()
    group_identifier = 'ON' if group_name == 'PD_ON' else 'OFF' if group_name == 'PD_OFF' else 'EC'

    # Handle multiple folders for 'PD_ON', single for other groups
    folder_list = folders if isinstance(folders, list) else [folders]
    for folder in folder_list:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file == 'pupil_positions.csv':
                    file_path = os.path.join(root, file)
                    if filter_file_path(file_path, group_identifier, filter_option):
                        parts = file_path.split(os.sep)
                        ec_index = parts.index("PD") if "PD" in parts else parts.index("EC")
                        patient_id = parts[ec_index + 1] if ec_index != -1 and ec_index + 1 < len(parts) else None
                        if patient_id and patient_id not in processed_patients:
                            patient_files.append((file_path, patient_id))
                            processed_patients.add(patient_id)
                            if len(patient_files) >= max_patients:
                                break

    # List to store results
    results = []

    # Define confidence thresholds
    confidence_thresholds = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    # Process each file
    for file_path, patient_id in patient_files:
        for threshold in confidence_thresholds:
            percentage = process_gaze_file(file_path, threshold)
            results.append({
                "File_Path": file_path,
                "Patient_ID": patient_id,
                "Confidence_Threshold": threshold,
                "Low_Confidence_Percentage": percentage,
                "Group": group_name
            })

    # Convert results to a DataFrame
    return pd.DataFrame(results)


def create_excel_report(df, output_folder, filter_option):
    output_file = os.path.join(output_folder, f'gaze_confidence_report{filter_option}.xlsx')

    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write the first sheet with individual results
        df.to_excel(writer, sheet_name='Results', index=False)

        # Calculate group statistics grouped by both Group and Confidence_Threshold
        group_stats = df.groupby(['Group', 'Confidence_Threshold']).agg({
            'Low_Confidence_Percentage': ['mean', 'std']
        }).round(2)

        # Rename columns for clarity
        group_stats.columns = ['Mean_Low_Confidence_%', 'Std_Low_Confidence_%']

        # Reset index to make 'Group' and 'Confidence_Threshold' columns
        group_stats = group_stats.reset_index()

        # Sort values by Group and Confidence_Threshold for better readability
        group_stats = group_stats.sort_values(['Group', 'Confidence_Threshold'])

        # Write the second sheet with group statistics
        group_stats.to_excel(writer, sheet_name='Group Statistics', index=False)

    print(f"Report saved to: {output_file}")



def main():
    # Directories
    ec_folder = 'D:\\EC'
    pd_folder = 'D:\\PD'
    pd_on_paths = # add the list of paths here
    # Output directory
    output_dir = r'C:\Users\shach\Documents\Shachar-s_Thesis2\results\confidence\confidence_at_different_sessions'
    os.makedirs(output_dir, exist_ok=True)

    # Get data for each group
    for i in range(1,5):
        filter_option = i
        ec_data= process_patient_data(ec_folder, 'EC', filter_option)
        pd_off_data = process_patient_data(pd_folder, 'PD_OFF', filter_option)
        pd_on_data = process_patient_data(pd_on_paths, 'PD_ON', filter_option)

        # Combine all data into one DataFrame
        all_data = pd.concat([ec_data, pd_off_data, pd_on_data], ignore_index=True)

        # Create an Excel report for the combined data
        create_excel_report(all_data, output_dir, filter_option)

if __name__ == "__main__":
    main()