from ultralytics import YOLO
import cv2
import math
import torch
import time
import numpy as np
import pyfirmata
from pyfirmata import Arduino, util

# Koneksi ke Arduino
board = Arduino('COM3')
hitung=0
hitungmaju=0
hitam= False
is_capit_on= False
qr_detected = False
biru=False
putih=False
# Pin setup
servo1_pin = board.get_pin('d:3:s')
servo2_pin= board.get_pin('d:11:s')
ena = board.get_pin('d:5:p')
in1 = board.get_pin('d:6:o')
in2 = board.get_pin('d:7:o')
in3 = board.get_pin('d:8:o')
in4 = board.get_pin('d:9:o')
enb = board.get_pin('d:10:p')
# servo2_pin.write(30)

# Fungsi untuk menggerakkan motor maju
def robot_maju():
    print("Robot bergerak maju...")
    in1.write(1)
    in2.write(0)
    ena.write(1)  # Kecepatan penuh
    in3.write(0)
    in4.write(1)
    enb.write(1)  # Kecepatan penuh
    
def robot_mundur():
        in1.write(0)
        in2.write(1)
        ena.write(1)  # Kecepatan penuh
        in3.write(0)
        in4.write(1)
        enb.write(1) 
\

# Fungsi untuk menggerakkan servo ke posisi menutup (capit)
def capit_on():
    print("Capit aktif...")
    global is_capit_on
    is_capit_on= True
    servo1_pin.write(0)
    time.sleep(2)  # jeda 3 detik setelah Servo 2 mencapai 0 derajat
    servo2_pin.write(25)
    time.sleep(2)  # jeda 3 detik setelah Servo 2 mencapai 0 derajat
    in1.write(0)
    in2.write(1)
    ena.write(0.5)  # Kecepatan penuh
    in3.write(0)
    in4.write(1)
    enb.write(0.5)
    time.sleep(0.5)
    robot_berputar()

# Fungsi untuk menggerakkan servo ke posisi membuka
def capit_off():
    print("Capit nonaktif.")
    robot_maju()
    delay(200)
    robot_berhenti()
    delay(100)
    for pos in range(25, 0, -1):
        servo2_pin.write(pos);       
        delay(30);               
    #servo2_pin.write(5) # jeda 3 detik setelah Servo 2 mencapai 0 derajat
    for pos in range(0, 45, +1):
        servo1_pin.write(pos)
        delay(30)
    delay(5000)
    in1.write(0)
    in2.write(1)
    ena.write(0.2)  # Kecepatan penuh
    in3.write(0)
    in4.write(1)
    enb.write(0.2) 
    delay(200)
    
    # jeda 3 detik setelah Servo 2 mencapai 0 derajat

# Fungsi untuk membuat robot berputar
def robot_berputar():
    print("Robot berputar...")
    in1.write(0)
    in2.write(1)
    ena.write(0.5)  # Setengah kecepatan
    in3.write(0)
    in4.write(1)
    enb.write(0.5)  # Setengah kecepatan
    
def belok_kiri():
    print("Robot kiri...")
    in1.write(1)
    in2.write(0)
    ena.write(0.5)  # Setengah kecepatan
    in3.write(0)
    in4.write(0)
    enb.write(0.5)  # Setengah kecepatan
    
def belok_kanan():
    print("Robot kanan...")
    in1.write(1)
    in2.write(0)
    ena.write(0.5)  # Setengah kecepatan
    in3.write(0)
    in4.write(0)
    enb.write(0.5)  # Setengah kecepatan

def robot_berhenti():
    print("Robot berhenti...")
    in1.write(0)
    in2.write(0)
    ena.write(0)  # Setengah kecepatan
    in3.write(0)
    in4.write(0)
    enb.write(0) 
    
# Fungsi untuk memberikan delay dalam milidetik
def delay(milliseconds):
    time.sleep(milliseconds / 1000)

# Variabel untuk mengecek status capit


# Start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

# Check for CUDA device and set it
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')

# Load model
model = YOLO('cekcek.pt').to(device)

# Object classes
classNames = ["biru", "putih"]

# Width and height of the frame (for calculating the center coordinates)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
center_line_x = frame_width // 2  # X-coordinate of the center vertical line
center_line_y = frame_height // 2  # Y-coordinate of the center horizontal line
horizontal_line_y = frame_height // 2


# Coordinates of the black dot, 150 pixels below the center line
black_dot_x = center_line_x
black_dot_y = 400
object_touching_center = False


qr_decoder = cv2.QRCodeDetector()
servo1_pin.write(45)
time.sleep(3)  # jeda 3 detik setelah Servo 2 mencapai 0 derajat
while True:
    success, img = cap.read()
    results = model.predict(img, stream=True)

    # Initialize a flag to check if any object is touching the center line
    center_x=0
    object_touching_center = False
    hitungmaju+=1
    if hitungmaju == 1000:
        hitungmaju=0
    
    if not is_capit_on:
        for r in results:
            boxes = r.boxes

            for box in boxes:
                # Bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Calculate the center of the bounding box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                # Set bounding box color based on detected object class
                cls = int(box.cls[0])
                detected_class = classNames[cls]

                if detected_class == "putih":
                    box_color = (0, 255, 0)  # Green for "putih"
                elif detected_class == "biru":
                    box_color = (255, 192, 203)  # Pink for "biru"
                else:
                    box_color = (255, 0, 255)  # Default color if class not recognized

                # Draw bounding box with specified color
                cv2.rectangle(img, (x1, y1), (x2, y2), box_color, 3)

                # Draw red dot at the center of the bounding box with a diameter of 2
                cv2.circle(img, (center_x, center_y), 1, (0, 0, 255), -1)

                # Check if the center dot is touching the center line (within diameter of 2)
                # if abs(center_x - center_line_x) <= 10:  # Allow 2-pixel tolerance for "touching"
                #     object_touching_center = True

                # Check if the red center dot of the object touches the black center dot
                if center_y>=400 and center_y <=420 and (x1<center_line_x) and (x2>center_line_x):
                    robot_berhenti()
                    capit_on()
                    object_touching_center=False
                    is_capit_on = True  # Set is_capit_on to True when touching black dot
                    robot_berhenti()

                # Display object details
                org = (x1, y1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                fontScale = 1
                text_color = (255, 0, 0)
                thickness = 2
                cv2.putText(img, detected_class, org, font, fontScale, text_color, thickness)
                if center_line_x>center_x and abs(center_line_x-x2<=10):
                    in1.write(1)
                    in2.write(0)
                    ena.write(0.5)  # Setengah kecepatan
                    in3.write(0)
                    in4.write(1)
                    enb.write(0.5)  # Setengah kecepatan
                    delay(80)
                    robot_berhenti()
                elif x1<center_line_x and x2>center_line_x and hitungmaju%10 < 1:
                    hitungmaju+=1
                    in1.write(1)
                    in2.write(0)
                    ena.write(1)  # Kecepatan penuh
                    in3.write(0)
                    in4.write(1)
                    enb.write(1)  # Kecepatan penuh 
                    delay(100)
                    in1.write(0)
                    in2.write(0)
                    ena.write(1)  # Kecepatan penuh
                    in3.write(0)
                    in4.write(0)
                    enb.write(1) 
                    continue
                else:
                    in1.write(0)
                    in2.write(1)
                    ena.write(0.5)  # Setengah kecepatan
                    in3.write(0)
                    in4.write(1)
                    enb.write(0.5)  # Setengah kecepatan     
                    delay(8)

    # Call the robot functions based on whether an object is touching the center line
        # if object_touching_center:
            # if x1<center_line_x and x2>center_line_x:
            #     robot_maju()
            #     robot_berhenti() 
        if hitungmaju%10 < 1 :
            in1.write(0)
            in2.write(1)
            ena.write(0.5)  # Setengah kecepatan
            in3.write(0)
            in4.write(1)
            enb.write(0.5)  # Setengah kecepatan     
            delay(8)
        else:
            robot_berhenti()
        # else:
        #     hitung+=1
        #     if hitung == 10:
        #         hitung=0
        #     if hitung > 1 :
        #         robot_berhenti()
        #     else:
        #         robot_berputar()
    
    if is_capit_on:
        if not qr_detected and is_capit_on:
            if hitungmaju%10 <3:
                robot_berputar()
            else:
                robot_berhenti()
        black_dot_y = 240
        horizontal_line_y = 240
        # Mengubah bagian deteksi QR code menggunakan detectAndDecodeMulti
        ret_qr, decoded_info, points, _ = qr_decoder.detectAndDecodeMulti(img)
        if ret_qr and not qr_detected:
            for s, p in zip(decoded_info, points):
                if s:
                    color = (0, 255, 0)  # Warna hijau untuk QR yang valid
                else:
                    color = (0, 0, 255)  # Warna merah untuk QR yang tidak valid

                # Gambar bounding box untuk QR code
                img = cv2.polylines(img, [p.astype(int)], True, color, 8)

                # Titik tengah atas dan bawah bounding box QR code
                # Menghitung titik tengah atas dan bawah dengan benar
                top_center = (int((p[0][0] + p[1][0] + p[2][0] + p[3][0]) / 4), int((p[0][1] + p[1][1] + p[2][1] + p[3][1]) / 4))
                bottom_center = (int((p[0][0] + p[1][0] + p[2][0] + p[3][0]) / 4), int((p[2][1] + p[3][1] + p[0][1] + p[1][1]) / 4))

                # Gambar titik merah di tengah atas dan bawah
                cv2.circle(img, top_center, 5, (0, 0, 255), -1)  # Titik merah atas
                cv2.circle(img, bottom_center, 2, (0, 0, 255), -1)  # Titik merah bawah
                x_kanan = max(p[0][0], p[1][0], p[2][0], p[3][0])
                x_kiri = min(p[0][0], p[1][0], p[2][0], p[3][0])
                detected_class=classNames[cls]
                # Menampilkan teks QR code di atas bounding box
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, s, (int(p[0][0]), int(p[0][1]) - 10), font, 0.8, (255, 0, 0), 2, cv2.LINE_AA)
                
                if abs(top_center[0] - black_dot_x) <= 20 and abs(top_center[1] - black_dot_y) <= 10:
                    robot_berhenti()
                    object_touching_center=False
                    capit_off()
                    robot_berhenti()
                    is_capit_on = False  # Set is_capit_on to False when touching the black dot
                # if abs(top_center[0] - center_line_x) <= 20:
                #     qr_detected = True
                #     object_touching_center= True
                # if center_line_x>center_x and hitungmaju%10 < 1 and abs(center_line_x-x2<=10):
                #     belok_kanan()
                #     delay(100)
                #     robot_berhenti()
                if top_center[1] < 100 and hitungmaju%10<1 and center_line_x<=x_kanan:
                    robot_maju()
                    delay(100)
                    robot_berhenti()
                    delay(100)
                if (center_line_x >= x_kiri and center_line_x <= x_kanan): #and (detected_class == "biru" and 'PENJARA BIRU' in decoded_info) or (detected_class == "putih" and ' PENJARA PUTIH' in decoded_info):
                    if center_line_x>x_kanan and hitungmaju%10<1:
                        in1.write(1)
                        in2.write(0)
                        ena.write(0.5)  # Setengah kecepatan
                        in3.write(0)
                        in4.write(1)
                        enb.write(0.5)  # Setengah kecepatan
                        delay(80)
                        robot_berhenti()
                    elif x_kiri<center_line_x and x_kanan>center_line_x and hitungmaju%10 < 1:
                        hitungmaju+=1
                        in1.write(1)
                        in2.write(0)
                        ena.write(1)  # Kecepatan penuh
                        in3.write(0)
                        in4.write(1)
                        enb.write(1)  # Kecepatan penuh 
                        delay(100)
                        in1.write(0)
                        in2.write(0)
                        ena.write(1)  # Kecepatan penuh
                        in3.write(0)
                        in4.write(0)
                        enb.write(1) 
                        continue
                    else:
                        in1.write(0)
                        in2.write(1)
                        ena.write(0.5)  # Setengah kecepatan
                        in3.write(0)
                        in4.write(1)
                        enb.write(0.5)  # Setengah kecepatan     
                        delay(8)
                        
                side_1 = np.linalg.norm(p[0] - p[1])
                side_2 = np.linalg.norm(p[1] - p[2])
                side_3 = np.linalg.norm(p[2] - p[3])
                side_4 = np.linalg.norm(p[3] - p[0])

                # Jika bounding box tidak berbentuk persegi atau persegi panjang, panggil capit_off()
                if not (abs(side_1 - side_3) <= 40 and abs(side_2 - side_4) <= 40):
                    is_capit_on=False
                    robot_berhenti()
                    robot_berputar()
                    delay(50)
                    is_capit_on = False
                    black_dot_y = 400
                    capit_off()
                    continue
        if hitungmaju%10 < 1 :
            in1.write(0)
            in2.write(1)
            ena.write(0.5)  # Setengah kecepatan
            in3.write(0)
            in4.write(1)
            enb.write(0.5)  # Setengah kecepatan     
            delay(8)
        else:
            robot_berhenti()

    # Gambar garis merah di tengah layar
    cv2.line(img, (center_line_x, 0), (center_line_x, frame_height), (0, 0, 255), 2)
    cv2.circle(img, (black_dot_x, black_dot_y), 4, (0, 0, 0), -1)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) == ord('q'):
        robot_berhenti()
        break

cap.release()
cv2.destroyAllWindows()
