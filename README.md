# Face Recognition Attendance System

A Python-based face recognition system for automated attendance marking with a modern graphical user interface. The system uses OpenCV for face detection and comparison, providing an efficient way to manage attendance through facial recognition.

## Features

- 👤 Register new people with their facial data
- 📝 Automated attendance marking through face recognition
- 🎯 Real-time face detection and matching
- 💻 Modern, user-friendly graphical interface
- 📊 Live attendance logging with timestamps
- 🔄 Continuous monitoring with stop functionality

## Requirements

- Python 3.x
- Required packages:
  ```
  opencv-python==4.8.1.78
  numpy==1.24.3
  Pillow==10.0.0
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Face_Recognition.git
   cd Face_Recognition
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application with the graphical interface(to run the whole project):
   ```bash
   python face_recognition_ui.py
   ```

2. For command-line interface(To run only the model):
   ```bash
   python face_recognition.py
   ```

### Features Guide

#### Registering a New Person
1. Click "Register New Person"
2. The camera will open
3. Position the person's face in the frame
4. Press SPACE to capture
5. Enter the person's name when prompted

#### Taking Attendance
1. Click "Start Attendance"
2. The system will automatically detect and recognize faces
3. Attendance is marked automatically when a registered face is recognized
4. The attendance log updates in real-time
5. Click "Stop" to end the attendance session

## Project Structure

NOTE: GUI and face recognition model are placed separately in different files.
- `face_recognition_ui.py`: Main GUI application file.
- `face_recognition.py`: Core face recognition functionality
- `requirements.txt`: List of Python dependencies
- `reference_images/`: Directory storing registered face images
  - `labels.json`: Mapping of image files to person names

## Technical Details

- Uses OpenCV's Haar Cascade Classifier for face detection
- Implements Mean Squared Error (MSE) for face comparison
- Threading support for non-blocking UI operations
- Automatic attendance logging with timestamps
- Persistent storage of registered faces and labels
