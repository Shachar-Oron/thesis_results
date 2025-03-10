import os
import pandas as pd
from scipy.stats import mannwhitneyu


# Function to perform Wilcoxon signed-rank test
def perform_mannwhitney(group1, group2, data, column):
    group1_data = data[data['Group'] == group1][column].dropna()
    group2_data = data[data['Group'] == group2][column].dropna()

    # Ensure both groups have data and equal size
    if len(group1_data) > 0 and len(group2_data) > 0:
        # TODO: Perform the Mann-Whitney U test alternative='two-sided'
        stat, p_value = mannwhitneyu(group1_data, group2_data, alternative='greater')
        return stat, p_value
    else:
        return None, None


# Main function to process files and perform analysis
def process_files(folder_path, output_file):
    # Define frequency ranges and comparisons
    frequency_ranges = [(0, 0.1), (0, 0.5), (0, 1), (0, 5), (0, 10)]
    comparisons = [('PD_OFF', 'PD_ON'), ('PD_OFF', 'EC')]

    # Prepare output dataframe
    output_data = []

    for root, dirs, files in os.walk(folder_path):
        for file, freq_range in zip(files, frequency_ranges):
            if file.endswith('.xlsx'):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file} for frequency range: {freq_range}")
                data = pd.read_excel(file_path)
                column = "Area_0_0.1Hz"
                for group1, group2 in comparisons:
                    stat, p_value = perform_mannwhitney(group1, group2, data, column)
                    output_data.append({
                        'Frequency_Range': f"{freq_range}",
                        'Comparison': f'{group1} vs {group2}',
                        'Statistic': stat,
                        'P-Value': p_value
                    })
        # Save results to an Excel file
        output_df = pd.DataFrame(output_data)
        output_df.to_excel(output_file, index=False)

def main():
    folder_path = r'C:\Users\shach\Documents\Shachar-s_Thesis2\results\pupil_diameter\fft_area_results'
    output_file = os.path.join(folder_path, "mannwhitney_test_results.xlsx")
    # Run the process
    process_files(folder_path, output_file)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()