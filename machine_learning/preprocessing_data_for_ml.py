import os
import pandas as pd


def filter_file_path(file_path, group_identifier):
    file_path_upper = file_path.upper()
    group_identifier_upper = group_identifier.upper()

    if any(keyword in file_path_upper for keyword in ["STRIGHT", "STRAIGHT"]) and \
            "DT" not in file_path_upper and group_identifier_upper in file_path_upper:
        return 1

    elif any(keyword in file_path_upper for keyword in ["STRIGHT", "STRAIGHT"]) and \
            "DT" in file_path_upper and group_identifier_upper in file_path_upper:
        return 2

    elif "RESH" in file_path_upper and group_identifier_upper in file_path_upper and \
            "DT" not in file_path_upper and group_identifier_upper in file_path_upper:
        return 3

    elif "RESH" in file_path_upper and group_identifier_upper in file_path_upper and \
            "DT" in file_path_upper and group_identifier_upper in file_path_upper:
        return 4

    return -1


def save_filtered_file(file_path, patient_id, group, filter_option):
    """Loads the CSV, filters columns, and saves the new file in D:\preprocessing."""
    # Construct the new filename with filter option
    new_filename = f"{group}_{patient_id}_filter{filter_option}_pupil_positions.csv"
    save_dir = r"D:\preprocessing"
    if new_filename not in os.listdir(save_dir):
        os.makedirs(save_dir, exist_ok=True)

        # Load data and filter only necessary columns
        df = pd.read_csv(file_path, low_memory=False)
        required_columns = ["norm_pos_x", "norm_pos_y", "confidence", "pupil_timestamp", "diameter"]
        df_filtered = df[required_columns]


        save_path = os.path.join(save_dir, new_filename)

        # Save the filtered file
        df_filtered.to_csv(save_path, index=False)
        print(f"Saved: {save_path}")


def process_patient_data(folders, group_name):
    """Finds pupil_positions.csv files, extracts patient IDs, and saves filtered copies."""
    group_identifier = 'ON' if group_name == 'PD_ON' else 'OFF' if group_name == 'PD_OFF' else 'EC'
    folder_list = folders if isinstance(folders, list) else [folders]

    for folder in folder_list:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file == 'pupil_positions.csv':
                    file_path = os.path.join(root, file)
                    filter_option = filter_file_path(file_path, group_identifier)
                    if filter_option == -1:
                        continue
                    parts = file_path.split(os.sep)
                    if "PD" in parts:
                        ec_index = parts.index("PD")
                    elif "EC" in parts:
                        ec_index = parts.index("EC")
                    else:
                        ec_index = -1

                    patient_id = parts[ec_index + 1] if ec_index != -1 and ec_index + 1 < len(parts) else None
                    if patient_id:
                        save_filtered_file(file_path, patient_id, group_name, filter_option)


def main():
    ec_folder = 'D:\\EC'
    pd_folder = 'D:\\PD'
    pd_on_paths = [
        r"D:\PD\PD01-EF809\ON", r"D:\PD\PD02-MB345\ON", r"D:\PD\PD03-CG657\ON",
        r"D:\PD\PD04-DG652\ON", r"D:\PD\PD05-TO723\ON", r"D:\PD\PD06-ZH215\ON",
        r"D:\PD\PD07-YY137\ON", r"D:\PD\PD09-VR470\ON", r"D:\PD\PD10-MO430\ON",
        r"D:\PD\PD11-AM303\ON"
    ]
    process_patient_data(ec_folder, 'EC')
    process_patient_data(pd_folder, 'PD_OFF')
    process_patient_data(pd_on_paths, 'PD_ON')


if __name__ == "__main__":
    main()
