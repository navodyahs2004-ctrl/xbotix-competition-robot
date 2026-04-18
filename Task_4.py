import time
import numpy as np

rotate = -1

def Task_4(row1, row2, servo4, move_servo_smooth,upload_sketch,):
    global rotate

    move_servo_smooth(servo4, 90)

    # 1. Make matrix from two rows
    matrix = np.array([row1, row2])
    print("Matrix:\n", matrix)

    # 2. Multiply matrix × transpose
    result = matrix @ matrix.T
    print("Result Matrix (2x2):\n", result)

    # 3. Add all 4 values in the result matrix
    total_sum = np.sum(result)
    print("Sum of all elements =", total_sum)

    # 4. Divide by 4 → get quotient and remainder
    quotient = total_sum // 4      # integer division
    remainder = total_sum % 4      # remainder
    
    print("Quotient =", quotient)
    print("Remainder =", remainder)



    def handle_rotation(q, r, servo4, move_servo_smooth):
        global rotate

        rotate = q
        time.sleep(1)
        move_servo_smooth(servo4, 30)
        time.sleep(5)

        rotate = r
        move_servo_smooth(servo4, 150)
        time.sleep(5)

        move_servo_smooth(servo4, 90)
        return rotate
    
    rotate = handle_rotation(quotient, remainder, servo4, move_servo_smooth)
    return rotate



    
    