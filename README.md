AI Curl Counter mainly uses Mediapipe and OpenCV to track the number of reps the user did while performing arm curls, along with a customizable encouragement message. 

Aditionally the user is given the option to play the workout music they like by choosing an mp3 file of the track. The song thats currently playing is displayed while the user works out.

**Music Selection:**
   - Ask the user if they want to play workout music.
   - If yes, prompt the user to select a music file.
   - Initialize `pygame` to play the selected music file in a loop.

**Curl Counting Logic:**
   - Extract landmarks for the shoulder, elbow, and wrist.
   - Calculate the angle between these landmarks to determine the arm position.
   - Count repetitions based on the angle (arm up and down movement).
   - Provide real-time feedback on the workout form.

**Timer and Feedback:**
   - Track the elapsed time for the workout.
   - Pause and display a blinking timer when the user is not performing curls.

How to run-
1. Make sure you have the following libraries installed by running the following command in your terminal - ```pip install opencv-python mediapipe numpy pygame``` .
4. Make sure your IDE or environment is given webcam permission.
5. If your camera displays a black screen change the camera index with the "camera_index" variable, setting it to a number which makes your camera work.

