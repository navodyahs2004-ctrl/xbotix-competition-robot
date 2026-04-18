import time

def move_func():
    pass

num_of_ball = []
num_of_red_ball = []
num_of_green_ball = []


def Task_3(current_task,red_ball_locations,green_ball_locations,pbox_xmin,pbox_xmax,pbox_ymin,pbox_ymax,servo1,servo2,servo3,servo4,move_servo_smooth,upload_sketch,gpio_state,red_ball_detections,green_ball_detections):
        ######################## for red ball ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    red_ball_in_pbox = False
    row2 = []

    move_servo_smooth(servo4, 90)


    # Go through person detections to check if any are within desired box location
    for ball_xy in red_ball_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            red_ball_in_pbox = True

    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if red_ball_in_pbox == True:
        red_ball_detections = min(8, red_ball_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        red_ball_detections = max(0, red_ball_detections - 1)

    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if red_ball_detections >= 8 and gpio_state == 0:
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

        gpio_state = 0
        num_of_ball.append("red")
        num_of_red_ball.append(0)  #adding nu of red ball
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)



    if red_ball_detections <= 0 and gpio_state == 0:
        gpio_state = 0
        move_func()



    ######################## for green ball ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    green_ball_in_pbox = False

    # Go through person detections to check if any are within desired box location
    for ball_xy in green_ball_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            green_ball_in_pbox = True

    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if green_ball_in_pbox == True:
        green_ball_detections = min(8, green_ball_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        green_ball_detections = max(0, green_ball_detections - 1)

    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if green_ball_detections >= 8 and gpio_state == 0:
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

        gpio_state = 0
        num_of_ball.append("green")
        num_of_green_ball.append(1)  #adding nu of green ball
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)


    if len(num_of_ball) == 5:
        print(num_of_ball)
        if len(num_of_green_ball) == 0:
            row2 = [0,0,0]
        
        if len(num_of_green_ball) == 1:
            row2 = [0,0,1]
        
        if len(num_of_green_ball) == 2:
            row2 = [0,1,0]
        
        if len(num_of_green_ball) == 3:
            row2 = [0,1,1]
        
        if len(num_of_green_ball) == 4:
            row2 = [1,0,0]
        
        if len(num_of_green_ball) == 5:
            row2 = [1,0,1]
        
        print("row2" ,row2)
        current_task = 1
        
    if green_ball_detections <= 0 and gpio_state == 0:
        gpio_state = 0
        move_func()

        
            

    return gpio_state, red_ball_detections, green_ball_detections,current_task, row2      

