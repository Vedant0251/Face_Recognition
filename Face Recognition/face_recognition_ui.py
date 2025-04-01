import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
from face_recognition import capture_reference_image, compare_faces
from datetime import datetime
import sys

class FaceRecognitionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        
        # Make the window full screen
        try:
            self.root.state('zoomed')  # For Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # For Linux
            except:
                # If neither works, set a large default size
                self.root.geometry("1200x800")
        
        # Configure the root window to expand
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.root.configure(bg='#2c3e50')  # Dark blue background
        
        # Configure style
        style = ttk.Style()
        style.configure('TButton', padding=5, font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 12))
        
        # Create main container with gradient effect
        main_container = ttk.Frame(root, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.grid_rowconfigure(1, weight=1)  # Make the middle row expandable
        
        # Title with custom styling
        title_label = tk.Label(main_container, 
                             text="Face Recognition Attendance System",
                             font=('Helvetica', 32, 'bold'),
                             bg='#2c3e50',
                             fg='#ecf0f1')  # Light gray text
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Create frames for better organization
        left_frame = ttk.Frame(main_container)
        left_frame.grid(row=1, column=0, padx=20, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.grid_rowconfigure(0, weight=1)  # Make video frame expandable
        
        right_frame = ttk.Frame(main_container)
        right_frame.grid(row=1, column=1, padx=20, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.grid_rowconfigure(0, weight=1)  # Make attendance frame expandable
        
        # Video frame with border
        self.video_frame = tk.Label(left_frame, 
                                  bg='#34495e',  # Slightly lighter blue
                                  relief='solid',
                                  borderwidth=2)
        self.video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Status label with custom styling
        self.status_label = tk.Label(left_frame,
                                   text="System Ready",
                                   font=('Helvetica', 14),
                                   bg='#2c3e50',
                                   fg='#ecf0f1')
        self.status_label.grid(row=1, column=0, pady=10)
        
        # Attendance display with scrollbar
        attendance_frame = ttk.LabelFrame(right_frame, text="Attendance Log", padding="10")
        attendance_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        attendance_frame.grid_rowconfigure(0, weight=1)  # Make text area expandable
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(attendance_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.attendance_text = tk.Text(attendance_frame, 
                                     height=20,  # Increased height
                                     width=50,   # Increased width
                                     bg='#34495e',
                                     fg='#ecf0f1',
                                     font=('Helvetica', 12),
                                     yscrollcommand=scrollbar.set)
        self.attendance_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.attendance_text.config(state=tk.DISABLED)
        scrollbar.config(command=self.attendance_text.yview)
        
        # Buttons frame with custom styling
        button_frame = ttk.Frame(main_container)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Custom button styling with different colors for each button
        capture_button_style = {'font': ('Helvetica', 12, 'bold'),
                              'width': 25,
                              'bg': '#27ae60',  # Green
                              'fg': 'white',
                              'relief': 'raised',
                              'padx': 15,
                              'pady': 8}
        
        recognize_button_style = {'font': ('Helvetica', 12, 'bold'),
                                'width': 25,
                                'bg': '#e67e22',  # Orange
                                'fg': 'white',
                                'relief': 'raised',
                                'padx': 15,
                                'pady': 8}
        
        stop_button_style = {'font': ('Helvetica', 12, 'bold'),
                           'width': 25,
                           'bg': '#c0392b',  # Red
                           'fg': 'white',
                           'relief': 'raised',
                           'padx': 15,
                           'pady': 8}
        
        # Capture button
        self.capture_btn = tk.Button(button_frame,
                                   text="Register New Person",
                                   command=self.start_capture,
                                   **capture_button_style)
        self.capture_btn.grid(row=0, column=0, padx=20)
        
        # Start recognition button
        self.recognize_btn = tk.Button(button_frame,
                                     text="Start Attendance",
                                     command=self.start_recognition,
                                     **recognize_button_style)
        self.recognize_btn.grid(row=0, column=1, padx=20)
        
        # Stop button
        self.stop_btn = tk.Button(button_frame,
                                text="Stop",
                                command=self.stop_process,
                                state=tk.DISABLED,
                                **stop_button_style)
        self.stop_btn.grid(row=0, column=2, padx=20)
        
        # Variables
        self.is_running = False
        self.current_process = None
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """Handle window closing event"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "A process is running. Do you want to quit?"):
                self.stop_process()
                self.root.destroy()
        else:
            self.root.destroy()
        
    def update_attendance(self, name):
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            attendance_text = f"{current_time} - {name} marked present\n"
            self.attendance_text.config(state=tk.NORMAL)
            self.attendance_text.insert(tk.END, attendance_text)
            self.attendance_text.see(tk.END)
            self.attendance_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"Error updating attendance: {str(e)}")
        
    def start_capture(self):
        try:
            self.is_running = True
            self.capture_btn.config(state=tk.DISABLED)
            self.recognize_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Registering new person...")
            
            # Start capture in a separate thread
            self.current_process = threading.Thread(target=self.capture_process)
            self.current_process.daemon = True  # Make thread daemon
            self.current_process.start()
        except Exception as e:
            messagebox.showerror("Error", f"Error starting capture: {str(e)}")
            self.stop_process()
    
    def start_recognition(self):
        try:
            self.is_running = True
            self.capture_btn.config(state=tk.DISABLED)
            self.recognize_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Starting attendance marking...")
            
            # Start recognition in a separate thread
            self.current_process = threading.Thread(target=self.recognition_process)
            self.current_process.daemon = True  # Make thread daemon
            self.current_process.start()
        except Exception as e:
            messagebox.showerror("Error", f"Error starting recognition: {str(e)}")
            self.stop_process()
    
    def stop_process(self):
        try:
            self.is_running = False
            self.capture_btn.config(state=tk.NORMAL)
            self.recognize_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="System Ready")
            
            # Wait for the process to finish if it's running
            if self.current_process and self.current_process.is_alive():
                self.current_process.join(timeout=1.0)
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping process: {str(e)}")
    
    def capture_process(self):
        try:
            capture_reference_image()
        except Exception as e:
            messagebox.showerror("Error", f"Error during registration: {str(e)}")
        finally:
            self.root.after(0, self.stop_process)
    
    def recognition_process(self):
        try:
            compare_faces(self.update_attendance)
        except Exception as e:
            messagebox.showerror("Error", f"Error during attendance marking: {str(e)}")
        finally:
            self.root.after(0, self.stop_process)

def main():
    try:
        root = tk.Tk()
        app = FaceRecognitionUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 