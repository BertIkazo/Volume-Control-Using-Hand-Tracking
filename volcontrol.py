import cv2
import time
import numpy as np
import HandTrackingModule as htm  #harus didalam 1 folder yang sama
import math  #Untuk mengetahui panjang garis (PENTING UNTUK MENGATUR VOLUME)
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

Widecam, Heightcam = 640, 480  #Bisa kita Adjust Sesuai Kemauan Kita

cap = cv2.VideoCapture(0)  # 0 untuk integrated camera, 1 untuk camera external
cap.set(3, Widecam)  # Harus Diletakan Dibawah
cap.set(4, Heightcam)  # -II-

detector = htm.handDetector(detectionCon=0.6)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
volRange = volume.GetVolumeRange()

######################
#VARIABEL
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
pTime = 0
#####################
while True:
    succes, img = cap.read()
    img = detector.findHands(img) #Mencari tangan
    lmList = detector.findPosition(img, draw=False)  #Mencari Posisi Landmark
    if len(lmList) !=0:
        print(lmList[4],lmList[8])  #Mengeluarkan hasil lanndmark yang di inginkan

        x1, y1 = lmList[4][1], lmList[4][2]  #Posisi ujung jempol, 4 = id landmark jempol, 1 = cord x, 2= cord y
        x2, y2 = lmList[8][1], lmList[8][2]  #Posisi ujung telunjuk, 8 = id landmark telunjuk, 1 = cord x, 2 = cord y
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2  #Membuat Bulatan Di Garis Tengah Line

        cv2.circle(img, (x1, y1), 7, (255,255,255), cv2.FILLED)  #Circle di posisi ujung jempol, centernya diambil dari cord x dan y
        cv2.circle(img, (x2, y2), 7, (255,255,255), cv2.FILLED)  # -II-
        cv2.line(img, (x1, y1), (x2,y2), (0, 0, 252), 2)  #Membuat Garis Mengaitkan Ujung Jempol Dan Ibu Jari
        cv2.circle(img, (cx, cy), 7, (255, 255, 255), cv2.FILLED)

        length = math.hypot(x1 - x2, y1 - y2)  #Mendapatkan hasil panjang dari ujung jempol ke ujung telunjuk
        #print(length)  Mengeluarkan Hasil Panjang

        vol = np.interp(length, [50, 200], [minVol, maxVol])
        volBar = np.interp(length, [50, 200], [400, 150])
        volPer = np.interp(length, [50, 200], [0, 100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 7, (0, 255, 0), cv2.FILLED)  #Jika nilai value dibawah 50 circle ditengah akan menjadi hijau

    cv2.rectangle(img, (50, 150), (85, 400), (0, 200, 255), 1)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 200, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 200, 255), 1)
    #if length > 200:
            #cv2.circle(img, (cx, cy), 7, (0, 200, 250), cv2.FILLED)

    #print(lmList)  #Mengeluarkan hasil landmark

    #Fps information
    cTime = time.time()  #cTime = current time, pTime = previous time
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 204), 1) #Fps text

    cv2.imshow("Img", img)
    cv2.waitKey(1)