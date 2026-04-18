import time

what_box = []
Turn = 0
move_opposite = 0


def move_func():
    pass


def Task_1_1(red_box_dis,blue_box_dis,current_task,red_box_locations,blue_box_locations,pbox_xmin,pbox_xmax,pbox_ymin,pbox_ymax,servo1,servo2,servo3,move_servo_smooth,upload_sketch,gpio_state,red_box_detections,blue_box_detections):
    

    ### Logic to trigger GPIO change

    ######################## for red and blue box ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    red_box_in_pbox = False
    blue_box_in_pbox = False

    # Go through person detections to check if any are within desired box location
    for ball_xy in red_box_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax) and (red_box_dis < 30):
            red_box_in_pbox = True
            what_box.extend(["red box", "blue box"])
            print("Picked red box")

    for ball_xy in blue_box_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax) and (blue_box_dis < 20):
            blue_box_in_pbox = True
            what_box.extend(["blue box","red box"])
            print("Picked blue box")
            
        # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if red_box_in_pbox == True:
        red_box_detections = min(8, red_box_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        red_box_detections = max(0, red_box_detections - 1)

    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if blue_box_in_pbox == True:
        blue_box_detections = min(8, blue_box_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        blue_box_detections = max(0, blue_box_detections - 1)

    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if (red_box_detections >= 8 or blue_box_detections >= 8)and (red_box_dis < 30 or blue_box_dis < 20 ) and gpio_state == 0:
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
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)

        current_task = 1.2



    return gpio_state, red_box_detections, blue_box_detections,current_task

def Task_1_2(red_box_dis,blue_box_dis,current_task,red_box_locations,blue_box_locations,pbox_xmin,pbox_xmax,pbox_ymin,pbox_ymax,servo1,servo2,servo3,move_servo_smooth,upload_sketch,gpio_state,red_box_detections,blue_box_detections):
    global Turn  
        
        ### Logic to trigger GPIO change

    ######################## for red and blue box ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    red_box_in_pbox = False
    blue_box_in_pbox = False

    # Go through person detections to check if any are within desired box location
    if what_box[0] == "blue box":
        for ball_xy in red_box_locations:
            
            ball_cx, ball_cy = ball_xy # Get center coordinates for this person
            
            # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
            if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
                red_box_in_pbox = True
                print("Picked red box")

    else:
        for ball_xy in blue_box_locations:
            
            ball_cx, ball_cy = ball_xy # Get center coordinates for this person
            
            # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
            if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
                blue_box_in_pbox = True
                print("Picked blue box")
                
        # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if red_box_in_pbox == True:
        red_box_detections = min(8, red_box_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        red_box_detections = max(0, red_box_detections - 1)

    # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if blue_box_in_pbox == True:
        blue_box_detections = min(8, blue_box_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        blue_box_detections = max(0, blue_box_detections - 1)

    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if (red_box_detections >= 8 or blue_box_detections >= 8)and (red_box_dis < 30 or blue_box_dis < 20 ) and gpio_state == 0:
        gpio_state = 1
        print("Starting servo sequence...")


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        # move_servo_smooth(servo1, 90)
        # move_servo_smooth(servo2, 90)
        # move_servo_smooth(servo3, 90)
        # time.sleep(1)

        move_servo_smooth(servo1, 180)
        move_servo_smooth(servo2, 180)
        move_servo_smooth(servo3, 180)
        time.sleep(1)

        # move_servo_smooth(servo1, 90)
        # move_servo_smooth(servo2, 90)
        # move_servo_smooth(servo3, 90)
        # time.sleep(1)


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        print("Sequence complete!")

        gpio_state = 0
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)

        if what_box[0] == "red box":
            Turn = 1
            time.sleep(1)


        else:
            Turn = -1
            time.sleep(1)


        current_task = 1.3

    return gpio_state, red_box_detections, blue_box_detections,current_task

def Task_1_3(square_dis, current_task, square_locations, pbox_xmin, pbox_xmax, pbox_ymin, pbox_ymax, servo1, servo2, servo3, move_servo_smooth,upload_sketch, gpio_state, square_detections):
    global move_opposite

            ### Logic to trigger GPIO change

    ######################## for red and blue box ########################
    
    # Initialize flag to indicate whether person is in the desired location this frame (set as False)
    square_in_pbox = False
    

    # Go through person detections to check if any are within desired box location

    for ball_xy in square_locations:
        
        ball_cx, ball_cy = ball_xy # Get center coordinates for this person
        
        # This big conditional checks if the person's center_x/center_y coordinates are within the box coordinates
        if (ball_cx > pbox_xmin) and (ball_cx < pbox_xmax) and (ball_cy > pbox_ymin) and (ball_cy < pbox_ymax):
            square_in_pbox = True


                
        # If there is a ball in the box, increment consecutive detection count by 1 (but not above 15)
    if square_in_pbox == True:
        square_detections = min(8, square_detections + 1) # Prevents this variable from going above 15 
    
    # If not, decrease consecutive detection count by 1 (but not below 0)
    else:
        square_detections = max(0, square_detections - 1)


    # If consecutive detections are high enough AND the arm is currently off, turn arm on!
    if square_detections >= 8 and square_dis < 15  and gpio_state == 0:
        gpio_state = 1
        print("Starting servo sequence...")


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        # move_servo_smooth(servo1, 90)
        # move_servo_smooth(servo2, 90)
        # move_servo_smooth(servo3, 90)
        # time.sleep(1)

        move_servo_smooth(servo1, 180)
        move_servo_smooth(servo2, 180)
        move_servo_smooth(servo3, 180)
        time.sleep(1)

        # move_servo_smooth(servo1, 90)
        # move_servo_smooth(servo2, 90)
        # move_servo_smooth(servo3, 90)
        # time.sleep(1)


        move_servo_smooth(servo1, 0)
        move_servo_smooth(servo2, 0)
        move_servo_smooth(servo3, 0)
        time.sleep(1)

        print("Sequence complete!")

        move_opposite = 1 # for turn 180

        gpio_state = 0
        servo1.ChangeDutyCycle(0)
        servo2.ChangeDutyCycle(0)
        servo3.ChangeDutyCycle(0)

        current_task = 2


    return gpio_state, square_detections,current_task, Turn, move_opposite







    

    # if (red_box_detections <= 0 and blue_box_detections <= 0) and gpio_state == 0:
    #     gpio_state = 0
    #     move_func()  



    


        


