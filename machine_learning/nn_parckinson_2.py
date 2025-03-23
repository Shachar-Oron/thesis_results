import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.utils import to_categorical
import os


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
        return "EC", 0  # Healthy Control Group
    elif file_name.startswith("PD_OFF_"):
        return "PD_OFF", 1  # Parkinson's without medication
    elif file_name.startswith("PD_ON_"):
        return "PD_ON", 2  # Parkinson's with medication
    return None, None


def load_and_process_data(file_paths):
    """ Loads CSV files, concatenates them, and prepares features (X) and labels (y). """
    data = []
    labels = []
    for file_path in file_paths:
        patient_state, label = extract_patient_state(file_path)
        if patient_state is None:
            print(f"⚠️ Skipping file (unknown patient state): {file_path}")
            continue
        df = pd.read_csv(file_path)
        df['pupil_timestamp'] = df['pupil_timestamp'] - df['pupil_timestamp'].iloc[0]
        df['label'] = label
        df = df[df['confidence'] > 0.7]  # Filter by confidence
        df = df.dropna()
        data.append(df)
        labels.append(label)

    if not data:
        print("⚠️ No valid CSV files found.")
        return None, None

    df = pd.concat(data, ignore_index=True)
    X = df.drop(columns=['label', 'patient_state'], errors='ignore')  # Remove non-numeric
    y = to_categorical(df['label'].values, num_classes=3)
    X_scaled = StandardScaler().fit_transform(X)
    return X_scaled, y


def build_model(input_dim):
    """Builds a neural network model for classification."""
    model = Sequential([
        Dense(128, input_dim=input_dim, activation='relu'),
        Dropout(0.2),
        Dense(64, activation='relu'),
        Dropout(0.2),
        Dense(32, activation='relu'),
        Dense(3, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def main():
    data_path = r"/home/dsi/oronsha/preprocessing"
    file_paths = get_csv_files(data_path)
    if not file_paths:
        return
    X, y = load_and_process_data(file_paths)
    if X is None or y is None:
        return
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = build_model(X_train.shape[1])
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))
    loss, accuracy = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss}")
    print(f"Test Accuracy: {accuracy}")


if __name__ == "__main__":
    main()
