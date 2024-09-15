import os

#pip install opencv-python
import cv2

#pip install cmake
#pip install dlib for python 3.12
import face_recognition
import pandas as pd
from datetime import datetime

#pip install numpy==1.26.0
import numpy as np

#pip install kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout

# Load person details from a text file into a dictionary.
def load_person_details(file_path):
    details = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Each line contains details about a person separated by commas.
            name, age, adhar, vehicle_no, license, image_path = line.strip().split(',')
            details[image_path] = {'name': name, 'age': age, 'adhar': adhar, 'vehicle_no': vehicle_no, 'license': license}
    return details

# Load known faces from images in a directory and encode them for face recognition.
def load_known_faces(directory_path):
    known_faces = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(directory_path, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_faces[filename] = encodings[0]
    return known_faces

# Define the login screen of the app.
class LoginPage(Screen):
    def __init__(self, **kwargs):
        super(LoginPage, self).__init__(**kwargs)
        self.layout = FloatLayout()

        # Title label for the login page.
        self.title = Label(text='ADMIN LOGIN',
                           size_hint=(None, None),
                           size=(400, 60),
                           pos_hint={'center_x': 0.5, 'top': 0.85},
                           font_size='32sp',
                           bold=True,
                           color=(0, 0.5, 0.8, 1))
        self.layout.add_widget(self.title)

        # Username input field.
        self.username = TextInput(hint_text='Username',
                                  size_hint=(None, None),
                                  size=(300, 50),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.6},
                                  padding_y=(10, 10),
                                  background_normal='',
                                  background_color=(1, 1, 1, 1),
                                  foreground_color=(0, 0, 0, 1),
                                  border=(1, 1, 1, 1),
                                  font_size='18sp')
        self.layout.add_widget(self.username)

        # Password input field.
        self.password = TextInput(hint_text='Password',
                                  password=True,
                                  size_hint=(None, None),
                                  size=(300, 50),
                                  pos_hint={'center_x': 0.5, 'center_y': 0.45},
                                  padding_y=(10, 10),
                                  background_normal='',
                                  background_color=(1, 1, 1, 1),
                                  foreground_color=(0, 0, 0, 1),
                                  border=(1, 1, 1, 1),
                                  font_size='18sp')
        self.layout.add_widget(self.password)

        # Login button.
        self.login_button = Button(text='Login',
                                   size_hint=(None, None),
                                   size=(300, 50),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.3},
                                   background_color=(0, 0.5, 1, 1),
                                   color=(1, 1, 1, 1),
                                   font_size='20sp',
                                   bold=True)
        self.login_button.bind(on_press=self.login)
        self.layout.add_widget(self.login_button)

        # Error message label.
        self.error_message = Label(size_hint=(None, None),
                                   size=(300, 30),
                                   pos_hint={'center_x': 0.5, 'center_y': 0.2},
                                   color=(1, 0, 0, 1),
                                   font_size='16sp',
                                   halign='center')
        self.layout.add_widget(self.error_message)

        self.add_widget(self.layout)

    def login(self, instance):
        # Check if the entered username and password are correct.
        username = self.username.text
        password = self.password.text

        if username == '123' and password == '123':
            # Switch to the main screen if login is successful.
            self.manager.current = 'main'
        else:
            # Display an error message if login fails.
            self.error_message.text = 'Invalid username or password!'

# Define the face detection screen of the app.
class FaceDetectionScreen(Screen):
    detected_info = StringProperty("PRESS THE BUTTON TO OPEN CAMERA.")

    def __init__(self, **kwargs):
        super(FaceDetectionScreen, self).__init__(**kwargs)
        self.person_details = load_person_details('assets/person_details.txt')
        self.known_faces = load_known_faces('assets')

        Window.clearcolor = (0.9, 0.9, 0.9, 1)  # Set background color to light gray

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title label for the face detection screen.
        title_label = Label(text="FACE DETECTION APP",
                            size_hint=(1, 0.1),
                            color=(0, 0.5, 0.8, 1),
                            bold=True, font_size='30sp')
        self.layout.add_widget(title_label)

        # Box layout for camera feed.
        self.camera_box = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.image = Image(size_hint=(1, 0.9))
        self.camera_box.add_widget(self.image)

        # Box layout for displaying detection results and buttons.
        self.details_box = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.label = Label(text=self.detected_info,
                           size_hint=(1, 0.8),
                           color=(0, 0, 0, 1),
                           bold=True, font_size='18sp')
        self.details_box.add_widget(self.label)

        # Button to start the camera.
        self.open_camera_button = Button(text="OPEN CAMERA",
                                         size_hint=(0.5, 0.3),
                                         pos_hint={'center_x': 0.5, 'center_y': 1},
                                         background_color=(0, 0.8, 0.8, 1),  # Cyan color
                                         color=(1, 1, 1, 1),
                                         bold=True, font_size='24sp')
        self.open_camera_button.bind(on_press=self.start_camera)
        self.details_box.add_widget(self.open_camera_button)

        # Button to stop the camera.
        self.close_camera_button = Button(text="CLOSE CAMERA",
                                          size_hint=(0.5, 0.3),
                                          pos_hint={'center_x': 0.5, 'center_y': 1},
                                          background_color=(1, 0, 0, 1),  # Red color
                                          color=(1, 1, 1, 1),
                                          bold=True, font_size='24sp')
        self.close_camera_button.bind(on_press=self.stop_camera)
        self.close_camera_button.opacity = 0  # Initially hidden
        self.details_box.add_widget(self.close_camera_button)

        self.layout.add_widget(self.camera_box)
        self.layout.add_widget(self.details_box)

        self.add_widget(self.layout)

        # Initialize an empty list to hold detected people data and a set for unique detections
        self.detected_people_data = []
        self.detected_people_set = set()

    def start_camera(self, instance):
        # Start capturing video from the camera and schedule regular updates.
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)  # Update at 30 FPS
        self.detected_info = "DETECTING FACES..."
        self.label.text = self.detected_info
        self.open_camera_button.opacity = 0
        self.close_camera_button.opacity = 1

    def stop_camera(self, instance):
        # Release the camera and update the UI.
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()
        self.image.texture = None
        self.detected_info = "CAMERA CLOSED."
        self.label.text = self.detected_info
        self.open_camera_button.opacity = 1
        self.close_camera_button.opacity = 0
        # Save detected people data to Excel file when camera is closed
        self.save_to_excel()

    def update(self, dt):
        # Read a frame from the camera and process it.
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.resize(frame, (800, 600))  # Resize frame for display
            face_encodings = face_recognition.face_encodings(frame)

            for face_encoding in face_encodings:
                # Generate a unique identifier for the face encoding
                face_encoding_hash = np.array2string(face_encoding, separator=',').strip()

                if face_encoding_hash not in self.detected_people_set:
                    self.detected_people_set.add(face_encoding_hash)
                    match_found = False
                    for known_image_path, known_encoding in self.known_faces.items():
                        # Compare the detected face encoding with known face encodings
                        results = face_recognition.compare_faces([known_encoding], face_encoding)
                        if results[0]:
                            match_found = True
                            person_info = self.person_details.get(known_image_path, {'name': 'Unknown', 'age': 'Unknown', 'adhar': 'Unknown', 'vehicle_no': 'Unknown', 'license': 'Unknown'})
                            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            detected_info = f"\nFACE DETECTED!\n\nNAME: {person_info['name']}\nAGE: {person_info['age']}\nAADHAR: {person_info['adhar']}\nVEHICLE NO: {person_info['vehicle_no']}\nLICENSE: {person_info['license']}\nTIME: {timestamp}"
                            
                            self.detected_info = detected_info
                            self.label.text = self.detected_info

                            # Store detected person data
                            self.detected_people_data.append({
                                'Name': person_info['name'],
                                'Age': person_info['age'],
                                'Adhar': person_info['adhar'],
                                'Vehicle No': person_info['vehicle_no'],
                                'License': person_info['license'],
                                'Timestamp': timestamp
                            })
                            break

                    if not match_found:
                        self.detected_info = "DETAILS NOT FOUND"
                        self.label.text = self.detected_info

            # Convert frame to texture and update the image widget
            buf1 = cv2.flip(frame, -1)
            buf = buf1.tostring()
            image_texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.image.texture = image_texture

    def save_to_excel(self):
        # Save detected people data to an Excel file.
        if self.detected_people_data:
            df = pd.DataFrame(self.detected_people_data)
            df.to_excel('detected_people.xlsx', index=False, engine='openpyxl')

    def on_stop(self):
        # Ensure the camera is released and data is saved when the app stops.
        if hasattr(self, 'capture') and self.capture.isOpened():
            self.capture.release()
        self.save_to_excel()

# Define the main app class.
class FaceDetectionApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginPage(name='login'))
        sm.add_widget(FaceDetectionScreen(name='main'))
        return sm

# Run the app.
if __name__ == '__main__':
    FaceDetectionApp().run()
