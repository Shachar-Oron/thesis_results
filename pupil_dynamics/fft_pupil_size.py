import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pupil_diameter import filter_file_path
from scipy.integrate import simpson  # For numerical integration using Simpson's rule


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
                            patient_files.append(file_path)
                            processed_patients.add(patient_id)
                            if len(patient_files) >= max_patients:
                                break

    # List to store processed data
    data = []

    for file_path in patient_files:
        df = pd.read_csv(file_path)

        # Filter rows where confidence >= 0.7
        if 'confidence' in df.columns:
            df = df[df['confidence'] >= 0.7]
        else:
            print(f"Warning: 'confidence' column missing in {file_path}. Skipping this file.")
            continue

        # Extract patient ID
        parts = file_path.split(os.sep)
        ec_index = parts.index("PD") if "PD" in parts else parts.index("EC")
        patient_id = parts[ec_index + 1] if ec_index != -1 and ec_index + 1 < len(parts) else None

        # Append each valid sample as a row in the final dataset
        for _, row in df.iterrows():
            data.append({
                'Patient_ID': patient_id,
                'Group': group_name,
                'Pupil_Diameter': row['diameter']
            })

    return pd.DataFrame(data)



def get_pupil_diameter(ec_folder, pd_folder, pd_on_paths, filter_option):
    # Process EC data
    ec_data = process_patient_data(ec_folder, 'EC', filter_option)

    # Process PD_OFF data
    pd_off_data = process_patient_data(pd_folder, 'PD_OFF', filter_option)

    # Process PD_ON data
    pd_on_data = pd.concat([process_patient_data(folder, 'PD_ON', filter_option) for folder in pd_on_paths], ignore_index=True)

    return ec_data, pd_off_data, pd_on_data


def perform_interactive_fft_analysis(data, output_dir):
    """
    Perform FFT analysis for each patient and save interactive plots using plotly.

    Parameters:
    - data: DataFrame containing columns 'Patient_ID', 'Group', 'Pupil_Diameter'
    - output_dir: Directory to save the interactive HTML plots
    """
    # Group the data by Patient_ID
    grouped_data = data.groupby('Patient_ID')
    patient_ids = data['Patient_ID'].unique()
    fft_results = []

    # Iterate through each patient
    for patient_id, patient_data in grouped_data:
        # Extract pupil diameter values for the current patient
        pupil_sizes = patient_data['Pupil_Diameter'].dropna().values
        if len(pupil_sizes) == 0:
            print(f"No valid pupil diameter data for patient {patient_id}, skipping...")
            continue

        # Get the group of the current patient
        group_name = patient_data['Group'].iloc[0]

        # Sampling frequency (Hz)
        fs = 120

        # Perform FFT
        fft_result = np.fft.fft(pupil_sizes)
        frequencies = np.fft.fftfreq(len(pupil_sizes), d=1 / fs)
        fft_results.append((patient_id, fft_result))

        # Create interactive plot
        fig = go.Figure()

        # Add FFT trace
        fig.add_trace(go.Scatter(
            x=frequencies[:len(frequencies) // 2],
            y=np.abs(fft_result)[:len(fft_result) // 2],
            name='Amplitude',
            line=dict(color='blue', width=2)
        ))

        # Update layout with title and axes labels
        fig.update_layout(
            title=f"FFT of Pupil Size for Patient {patient_id} ({group_name})",
            xaxis_title="Frequency (Hz)",
            yaxis_title="Amplitude",
            showlegend=True,
            hovermode='x',
            # Add buttons for predefined zoom levels
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=0.1,
                    y=1.1,
                    buttons=[
                        dict(label="Full View",
                             method="relayout",
                             args=[{"xaxis.range": [0, fs / 2]}]),
                        dict(label="0-10 Hz",
                             method="relayout",
                             args=[{"xaxis.range": [0, 10]}]),
                        dict(label="0-5 Hz",
                             method="relayout",
                             args=[{"xaxis.range": [0, 5]}]),
                        dict(label="0-1 Hz",
                             method="relayout",
                             args=[{"xaxis.range": [0, 1]}]),
                    ]
                )
            ]
        )

        # Add grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        # Save the interactive plot as HTML
        plot_path = os.path.join(output_dir, f"Interactive_FFT_{patient_id}_{group_name}.html")
        fig.write_html(plot_path)
        print(f"Interactive FFT plot saved for Patient {patient_id}: {plot_path}")
    return fft_results, patient_ids

def make_report_file(fft_results_ec, fft_results_pd_off, fft_results_pd_on,
                     patients_id_ec, patients_id_pd_off, patients_id_pd_on, output_dir, filter_option):
    """
        Create a report file with separate sheets for individual patients and group averages.
        """
    # Create lists for group averages results
    group_averages = []
    # Process EC results
    fft_magnitudes_ec = np.abs(fft_results_ec[1][1])[:len(fft_results_ec[1][1]) // 2]
    group_averages.append({
        'Condition': 'EC',
        'FFT_Mean': np.mean(fft_magnitudes_ec),
        'FFT_STD': np.std(fft_magnitudes_ec)
    })
    # Process PD OFF results
    fft_magnitudes_pd_off = np.abs(fft_results_pd_off[1][1])[:len(fft_results_pd_off[1][1]) // 2]
    group_averages.append({
        'Condition': 'PD_OFF',
        'FFT_Mean': np.mean(fft_magnitudes_pd_off),
        'FFT_STD': np.std(fft_magnitudes_pd_off)
    })
    # Process PD ON results
    fft_magnitudes_pd_on = np.abs(fft_results_pd_on[1][1])[:len(fft_results_pd_on[1][1]) // 2]
    group_averages.append({
        'Condition': 'PD_ON',
        'FFT_Mean': np.mean(fft_magnitudes_pd_on),
        'FFT_STD': np.std(fft_magnitudes_pd_on)
    })

    # Create lists for individual results
    # TODO: check and debug this part
    individual_results = []
    for fft_result in fft_results_ec:
        fft_magnitude = np.abs(fft_result[1])[: len(fft_result[1])//2]
        individual_results.append({
            'Patient_ID': fft_result[0],
            'Condition': 'EC',
            'FFT_Mean': np.mean(fft_magnitude),
            'FFT_STD': np.std(fft_magnitude)
        })
    for fft_result in fft_results_pd_off:
        fft_magnitude = np.abs(fft_result[1])[: len(fft_result[1])//2]
        individual_results.append({
            'Patient_ID': fft_result[0],
            'Condition': 'PD_OFF',
            'FFT_Mean': np.mean(fft_magnitude),
            'FFT_STD': np.std(fft_magnitude)
        })
    for fft_result in fft_results_pd_on:
        fft_magnitude = np.abs(fft_result[1])[: len(fft_result[1])//2]
        individual_results.append({
            'Patient_ID': fft_result[0],
            'Condition': 'PD_ON',
            'FFT_Mean': np.mean(fft_magnitude),
            'FFT_STD': np.std(fft_magnitude)
        })
    # create an excel file with 2 sheets: individual results and group averages
    output_file = os.path.join(output_dir, f'fft_results_report{filter_option}.xlsx')
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write individual results
        df_individual = pd.DataFrame(individual_results)
        df_individual.to_excel(writer, sheet_name='Individual Results', index=False)
        # Write group averages
        df_group = pd.DataFrame(group_averages)
        df_group.to_excel(writer, sheet_name='Group Averages', index=False)


def calculate_area_under_fft(fft_results, patient_ids, frequency_range, output_dir, group_name):
    """
    Calculate the area under the FFT graph for the specified frequency range.
    Save the results for all patients into a new Excel file with two sheets.

    Parameters:
    - fft_results: List of tuples containing (patient_id, fft_result)
    - patient_ids: List of patient IDs
    - frequency_range: Tuple specifying the frequency range (e.g., (0, 0.1))
    - output_dir: Directory to save the Excel file
    - group_name: Group name for the patients (e.g., 'EC', 'PD_ON', 'PD_OFF')
    """
    # Sampling frequency
    fs = 120

    # Create a list to store individual results
    individual_results = []

    for patient_id, fft_result in fft_results:
        # Get absolute FFT values and frequencies
        fft_magnitude = np.abs(fft_result)
        frequencies = np.fft.fftfreq(len(fft_magnitude), d=1 / fs)

        # Filter the frequencies in the specified range
        mask = (frequencies >= frequency_range[0]) & (frequencies <= frequency_range[1])
        filtered_frequencies = frequencies[mask]
        filtered_magnitude = fft_magnitude[mask]

        if len(filtered_frequencies) == 0:
            print(f"Warning: No data points found in the frequency range {frequency_range} for patient {patient_id}")
            area = 0
        else:
            # Calculate the area under the curve using Simpson's rule
            area = simpson(y=filtered_magnitude, x=filtered_frequencies)
            # Normalize the area to be between 0 and 1
            max_possible_area = simpson(
                y=np.ones_like(filtered_frequencies) * np.max(filtered_magnitude),
                x=filtered_frequencies
            )
            area = area / max_possible_area if max_possible_area > 0 else 0


        # Append the result to the list
        individual_results.append({
            'Patient_ID': patient_id,
            'Group': group_name,
            'Area_0_0.1Hz': area
        })

    # Calculate group averages
    df_individual = pd.DataFrame(individual_results)
    group_averages = df_individual.groupby('Group').mean(numeric_only=True).reset_index()
    return df_individual, group_averages


def makefile_area_under_fft_combined(df_dict, output_dir, frequency_range, filter_option):
    """
    Save the combined area under the FFT curve results to a single Excel file.
    :param df_dict: Dictionary containing individual and group averages for all groups.
                    Format: {'group_name': (df_individual, df_statistics)}
    :param output_dir: Directory to save the file.
    :param frequency_range: Frequency range for the analysis.
    :return: None
    """
    # Combine all individual results and group statistics
    combined_individuals = pd.concat(
        [df_dict[group][0].assign(Group=group) for group in df_dict],
        ignore_index=True
    )
    combined_statistics = pd.concat(
        [df_dict[group][1].assign(Group=group) for group in df_dict],
        ignore_index=True
    )

    # Output file path
    output_file = os.path.join(output_dir, f"fft_area_results_{frequency_range}_report_combined{filter_option}.xlsx")

    # Save to Excel
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        # Write combined individual results
        combined_individuals.to_excel(writer, sheet_name='All Individuals', index=False)
        # Write combined statistics
        combined_statistics.to_excel(writer, sheet_name='All Statistics', index=False)

    print(f"Combined area under FFT curve results saved to: {output_file}")


def analyze_mean_pupil_diameter(data_group, group_name):
    """
    Calculate mean pupil diameter across all patients for each time point.

    Parameters:
    - data_group: DataFrame containing pupil diameter data for one group
    - group_name: Name of the group (EC, PD_ON, or PD_OFF)

    Returns:
    - mean_values: Array of mean pupil diameter values
    - fft_result: FFT of mean values
    - n_points: Length of the FFT result
    """
    # Group by Patient_ID to get equal number of samples from each patient
    grouped = data_group.groupby('Patient_ID')
    min_length = grouped.size().min()

    # Get the first min_length samples for each patient
    aligned_data = []
    for _, patient_data in grouped:
        aligned_data.append(patient_data['Pupil_Diameter'].iloc[:min_length].values)

    # Convert to numpy array for efficient computation
    aligned_array = np.array(aligned_data)

    # Calculate mean across patients for each time point
    mean_values = np.mean(aligned_array, axis=0)

    # Perform FFT on mean values
    fft_result = np.fft.fft(mean_values)

    return mean_values, fft_result, len(mean_values)


def plot_group_means(ec_data, pd_off_data, pd_on_data, output_dir, filter_option):
    """
    Create interactive plot comparing mean pupil diameter FFT across groups.

    Parameters:
    - ec_data, pd_off_data, pd_on_data: DataFrames for each group
    - output_dir: Directory to save the output files

    Returns:
    - Dictionary containing FFT results and frequencies for each group
    """
    # Calculate mean values and FFT for each group
    ec_mean, ec_fft, ec_len = analyze_mean_pupil_diameter(ec_data, 'EC')
    pd_off_mean, pd_off_fft, pd_off_len = analyze_mean_pupil_diameter(pd_off_data, 'PD_OFF')
    pd_on_mean, pd_on_fft, pd_on_len = analyze_mean_pupil_diameter(pd_on_data, 'PD_ON')

    # Sampling frequency
    fs = 120

    # Calculate frequencies for each group
    ec_freqs = np.fft.fftfreq(ec_len, d=1 / fs)
    pd_off_freqs = np.fft.fftfreq(pd_off_len, d=1 / fs)
    pd_on_freqs = np.fft.fftfreq(pd_on_len, d=1 / fs)

    # Create interactive plot
    fig = go.Figure()

    # Add traces for each group (only plotting positive frequencies)
    fig.add_trace(go.Scatter(
        x=ec_freqs[:ec_len // 2],
        y=np.abs(ec_fft)[:ec_len // 2],
        name='EC',
        line=dict(color='blue', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=pd_off_freqs[:pd_off_len // 2],
        y=np.abs(pd_off_fft)[:pd_off_len // 2],
        name='PD OFF',
        line=dict(color='red', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=pd_on_freqs[:pd_on_len // 2],
        y=np.abs(pd_on_fft)[:pd_on_len // 2],
        name='PD ON',
        line=dict(color='green', width=2)
    ))

    # Update layout
    fig.update_layout(
        title='FFT of Mean Pupil Diameter Across Groups',
        xaxis_title='Frequency (Hz)',
        yaxis_title='Amplitude',
        showlegend=True,
        hovermode='x',
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.1,
                y=1.1,
                buttons=[
                    dict(label="Full View",
                         method="relayout",
                         args=[{"xaxis.range": [0, fs / 2]}]),
                    dict(label="0-10 Hz",
                         method="relayout",
                         args=[{"xaxis.range": [0, 10]}]),
                    dict(label="0-5 Hz",
                         method="relayout",
                         args=[{"xaxis.range": [0, 5]}]),
                    dict(label="0-1 Hz",
                         method="relayout",
                         args=[{"xaxis.range": [0, 1]}]),
                ]
            )
        ]
    )

    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    # Save the interactive plot
    plot_path = os.path.join(output_dir, f'Interactive_FFT_Group_Means{filter_option}.html')
    fig.write_html(plot_path)

    return {
        'EC': {'fft': ec_fft, 'freqs': ec_freqs, 'length': ec_len},
        'PD_OFF': {'fft': pd_off_fft, 'freqs': pd_off_freqs, 'length': pd_off_len},
        'PD_ON': {'fft': pd_on_fft, 'freqs': pd_on_freqs, 'length': pd_on_len}
    }


def calculate_group_mean_areas(fft_results, frequency_ranges, output_dir, filter_option):
    """
    Calculate areas under the FFT curves for group means and save to Excel.

    Parameters:
    - fft_results: Dictionary containing FFT results and frequencies for each group
    - frequency_ranges: List of tuples containing frequency ranges
    - output_dir: Directory to save the output files
    """
    results = []

    for freq_range in frequency_ranges:
        group_areas = {}

        # Calculate area for each group
        for group_name, group_data in fft_results.items():
            freqs = group_data['freqs']
            fft_vals = group_data['fft']

            # Get indices for the frequency range
            mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
            freq_filtered = freqs[mask]
            fft_filtered = np.abs(fft_vals[mask])

            # Calculate area
            if len(freq_filtered) > 0:
                area = simpson(y=fft_filtered, x=freq_filtered)
            else:
                area = 0
                print(f"Warning: No data points in range {freq_range} for group {group_name}")

            group_areas[group_name] = area

        # Calculate differences between groups
        results.append({
            'Frequency_Range': f"{freq_range[0]}-{freq_range[1]}Hz",
            'EC_Area': group_areas['EC'],
            'PD_OFF_Area': group_areas['PD_OFF'],
            'PD_ON_Area': group_areas['PD_ON'],
            'PD_OFF_vs_EC': group_areas['PD_OFF'] - group_areas['EC'],
            'PD_ON_vs_EC': group_areas['PD_ON'] - group_areas['EC'],
            'PD_ON_vs_PD_OFF': group_areas['PD_ON'] - group_areas['PD_OFF']
        })

    # Create DataFrame and save to Excel
    df_results = pd.DataFrame(results)
    output_file = os.path.join(output_dir, f'group_mean_fft_areas{filter_option}.xlsx')
    df_results.to_excel(output_file, index=False)

    return df_results

def main():
    # Directories
    ec_folder = 'D:\\EC'
    pd_folder = 'D:\\PD'
    pd_on_paths = [r"D:\PD\PD01-EF809\ON", r"D:\PD\PD02-MB345\ON", r"D:\PD\PD03-CG657\ON",
                   r"D:\PD\PD04-DG652\ON", r"D:\PD\PD05-TO723\ON", r"D:\PD\PD06-ZH215\ON",
                   r"D:\PD\PD07-YY137\ON", r"D:\PD\PD09-VR470\ON", r"D:\PD\PD10-MO430\ON",
                   r"D:\PD\PD11-AM303\ON"]
    # Output directory
    output_dir = r'C:\Users\shach\Documents\Shachar-s_Thesis2\results\pupil_diameter\fft_area_results'
    os.makedirs(output_dir, exist_ok=True)
    # Frequency range to calculate area
    frequency_ranges = [(0, 0.1), (0.1, 0.5), (0.5, 1), (1, 5), (5, 10)]

    # Get data for each group
    for i in range(1,5):
        filter_option = i
        ec_data, pd_off_data, pd_on_data = get_pupil_diameter(ec_folder, pd_folder, pd_on_paths, filter_option)
        print("Plotting group means and calculating areas...")
        # fft_results = plot_group_means(ec_data, pd_off_data, pd_on_data, output_dir, filter_option)
        # df_group_areas = calculate_group_mean_areas(fft_results, frequency_ranges, output_dir, filter_option)


        # # Perform interactive FFT analysis for each group
        fft_results_ec, patients_id_ec = perform_interactive_fft_analysis(ec_data, output_dir)
        fft_results_pd_off, patients_id_pd_off =perform_interactive_fft_analysis(pd_off_data, output_dir)
        fft_results_pd_on, patients_id_pd_on =perform_interactive_fft_analysis(pd_on_data, output_dir)
        make_report_file(fft_results_ec, fft_results_pd_off, fft_results_pd_on,
                         patients_id_ec, patients_id_pd_off, patients_id_pd_on, output_dir, filter_option)


        # Calculate areas and save results

        for frequency in frequency_ranges:
            df_ec, ec_statistics = calculate_area_under_fft(fft_results_ec, patients_id_ec, frequency, output_dir, 'EC')
            df_pd_off, pd_off_statistics = calculate_area_under_fft(fft_results_pd_off, patients_id_pd_off, frequency, output_dir, 'PD_OFF')
            df_pd_on, pd_on_statistics = calculate_area_under_fft(fft_results_pd_on, patients_id_pd_on, frequency, output_dir, 'PD_ON')
            # Combine all groups into a dictionary
            df_dict = {
                'EC': (df_ec, ec_statistics),
                'PD_OFF': (df_pd_off, pd_off_statistics),
                'PD_ON': (df_pd_on, pd_on_statistics)
            }
            # Save all results to a single file
            makefile_area_under_fft_combined(df_dict, output_dir, frequency, filter_option)


if __name__ == "__main__":
    main()