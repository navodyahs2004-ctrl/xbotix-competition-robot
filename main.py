import os
import sys
import argparse
import glob
import time
import gpiozero ######## only install RP
import serial

import cv2
import numpy as np
from ultralytics import YOLO #########  only install RP

#======================================================================================================================================================================
import RPi.GPIO as GPIO


import Task_1
import Task_2
import Task_3
import Task_4


# --- Connect to Arduino Nano (adjust COM port if needed) ---
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# GPIO pin numbers where servos are connected
SERVO1_PIN = 17    
SERVO2_PIN = 27
SERVO3_PIN = 22

SERVO4_PIN = 5    #For a gate

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO1_PIN, GPIO.OUT)
GPIO.setup(SERVO2_PIN, GPIO.OUT)
GPIO.setup(SERVO3_PIN, GPIO.OUT)

GPIO.setup(SERVO4_PIN, GPIO.OUT)

# Create PWM objects with 50Hz frequency (standard for servos)
servo1 = GPIO.PWM(SERVO1_PIN, 50)
servo2 = GPIO.PWM(SERVO2_PIN, 50)
servo3 = GPIO.PWM(SERVO3_PIN, 50)

servo4 = GPIO.PWM(SERVO4_PIN, 50)

servo1.start(0)
servo2.start(0)
servo3.start(0)

servo4.start(0)


# Helper function to convert angle (0-180) to PWM duty cycle
# Helper function to convert angle (0ï¿½180ï¿½) to PWM duty cycle

# def move_servo_smooth(servo, angle):
#     duty = 2 + (angle / 18)   # Convert angle to duty cycle
#     servo.ChangeDutyCycle(duty)
#     time.sleep(0.03)   

def move_servo_smooth(servo, angle):
    duty = 2 + (angle / 18)
    servo.ChangeDutyCycle(0)
    time.sleep(0.02)
    servo.ChangeDutyCycle(duty)
    time.sleep(0.03)



#======================================================================================================================================================================


### Set user-defined parameters and program parameters

# User-defined parameters
model_path = 'my_model_ncnn_model'	# Path to model file or folder
cam_source = 'picamera0'				# Options: 'usb0' for USB camera, 'picamera0' for Picamera
min_thresh = 0.5 					# Minimum detection threshold
resW, resH = 1280, 720				# Resolution to run camera at
record = False						# Enables recording if True


# Define box coordinates where we want to look for a person. If a person is present in this box for enough frames, toggle GPIO to turn light on.
# pbox_xmin = 540      #1280×720
# pbox_ymin = 160
# pbox_xmax = 760
# pbox_ymax = 450


pbox_xmin = 1384      # for ful res 3280 × 2464
pbox_ymin = 548
pbox_xmax = 1948
pbox_ymax = 1540


# Set detection bounding box colors (using the Tableu 10 color scheme)
bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

# Check if model file exists and is valid
if (not os.path.exists(model_path)):
    print('ERROR: Model path is invalid or model was not found.')
    sys.exit()


# Load YOLO model
print("Loading YOLO model...")
model = YOLO(model_path, task='detect')
labels = model.names
print("Model loaded successfully")


#object in model
__red_box_ = 'SSD'
__blue_box_ = 'wallet'
__square_ = 'square'
__red_light_ = 'SSD'
__green_light_ = 'pen'
__off_light_ = 'wallet'
__red_ball_ = 'pen'
__green_ball_ = 'SSD' 
################################################## for distance ###############################################################################################################

############ for distance (add object real width)======================================================================================================
object_widths = {
    __red_box_: 20,
    __blue_box_: 20,
    __square_: 20,
    __off_light_: 20,
    __red_ball_:20,
    __green_ball_: 20,
}

# Approximate focal length for your webcam
FOCAL_LENGTH = 600

# 4. Function to calculate distance
def calculate_distance(focal_length, real_width, pixel_width):
    if pixel_width == 0:
        return 0
    return (real_width * focal_length) / pixel_width


#################################################################################################################################################################



# Set up recording
if record:
    record_name = 'demo6.avi'
    record_fps = 5
    recorder = cv2.VideoWriter(record_name, cv2.VideoWriter_fourcc(*'MJPG'), record_fps, (resW,resH))


# Initialize Picamera or USB camera depending on user input
if 'usb' in cam_source:
    cam_type = 'usb'
    cam_idx = int(cam_source[3:])
    cam = cv2.VideoCapture(cam_idx)
    ret = cam.set(3, resW)
    ret = cam.set(4, resH)

# elif 'picamera' in cam_source:
#     from picamera2 import Picamera2
#     cam_type = 'picamera'
#     cam = Picamera2()
#     cam.configure(cam.create_video_configuration(main={"format": 'XRGB8888', "size": (resW, resH)}))
#     cam.start()




elif 'picamera' in cam_source:                    ############ this part increse the cap area of picamera
    from picamera2 import Picamera2
    cam_type = 'picamera'
    cam = Picamera2()

    # ? Use full sensor resolution for maximum capture area
    full_res = cam.sensor_resolution  # get full sensor size automatically
    cam_config = cam.create_video_configuration(
        main={"format": 'XRGB8888', "size": full_res}   
    )
    cam.configure(cam_config)

    # ? Ensure no cropping (full zoom area)
    cam.zoom = (0.0, 0.0, 1.0, 1.0)

    cam.start()

else:
    print('Invalid input for cam_source variable! Use "usb0" or "picamera0". Exiting program.')
    sys.exit()


# Initialize frame rate variables 
avg_frame_rate = 0
frame_rate_buffer = []
fps_avg_len = 200

# Initialize control and status variables
red_box_detections = 0
blue_box_detections = 0

square_detections = 0

green_light_detections =  0
red_light_detections = 0
off_light_detections = 0

red_ball_detections = 0
green_ball_detections = 0



######## Serial communication variables ##########################################################################################
Turn = 0
Turn_timer = time.perf_counter()
prev_Turn = Turn

move_opposite = 0
move_opposite_timer = time.perf_counter()
prev_move_opposite = move_opposite


gpio_state = 0
gpio_state_timer = time.perf_counter()
DEBOUNCE_TIME = 0.5  # 0.5 seconds
prev_gpio_state = gpio_state

rotate = -1
rotate_timer = time.perf_counter()
prev_rotate = rotate
################################################################################################################################

# ===================== PUSH BUTTON SETUP ======================
BTN1 = 6
BTN2 = 13
BTN3 = 19
BTN4 = 26
BTN5 = 21

GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Debounce time
BUTTON_DEBOUNCE = 0.25
last_button_press = time.time()

# Current task number
current_task = 1
###############################################################

row1 = []
row2 = []



####### Arduino code upload part ##################################
# PORT of your Nano
PORT = "/dev/ttyUSB0"

def upload_sketch(sketch_name):
    arduino.close()   # close serial
    time.sleep(0.5)
    os.system(f"arduino-cli compile --fqbn arduino:avr:nano {sketch_name}")
    os.system(f"arduino-cli upload -p {PORT} --fqbn arduino:avr:nano {sketch_name}")
    time.sleep(1)
    arduino.open()    # open again



if __name__ == "__main__":
    try:
        ### Begin main inference loop
        while True:

            t_start = time.perf_counter()

            # Grab frame from USB camera or Picamera (depending on user selection)
            if cam_type == 'usb':
                ret, frame = cam.read()

            elif cam_type == 'picamera':
                frame_bgra = cam.capture_array()
                frame = cv2.cvtColor(np.copy(frame_bgra), cv2.COLOR_BGRA2BGR) # Remove alpha channel

            # Check to make sure frame was received
            if (frame is None):
                print('Unable to read frames from the camera. This indicates the camera is disconnected or not working. Exiting program.')
                break



            ### Run inference on frame and parse detections
            
            # Run inference on frame with tracking enabled (tracking helps object to be consistently detected in each frame)
            results = model.track(frame, verbose=False)

            # Extract results
            detections = results[0].boxes

            # Initialize array to hold locations of object detections
            red_box_locations = []    ### for red box
            blue_box_locations = []   ### for blue box

            square_locations = []

            green_light_locations = []
            red_light_locations = []
            off_light_locations = []

            red_ball_locations = []   #####for red ball
            green_ball_locations = [] ###for green ball

            # adding distance measurement to list
            object_distances = {}

            red_box_dis = 1000   # default "far" distance
            blue_box_dis = 1000  # default "far" distance

            square_dis = 1000

            red_light_dis = 1000
            green_light_dis = 1000
            off_light_dis = 1000

            red_ball_dis = 1000
            green_ball_dis = 1000


            # ===================== CHECK BUTTON PRESS =====================
            now = time.time()

            if GPIO.input(BTN1) == 0 and now - last_button_press > BUTTON_DEBOUNCE:
                current_task = 1
                print("Button 1 pressed → Switching to TASK 1")
                last_button_press = now

            if GPIO.input(BTN2) == 0 and now - last_button_press > BUTTON_DEBOUNCE:
                current_task = 2
                print("Button 2 pressed → Switching to TASK 2")
                last_button_press = now

            if GPIO.input(BTN3) == 0 and now - last_button_press > BUTTON_DEBOUNCE:
                current_task = 3
                print("Button 3 pressed → Switching to TASK 3")
                last_button_press = now

            if GPIO.input(BTN4) == 0 and now - last_button_press > BUTTON_DEBOUNCE:
                current_task = 4
                print("Button 4 pressed → Switching to TASK 4")
                last_button_press = now

            if GPIO.input(BTN5) == 0 and now - last_button_press > BUTTON_DEBOUNCE:
                current_task = 5
                print("Button 5 pressed → Switching to TASK 5")
                last_button_press = now
            # =============================================================



            

            for i in range(len(detections)):

                # Get bounding box coordinates
                xyxy_tensor = detections[i].xyxy.cpu()
                xyxy = xyxy_tensor.numpy().squeeze()
                xmin, ymin, xmax, ymax = xyxy.astype(int)
                
                # Calculate center coordinates
                cx = int((xmin + xmax)/2)
                cy = int((ymin + ymax)/2)

                # Get class ID, name, and confidence
                classidx = int(detections[i].cls.item())
                classname = labels[classidx]
                conf = detections[i].conf.item()


                # Draw box if confidence is high enough
                if conf > 0.5:
                    color = bbox_colors[classidx % 10]
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                    label = f'{classname}: {int(conf*100)}%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                    label_ymin = max(ymin, labelSize[1] + 10)
                    cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED)
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                    # ==============================
                    # Distance measurement 
                    # ==============================
                    if classname in object_widths:
                        pixel_width = xmax - xmin
                        distance = calculate_distance(FOCAL_LENGTH, object_widths[classname], pixel_width)
                        object_distances[classname] = distance  # store distance
                        cv2.putText(frame, f"{int(distance)} cm",
                                    (xmin, ymax + 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4)



                    # If this object is a person, append their coordinates to running list of person detections
                    if classname == __red_box_:  
                        red_box_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*red_box_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __red_box_ in object_distances:
                            red_box_dis = object_distances[__red_box_]


                    if classname == __blue_box_:     
                        blue_box_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*blue_box_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __blue_box_ in object_distances:
                            blue_box_dis = object_distances[__blue_box_]

                    
                    if classname == __square_: 
                        square_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*square_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __square_ in object_distances:
                            square_dis = object_distances[__square_]


                    if classname == __red_light_:  
                        red_light_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*red_light_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __red_light_ in object_distances:
                            red_light_dis = object_distances[__red_light_]


                    if classname == __green_light_: 
                        green_light_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*green_light_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __green_light_ in object_distances:
                            green_light_dis = object_distances[__green_light_]


                    if classname == __off_light_:  
                        off_light_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*off_light_detections 
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __off_light_ in object_distances:
                            off_light_dis = object_distances[__off_light_]


                    if classname == __red_ball_:    
                        red_ball_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*red_ball_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1) 
                        if __red_ball_ in object_distances:
                            red_ball_dis = object_distances[__red_ball_]


                    if classname == __green_ball_:
                        green_ball_locations.append([cx, cy])
                        # Draw a cirle there too (and make it change color based on number of consecutive detections)
                        color_intensity = 30*green_ball_detections
                        cv2.circle(frame, (cx, cy), 7, (0,color_intensity,color_intensity), -1)
                        if __green_ball_ in object_distances:
                            green_ball_dis = object_distances[__green_ball_]

        
            print("=== XBOTIX 2025 AUTONOMOUS RUN ===")
            if current_task == 1:
                print("=== TASK 1: BOX DETECTION AND SERVO CONTROL ===")
                gpio_state, red_box_detections, blue_box_detections,current_task = Task_1.Task_1_1(red_box_dis, blue_box_dis, current_task, red_box_locations, blue_box_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth, upload_sketch, gpio_state, red_box_detections, blue_box_detections)
                
            if current_task == 1.2:   
                gpio_state, red_box_detections, blue_box_detections,current_task = Task_1.Task_1_2(red_box_dis, blue_box_dis, current_task, red_box_locations, blue_box_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth,upload_sketch, gpio_state, red_box_detections, blue_box_detections)

            if current_task == 1.3:
                gpio_state, square_detections, current_task, Turn, move_opposite = Task_1.Task_1_3(square_dis, current_task, square_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth,upload_sketch, gpio_state, square_detections)



            if current_task == 2:
                print("=== TASK 2: LIGHT DETECTION AND SERVO CONTROL ===")
                gpio_state, green_light_detections, red_light_detections, off_light_detections,current_task, row1 = Task_2.Task_2_1(green_light_dis, red_light_dis, off_light_dis, current_task, green_light_locations, red_light_locations, off_light_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth, upload_sketch, gpio_state, green_light_detections, red_light_detections, off_light_detections)


            
            if current_task == 3:
                #print("----------------------------------------------------------------", row1)
                print("=== TASK 3: BALL DETECTION AND SERVO CONTROL ===")
                gpio_state, red_ball_detections, green_ball_detections,current_task, row2 = Task_3.Task_3(current_task, red_ball_locations, green_ball_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3,servo4, move_servo_smooth,upload_sketch, gpio_state, red_ball_detections, green_ball_detections)



            if current_task == 4:
                print("=== TASK 4: BALL DETECTION AND SERVO CONTROL ===")
                rotate  = Task_4.Task_4(row1, row2, servo4, move_servo_smooth, upload_sketch)


            #print("=== ALL TASKS COMPLETED ===")


            if gpio_state != prev_gpio_state:
                if time.perf_counter() - gpio_state_timer > DEBOUNCE_TIME:
                    arduino.write(f"{gpio_state}\n".encode())
                    prev_gpio_state = gpio_state
                    gpio_state_timer = time.perf_counter()

            if Turn != prev_Turn:
                if time.perf_counter() - Turn_timer > DEBOUNCE_TIME:
                    arduino.write(f"{Turn}\n".encode())
                    prev_Turn = Turn
                    Turn_timer = time.perf_counter()
                    Turn = 0  


            if move_opposite != prev_move_opposite:
                if time.perf_counter() - move_opposite_timer > DEBOUNCE_TIME:
                    arduino.write(f"{move_opposite}\n".encode())
                    prev_move_opposite = move_opposite
                    move_opposite_timer = time.perf_counter()
                    move_opposite = 0  # reset after sending command

            if rotate != prev_rotate:
                if time.perf_counter() - rotate_timer > DEBOUNCE_TIME:
                    arduino.write(f"{rotate}\n".encode())
                    prev_rotate = rotate
                    rotate_timer = time.perf_counter()
                    rotate = -1  # reset after sending command

    












# matrix = np.array([row1, row2])
# print(matrix)
# result = matrix @ matrix.T
# print(result)









            ### Display results

            # Draw framerate
            cv2.putText(frame, f'FPS: {avg_frame_rate:0.2f}', (20,30), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,0,0), 2)
            
            # Draw rectangle around the detection box where we are looking for a person
            cv2.rectangle(frame, (pbox_xmin, pbox_ymin), (pbox_xmax, pbox_ymax), (0,255,255), 2)
            
            # Draw GPIO status on frame
            if gpio_state == 0:
                cv2.putText(frame, 'No object.', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,0,0), 2)
            elif gpio_state == 1:
                cv2.putText(frame, 'Object detected in box! Turning arm ON.', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,0,0), 3)
                cv2.putText(frame, 'Object detected in box! Turning arm ON.', (20, 60), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
            # Display detection results
            cv2.imshow('YOLO detection results',frame) # Display image
            if record: recorder.write(frame)

            # Wait 5ms before moving to next frame and check for user keypress.
            key = cv2.waitKey(5)
            
            if key == ord('q') or key == ord('Q'): # Press 'q' to quit
                break
            elif key == ord('s') or key == ord('S'): # Press 's' to pause inference
                cv2.waitKey()
            elif key == ord('p') or key == ord('P'): # Press 'p' to save a picture of results on this frame
                cv2.imwrite('capture.png',frame)
            
            # Calculate FPS for this frame
            t_stop = time.perf_counter()
            frame_rate_calc = float(1/(t_stop - t_start))

            # Append FPS result to frame_rate_buffer (for finding average FPS over multiple frames)
            if len(frame_rate_buffer) >= fps_avg_len:
                temp = frame_rate_buffer.pop(0)
                frame_rate_buffer.append(frame_rate_calc)
            else:
                frame_rate_buffer.append(frame_rate_calc)

            # Calculate average FPS for past frames
            avg_frame_rate = np.mean(frame_rate_buffer)


        # Clean up
        print(f'Average pipeline FPS: {avg_frame_rate:.2f}')
        if record: recorder.release()
        if cam_type == 'usb': cam.release()
        if cam_type == 'picamera': cam.stop()
        cv2.destroyAllWindows()





    except KeyboardInterrupt:
        pass

    finally:
        servo1.stop()
        servo2.stop()
        servo3.stop()
        GPIO.cleanup()