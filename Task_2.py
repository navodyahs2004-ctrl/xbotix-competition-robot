import time

row1 = []

import RPi.GPIO as GPIO

# Define pins
LED_PINS = [16,12]

# Setup pins as output
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)



# add these globals once (see above)
task2_initialized = False
task2_red_recorded = False
task2_green_recorded = False
task2_off_recorded = False

the_rest = True


def Task_2_1(green_light_dis, red_light_dis, off_light_dis, current_task, green_light_locations, red_light_locations, off_light_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth,upload_sketch, gpio_state, green_light_detections, red_light_detections, off_light_detections):
    
    global task2_initialized, task2_red_recorded, task2_green_recorded, task2_off_recorded, the_rest


    if (not task2_initialized) and current_task == 2:
        task2_initialized = True
        task2_red_recorded = False
        task2_green_recorded = False
        task2_off_recorded = False
           # start fresh for this task run (optional but recommended)

    # If we leave Task 2, clear initialization so next time we re-enter it will reset
    if current_task != 2:
        task2_initialized = False
    ### Logic to trigger GPIO change

    ######################## for red and blue box ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    red_light_in_pbox = False
    green_light_in_pbox = False
    off_light_in_pbox = False

    # Go through person detections to check if any are within desired box location
    for ball_xy in red_light_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            red_light_in_pbox = True
            


    for ball_xy in green_light_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            green_light_in_pbox = True


    for ball_xy in off_light_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            off_light_in_pbox = True




            
        # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if red_light_in_pbox == True:
        red_light_detections = min(8, red_light_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        red_light_detections = max(0, red_light_detections - 1)





    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if green_light_in_pbox == True:
        green_light_detections = min(8, green_light_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        green_light_detections = max(0, green_light_detections - 1)




    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if off_light_in_pbox == True:
        off_light_detections = min(8, off_light_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        off_light_detections = max(0, off_light_detections - 1)



    if (red_light_detections >= 8) and (not task2_red_recorded) and gpio_state == 0 and (the_rest == True):
        gpio_state = 1
        row1.append(0)
        task2_red_recorded = True
        print("Recorded RED -> 0; array now:", row1)
        gpio_state = 0
        time.sleep(10)
        task2_red_recorded = False


    if (green_light_detections >= 8) and (not task2_green_recorded) and gpio_state == 0 and (the_rest == True):
        gpio_state = 1
        row1.append(1)
        task2_green_recorded = True
        print("Recorded GREEN -> 1; array now:", row1)
        gpio_state = 0
        time.sleep(10)
        task2_green_recorded = False




    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if (off_light_detections >= 8)and (off_light_dis < 20) and gpio_state == 0:
        gpio_state = 1
        print("Starting servo sequence...")


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        move_servo_smooth(servo1, 90)
        move_servo_smooth(servo2, 90)
        move_servo_smooth(servo3, 90)
        time.sleep(1)

        move_servo_smooth(servo1, 180)
        move_servo_smooth(servo2, 180)
        move_servo_smooth(servo3, 180)
        time.sleep(1)

        move_servo_smooth(servo1, 90)
        move_servo_smooth(servo2, 90)
        move_servo_smooth(servo3, 90)
        time.sleep(1)


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        print("Sequence complete!")

        
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)

        the_rest = False

    if (not task2_off_recorded) and (not the_rest):
        if green_light_detections >= 8:
            row1.append(1)
            task2_off_recorded = True
            print("Recorded OFF->GREEN -> 1; array now:", row1)
            gpio_state = 0
            the_rest = True

        elif red_light_detections >= 8:
            row1.append(0)
            task2_off_recorded = True
            print("Recorded OFF->RED -> 0; array now:", row1)
            gpio_state = 0
            the_rest = True
        # else:
        #     # if neither detection reached 8 after press, you can either wait more frames or set a fallback
        #     # For now, we will not record anything until one reaches 8
        #     print("After press: no confirmed color yet; waiting for detection to reach threshold.")



    # light towers
    if row1[0] == 1:
        GPIO.output(LED_PINS[0], GPIO.HIGH)
    if row1[1] == 1:
        GPIO.output(LED_PINS[1], GPIO.HIGH) 
    if row1[2] == 1:
        GPIO.output(LED_PINS[2], GPIO.HIGH)    


    if len(row1) == 3:
        current_task = 3
        print("array : ", row1)


    return gpio_state, green_light_detections, red_light_detections, off_light_detections, current_task, row1



