import os
import pandas as pd

def filter_file_path(file_path, group_identifier, option):
    file_path_upper = file_path.upper()
    group_identifier_upper = group_identifier.upper()

    # Option 1: Only "STRIGHT" or "STRAIGHT" and no "DT"
    if option == 1:
        return any(keyword in file_path_upper for keyword in ["STRIGHT", "STRAIGHT"]) and \
               "DT" not in file_path_upper and group_identifier_upper in file_path_upper

    # Option 2: "STRIGHT" or "STRAIGHT" and must have "DT"
    elif option == 2:
        return any(keyword in file_path_upper for keyword in ["STRIGHT", "STRAIGHT"]) and \
               "DT" in file_path_upper and group_identifier_upper in file_path_upper

    # Option 3: "RESH" only
    elif option == 3:
        return "RESH" in file_path_upper and group_identifier_upper in file_path_upper

    # Option 4: "RESH" and must have "DT"
    elif option == 4:
        return "RESH" in file_path_upper and "DT" in file_path_upper and group_identifier_upper in file_path_upper

    return False

def process_patient_data(folders, group_name, max_patients=10, filter_option=1):
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
                            patient_files.append(file_path)
                            processed_patients.add(patient_id)
                            if len(patient_files) >= max_patients:
                                break

    data = []
    for file_path in patient_files:
        df = pd.read_csv(file_path)
        below_07 = df[df['confidence'] < 0.7]['diameter']
        above_07 = df[df['confidence'] >= 0.7]['diameter']
        parts = file_path.split(os.sep)
        ec_index = parts.index("PD") if "PD" in parts else parts.index("EC")
        patient_id = parts[ec_index + 1] if ec_index != -1 and ec_index + 1 < len(parts) else None
        data.append({
            'Patient_ID': patient_id,
            'Group': group_name,
            'Mean_diameter_below0.7': below_07.mean() if not below_07.empty else float('nan'),
            'Std_diameter_below0.7': below_07.std() if not below_07.empty else float('nan'),
            'Mean_diameter_above0.7': above_07.mean() if not above_07.empty else float('nan'),
            'Std_diameter_above0.7': above_07.std() if not above_07.empty else float('nan'),
            'Low_Confidence_Percentage': (below_07.count() / df.shape[0]) * 100 if df.shape[0] > 0 else float('nan')
        })

    return pd.DataFrame(data)

def calculate_group_statistics(df):
    group_stats = df.groupby('Group').agg({
        'Mean_diameter_below0.7': 'mean',
        'Std_diameter_below0.7': 'mean',
        'Mean_diameter_above0.7': 'mean',
        'Std_diameter_above0.7': 'mean',
        'Low_Confidence_Percentage': 'mean'
    }).reset_index()

    group_stats.columns = ['Group', 'Mean_diameter_below0.7', 'Mean_Std_diameter_below0.7',
                           'Mean_diameter_above0.7', 'Mean_Std_diameter_above0.7',
                           'Mean_Low_Confidence_Percentage']

    return group_stats

def main():
    # Directories
    ec_folder = 'D:\\EC'
    pd_folder = 'D:\\PD'
    pd_on_paths = [r"D:\PD\PD01-EF809\ON", r"D:\PD\PD02-MB345\ON", r"D:\PD\PD03-CG657\ON",
                   r"D:\PD\PD04-DG652\ON", r"D:\PD\PD05-TO723\ON", r"D:\PD\PD06-ZH215\ON",
                   r"D:\PD\PD07-YY137\ON", r"D:\PD\PD09-VR470\ON", r"D:\PD\PD10-MO430\ON",
                   r"D:\PD\PD11-AM303\ON"]

    # Ask user to select filter option
    print("Choose a filtering option:")
    print("1: Only 'STRIGHT' or 'STRAIGHT' and no 'DT'")
    print("2: 'STRIGHT' or 'STRAIGHT' and must have 'DT'")
    print("3: Only 'RESH'")
    print("4: 'RESH' and must have 'DT'")
    filter_option = int(input("Enter the filter option (1, 2, 3, or 4): "))

    # Output directory
    output_dir = r'C:\Users\shach\Documents\Shachar-s_Thesis2\results\pupil_diameter'
    os.makedirs(output_dir, exist_ok=True)

    max_patients = 10
    ec_data = process_patient_data(ec_folder, 'EC', max_patients, filter_option)
    pd_off_data = process_patient_data(pd_folder, 'PD_OFF', max_patients, filter_option)
    pd_on_data = process_patient_data(pd_on_paths, 'PD_ON', max_patients, filter_option)

    all_data = pd.concat([ec_data, pd_off_data, pd_on_data], ignore_index=True)
    group_statistics = calculate_group_statistics(all_data)

    # Unique output file based on selected option
    output_file = os.path.join(output_dir, f'pupil_diameter_report_option_{filter_option}.xlsx')
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        all_data.to_excel(writer, sheet_name='Individual Data', index=False)
        group_statistics.to_excel(writer, sheet_name='Group Statistics', index=False)

    print(f"Report saved to: {output_file}")

if __name__ == "__main__":
    main()
