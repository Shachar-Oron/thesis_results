import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
import os

# Dictionary to store unique patient IDs
patient_id_mapping = {}
next_patient_id = 1  # Start assigning IDs from 1

def get_csv_files(directory):
    """ Collects all CSV file paths from the given directory and its subdirectories. """
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files if file.endswith('.csv')
    ]

def extract_patient_state(file_path):
    """ Extracts the patient state (EC, PD_OFF, PD_ON) from the file name. """
    file_name = os.path.basename(file_path)

    if file_name.startswith("EC_"):
        return "EC", 0  # Elderly Control group (Healthy)
    elif file_name.startswith("PD_OFF_"):
        return "PD_OFF", 1  # Parkinson's without medication
    elif file_name.startswith("PD_ON_"):
        return "PD_ON", 2  # Parkinson's with medication
    else:
        return None, None  # Unknown state


def extract_patient_id_and_filter(file_path):
    """ Extracts an anonymized patient ID and the filter option from the file name. """
    global next_patient_id

    file_name = os.path.basename(file_path)
    parts = file_name.split('_')

    # Extract the patient ID based on the group (EC or PD)
    if parts[0] == "EC":  # EC group
        # Patient ID is after the first underscore for EC
        patient_id = parts[1]
    elif parts[0] == "PD":  # PD group (either PD_ON or PD_OFF)
        # Patient ID is after the second underscore for PD
        patient_id = parts[2]
    else:
        print(f"⚠️ Unrecognized patient type in file: {file_path}")
        return None, None  # Return None if the type is not recognized

    # Ensure patient ID is anonymized by assigning a unique numeric ID
    if patient_id not in patient_id_mapping:
        patient_id_mapping[patient_id] = next_patient_id
        next_patient_id += 1

    # Extract the filter option (e.g., filter1, filter2)
    filter_option = next((part for part in parts if part.startswith("filter")), None)
    if parts[0] == "PD":
        parts2 = patient_id.split('-')
        patient_id = parts2[0]

    return patient_id, filter_option


# Load and process data
def load_and_process_data(file_paths):
    """ Loads CSV files, concatenates them, and prepares features (X) and labels (y). """
    data = []
    labels = []
    patient_ids = []
    filter_options = []

    for file_path in file_paths:
        patient_state, label = extract_patient_state(file_path)
        if patient_state is None:
            print(f"⚠️ Skipping file (unknown patient state): {file_path}")
            continue  # Skip files with unknown labels

        patient_id, filter_option = extract_patient_id_and_filter(file_path)

        df = pd.read_csv(file_path)
        df["patient_state"] = patient_state
        df["label"] = label
        df["patient_id"] = patient_id
        df["filter_option"] = filter_option

        data.append(df)
        labels.append(label)
        patient_ids.append(patient_id)
        filter_options.append(filter_option)

    if not data:
        print("⚠️ No valid CSV files found. Please check the directory.")
        return None, None

    # Concatenate data from all files
    df = pd.concat(data, ignore_index=True)

    # Focus on pupil diameter and encode filter options
    df = df[['pupil_diameter', 'patient_state', 'label', 'patient_id', 'filter_option']]
    df = df.dropna(subset=['pupil_diameter'])

    # One-hot encode filter_option
    filter_dummies = pd.get_dummies(df['filter_option'], prefix='filter')
    df = pd.concat([df, filter_dummies], axis=1)

    # Define features (X) and labels (y)
    X = df.drop(columns=["label", "patient_state", "patient_id", "filter_option"])
    y = df["label"]

    # Normalize the features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # One-hot encode the labels
    y_encoded = to_categorical(y, num_classes=3)

    return X_scaled, y_encoded

# Build the neural network model
def build_model(input_dim):
    """Builds a simple neural network model for classification."""
    model = Sequential()
    model.add(Dense(128, input_dim=input_dim, activation='relu'))
    model.add(Dropout(0.2))  # Dropout layer to prevent overfitting
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))  # Dropout layer to prevent overfitting
    model.add(Dense(32, activation='relu'))
    model.add(Dense(3, activation='softmax'))  # 3 output classes for EC, PD_OFF, PD_ON

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


# Main function to load data, train the model, and evaluate
def main():
    # data_path = r"D:\preprocessing"
    data_path = r"/home/dsi/oronsha/preprocessing"

    # Step 1: Get CSV files
    file_paths = get_csv_files(data_path)
    if not file_paths:
        return

    # Step 2: Load and process data
    X, y = load_and_process_data(file_paths)
    if X is None or y is None:
        return

    # Step 3: Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Step 4: Build the neural network model
    model = build_model(X_train.shape[1])

    # Step 5: Train the model
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

    # Step 6: Evaluate the model
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss}")
    print(f"Test Accuracy: {accuracy}")


if __name__ == "__main__":
    main()
