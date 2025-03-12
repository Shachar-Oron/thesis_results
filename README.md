
# Thesis Results

This repository contains the analysis and results of my thesis project. Some files contain privileged information; therefore, the filenames include the word "copy" at the end, indicating that these are anonymized copies of the original files.

## Structure

This repository contains multiple folders. Below is an explanation of the contents of each folder:

### confidence_at_different_sessions
This folder contains a Python script for analyzing confidence levels across different sessions. Additionally, it includes four reports corresponding to four different walking conditions:
1. **Straight**
2. **Straight_DT** (dual task)
3. **Raiesh** (walking with a 90-degree turn)
4. **Raiesh_DT** (walking with a 90-degree turn & dual task)

### deltas_of_turns
This folder contains Python scripts and Excel files for analyzing the deltas (endpoint - starting point) of gaze positions during 180-degree turns. This analysis was conducted exclusively for the "Straight" session.

The Excel files include:
1. **x_deltas.xlsx & y_deltas_v2.xlsx** – Group statistics and individual results for each turn of each patient. The deltas are calculated from the start to the end of the turn. X refers to horizontal changes, and Y refers to vertical changes in pupil position.
2. **x_deltas_middle.xlsx & y_deltas_middle_v2.xlsx** – Similar to the previous files but analyzing gaze position changes from the middle of the turn, where patients were expected to look at the ground.
3. **Other Python scripts** – Assist in extracting gaze positions recorded during turns and calculating the deltas.
4. **Two R scripts** – Generate plots for individual and group gaze positions.

### straight_walking_gaze_positions
This folder contains all analyses conducted on segments where patients walked in a straight path. The data was extracted from gaze positions recorded between the cones, excluding turns.

1. **gaze_positions_non_data_extraction.py** – Extracts gaze position data for straight walking without turns.
2. **gaze_positions_non_turns_saparate.Rmd & gaze_positions_non_turns_together.Rmd** – R scripts analyzing deviations in gaze positions to determine whether patients looked more to the right or left, up or down.
3. **horizontal_gaze_analysis.py** – Analyzes whether patients looked more up or down while walking straight.
4. **Q-Q_plots folder** – Contains quantile-quantile plots comparing data quantiles with theoretical distributions to assess data normality. A PowerPoint presentation explaining the analysis is included.
5. **STRAIGHT_gaze_analysis_graphs** – Displays results indicating whether patients looked more to the right or left.
6. **straight_walking_vertical_positions** – Similar to the previous analysis but focusing on whether patients looked more up or down.

### preproccesing
This folder contains scripts used for data cleaning, converting machine time to milliseconds, and identifying annotations (files that document events occurring in the experiment videos).

### video_player
MATLAB scripts for building a program that synchronizes and plays two videos (one from a GoPro and one from a Pupil Labs camera) simultaneously from two different viewpoints.

### machine learning
To classify Parkinson’s disease (PD) patients and healthy controls based on pupil dynamics, a deep learning (DL) model was developed and trained on time-series pupil diameter data. This folder contains preprocessing scripts, analyses, and the model implementation.

### pupil dynamics
1. **fft_pupil_size.py** – Computes the Fast Fourier Transform (FFT) on pupil diameter data for each patient in different walking sessions. The FFT decomposes a time-domain signal (pupil diameter changes over time) into its frequency components.
2. **wilcoxone_fft_areas.py** – Performs a statistical test to compare FFT analysis results between groups.
3. **pupil_diameter.py** – Processes data by filtering relevant files based on user-selected criteria, extracting and analyzing pupil diameters with confidence levels, and generating an Excel report with individual and group statistics.




