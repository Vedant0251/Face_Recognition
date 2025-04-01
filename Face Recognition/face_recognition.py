import cv2
import os
import numpy as np
from datetime import datetime
import json
import tkinter as tk
from tkinter import simpledialog

# Create a directory to store reference images if it doesn't exist
if not os.path.exists('reference_images'):
    os.makedirs('reference_images')

# Create a JSON file to store image labels if it doesn't exist
LABELS_FILE = 'reference_images/labels.json'
if not os.path.exists(LABELS_FILE):
    with open(LABELS_FILE, 'w') as f:
        json.dump({}, f)

def load_labels():
    with open(LABELS_FILE, 'r') as f:
        return json.load(f)

def save_labels(labels):
    with open(LABELS_FILE, 'w') as f:
        json.dump(labels, f)

def capture_reference_image():
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Display the frame
        cv2.imshow('Register New Person (Press SPACE to capture, ESC to exit)', frame)
        
        # Wait for key press
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC key
            break
        elif key == 32:  # SPACE key
            # Create a temporary root window for the dialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            # Get name from user
            name = simpledialog.askstring("Input", "Enter person's name:",
                                        parent=root)
            
            if name:  # Only save if a name was provided
                # Save the image with name
                filename = f'reference_images/{name.lower().replace(" ", "_")}.jpg'
                cv2.imwrite(filename, frame)
                
                # Save label
                labels = load_labels()
                labels[filename] = name
                save_labels(labels)
                
                print(f"Reference image saved as {filename} for {name}")
            break
    
    cap.release()
    cv2.destroyAllWindows()

def compare_faces(attendance_callback=None):
    # Load the reference image (most recent one)
    reference_files = os.listdir('reference_images')
    if not reference_files:
        print("No reference images found. Please register a person first.")
        return
    
    # Filter out the labels.json file
    image_files = [f for f in reference_files if f.endswith('.jpg')]
    if not image_files:
        print("No reference images found. Please register a person first.")
        return
    
    # Load all reference images and their labels
    labels = load_labels()
    reference_images = {}
    for img_file in image_files:
        img_path = os.path.join('reference_images', img_file)
        img = cv2.imread(img_path)
        if img is not None:
            reference_images[img_file] = {
                'image': img,
                'name': labels.get(img_file, "Unknown Person")
            }
    
    if not reference_images:
        print("Failed to load reference images")
        return
    
    # Initialize face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    
    # Track attendance to prevent multiple marks
    attendance_marked = set()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Convert frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces_frame = face_cascade.detectMultiScale(gray_frame, 1.3, 5)
        
        # Draw rectangles around faces in the frame
        for (x, y, w, h) in faces_frame:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Compare faces if any faces are detected
        if len(faces_frame) > 0:
            # Get the first face from the frame
            face_frame = gray_frame[faces_frame[0][1]:faces_frame[0][1]+faces_frame[0][3],
                                  faces_frame[0][0]:faces_frame[0][0]+faces_frame[0][2]]
            
            # Compare with all reference images
            for ref_file, ref_data in reference_images.items():
                ref_image = ref_data['image']
                ref_name = ref_data['name']
                
                # Convert reference image to grayscale
                gray_reference = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
                
                # Detect faces in reference image
                faces_reference = face_cascade.detectMultiScale(gray_reference, 1.3, 5)
                
                if len(faces_reference) > 0:
                    # Get the first face from reference image
                    face_reference = gray_reference[faces_reference[0][1]:faces_reference[0][1]+faces_reference[0][3],
                                                  faces_reference[0][0]:faces_reference[0][0]+faces_reference[0][2]]
                    
                    # Resize faces to the same size for comparison
                    face_frame = cv2.resize(face_frame, (100, 100))
                    face_reference = cv2.resize(face_reference, (100, 100))
                    
                    # Compare faces using Mean Squared Error
                    mse = np.mean((face_frame - face_reference) ** 2)
                    
                    # If MSE is below threshold, faces are similar
                    if mse < 2000:
                        # Check if attendance hasn't been marked for this person in this session
                        if ref_name not in attendance_marked:
                            attendance_marked.add(ref_name)
                            cv2.putText(frame, f"Attendance Marked: {ref_name}", 
                                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            if attendance_callback:
                                attendance_callback(ref_name)
                        else:
                            cv2.putText(frame, f"Already Marked: {ref_name}", 
                                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                        break
                    else:
                        cv2.putText(frame, "No Match", (10, 30), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Display the frame
        cv2.imshow('Attendance Marking (Press ESC to exit)', frame)
        
        # Break loop on ESC key
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

def main():
    while True:
        print("\nFace Recognition System")
        print("1. Register New Person")
        print("2. Start Attendance Marking")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            capture_reference_image()
        elif choice == '2':
            compare_faces()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 