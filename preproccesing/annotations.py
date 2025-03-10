import pandas as pd
import os
from openpyxl import load_workbook
from tkinter import Tk, filedialog
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk # pip install pillow
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.editor as mp

import glob


class GuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coding GUI")
        self.frame = ttk.Frame(root)
        self.frame.grid(row=0, column=0)
        self.video_label = tk.Label(self.frame, text="Video Player Placeholder")
        self.video_label.grid(row=0, column=0)
        self.thumbnail_pil_label = None  # Hold a reference to the PIL Label

    def update_thumbnail(self, thumbnail_path):
        # Load the thumbnail image
        new_thumbnail_image = Image.open(thumbnail_path)

        # Create a Tkinter-compatible PhotoImage from the PIL image
        new_thumbnail_tk_image = ImageTk.PhotoImage(new_thumbnail_image)

        # If the PIL Label doesn't exist, create it
        if not self.thumbnail_pil_label:
            self.thumbnail_pil_label = tk.Label(self.frame)
            self.thumbnail_pil_label.grid(row=1, column=0)

        # Configure the existing PIL Label to display the new thumbnail image
        self.thumbnail_pil_label.configure(image=new_thumbnail_tk_image)
        self.thumbnail_pil_label.image = new_thumbnail_tk_image  # Keep a reference

        # Release the previous PIL image
        if hasattr(self.thumbnail_pil_label, 'image'):
            del self.thumbnail_pil_label.image

        # Update the reference to the current PIL image
        self.thumbnail_pil_label.image = new_thumbnail_tk_image



def read_excel_sheet(file_path, sheet_name):
    # Load the Excel workbook
    workbook = load_workbook(file_path, read_only=True, data_only=True)

    # Select the desired sheet
    sheet = workbook[sheet_name]

    # Read the entire sheet into a DataFrame
    result_df = pd.DataFrame(sheet.values)

    # Set the column names based on the first row
    result_df.columns = result_df.iloc[0]

    # Drop the first row, which contains the column names
    result_df = result_df[1:]

    # Close the workbook
    workbook.close()

    return result_df


def find_video_path(excel_file_path):
    data_directory = 'C:/Users/shach/Documents/Master/data'

    # Extract participant code from the Excel file path
    participant_code = os.path.basename(excel_file_path).split('_')[0]

    for root, dirs, files in os.walk(data_directory):
        for directory in dirs:
            if participant_code in directory:
                # Construct the search pattern for 'world.mp4' within the participant's directory
                # if the participant is pd, the path will be different because there is ON and OFF
                if excel_file_path.__contains__('ON'):
                    search_pattern = os.path.join(root, directory, '**', 'world_on.mp4')
                else:
                    search_pattern = os.path.join(root, directory, '**', 'world.mp4')

                # Use glob to find the file
                video_files = glob.glob(search_pattern, recursive=True)

                # Return the first found path (if any)
                if video_files:
                    return video_files[0]

    # If the 'world.mp4' file is not found, return None
    return None


def get_video_thumbnail(video_path, save_path='thumbnail.jpg', time_seconds=0.5):
    clip = VideoFileClip(video_path)
    thumbnail = clip.get_frame(time_seconds)
    clip.close()

    # Save the thumbnail image
    mp.ImageSequenceClip([thumbnail], fps=1).write_videofile(save_path, codec='png')

    return save_path
# dict_coding = {'A': 'environment', 'B': 'floor', 'C1': 'near cone 1', 'D1': 'cone 1 itself', 'C2': 'near cone 2', 'D2': 'cone 2 itself'}

def createGui(df, file_path):
    # Create the Tkinter window
    root = tk.Tk()
    app = GuiApp(root)

    # Assuming 'video_path' is the path to the video file
    video_path = find_video_path(file_path)

    # Display video if 'video_path' is available
    if video_path:
        # Get the full path to the thumbnail image
        thumbnail_path = get_video_thumbnail(video_path)

        # Update the thumbnail in the GUI
        app.update_thumbnail(thumbnail_path)

    # Populate the Treeview with coding information
    for col in df.columns:
        app.tree.heading(col, text=col)
    for index, row in df.iterrows():
        app.tree.insert("", tk.END, values=row.tolist())

    # Start the Tkinter event loop
    root.mainloop()



def main():
    root_dir = os.path.join(os.getcwd(), 'data', 'annotations')  # Update with the correct root directory    root = Tk()
    root = Tk()
    root.withdraw()  # Hide the main window

    # Ask the user to select an Excel file
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx;*.xls")],
    )

    if not file_path:
        print("No file selected. Exiting.")
        return

    # Read the Excel file into a dataframe
    df = read_excel_sheet(file_path, 'PL')
    createGui(df, file_path)

if __name__ == "__main__":
    main()


