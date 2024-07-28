import cv2
import mediapipe as mp
import numpy as np
import time
import pygame
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring


mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands


def calculate_angle(a, b, c):
    a = np.array(a)  # First point
    b = np.array(b)  # Mid point
    c = np.array(c)  # End point
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle 


# Curl counter variables
counter = 0 
stage = None
doing_curls = False

# Change the camera index here if your code displays a black screen (try changing it to 0,1,2,3, etc.)
camera_index = 1 #Mine worked with 1

# Ask user if they want to play music
Tk().withdraw() 
play_music = askstring("Workout Music", "Do you want to play your workout music while working out? (yes/no)")


if play_music and play_music.lower() == 'yes':
    #Prompt user to select a music file
    music_file = askopenfilename(title="Select a music file", filetypes=[("Music Files", "*.mp3 *.wav")])

    if not music_file:
        print("No music file selected. Exiting.")
        exit()

    #Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)  #Looping the music, if you want to play it only once, remove the -1.

    #Extract song title
    song_title = music_file.split('/')[-1]
else:
    music_file = None

# Start video capture
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print(f"Error: Could not open camera with index {camera_index}")
    exit()

print("Video capture opened successfully.")

# Initialize timer
start_time = time.time()
elapsed_time = 0
timer_running = False

# Setup MediaPipe instances
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose, \
     mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("Error: Failed to read frame from camera.")
            break
        
        # Recolor image to RGB 
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
      
        # Make detections (pose and hands)
        pose_results = pose.process(image)
        hand_results = hands.process(image)
    
        # Recolor back to BGR 
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Extract pose landmarks (for curl counter)
        try:
            landmarks = pose_results.pose_landmarks.landmark
            

            # Get coordinates
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            
            # Calculate angle (in degrees)
            angle = calculate_angle(shoulder, elbow, wrist)

            
            # Visualize angle (for debugging)
            cv2.putText(image, str(angle), 
                        tuple(np.multiply(elbow, [640, 480]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
            

            
            # Curl counter logic
            if angle > 160:
                stage = "down"
                doing_curls = False
            if angle < 30 and stage == 'down':
                stage = "up"
                counter += 1
                doing_curls = True
                print(counter)

            
            #Feedback on curl form, you can customize this to your liking
            feedback = "Good form!" if angle > 160 else "Keep going!"
            cv2.putText(image, feedback, 
                        (10, 100), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                       
        except Exception as e:
            print(f"Error processing landmarks: {e}")


        
        # Render curl counter
        # Setup status box 
        cv2.rectangle(image, (0, 0), (225, 73), (0, 0, 255), -1)  # Changed color to red (BGR: (0, 0, 255))


        
        #Rep data (counter)
        cv2.putText(image, 'REPS', (15, 12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), 
                    (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        


        #Stage data (up or down)
        cv2.putText(image, 'STAGE', (115, 12),  # Adjusted x-coordinate to fit inside the box
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, 
                    (110, 60),  # Adjusted y-coordinate to fit inside the box
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2, cv2.LINE_AA)
        


        #Timer
        if doing_curls:
            if not timer_running:
                start_time = time.time() - elapsed_time
                timer_running = True
            elapsed_time = time.time() - start_time
        else:
            timer_running = False



        #Blinking effect when not doing curls
        if not doing_curls and int(time.time() * 2) % 2 == 0:
            cv2.putText(image, f'Time: {int(elapsed_time)}s', 
                        (10, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            

        else:
            cv2.putText(image, f'Time: {int(elapsed_time)}s', 
                        (10, 150), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            



        #Display song title if music is playing
        if music_file:
            cv2.putText(image, f'Now Playing: {song_title}', 
                        (10, 200), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            # Add a small music disk icon (you can replace this with an actual image if you have one)
            cv2.circle(image, (300, 210), 10, (255, 255, 255), -1)

        #Render hand landmarks
        mp_drawing.draw_landmarks(image, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))
        
        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if music_file:
        pygame.mixer.music.stop()