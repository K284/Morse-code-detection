import cv2
import time
import numpy as np
import mediapipe as mp

MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
    '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
    '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
    '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
    '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
    '--..': 'Z', '': ' '
}

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1)

cap = cv2.VideoCapture(0)

def get_ear(landmarks, width, height):
    LEFT_EYE = [33, 160, 158, 133, 153, 144]
    coords = [(int(landmarks.landmark[i].x * width), int(landmarks.landmark[i].y * height)) for i in LEFT_EYE]
    horizontal = np.linalg.norm(np.array(coords[0]) - np.array(coords[3]))
    vertical = (np.linalg.norm(np.array(coords[1]) - np.array(coords[5])) +
                np.linalg.norm(np.array(coords[2]) - np.array(coords[4]))) / 2
    return vertical / horizontal

EAR_THRESHOLD = 0.2
DOT_DURATION = 0.3
DASH_DURATION = 0.7
LETTER_PAUSE = 1.2
WORD_PAUSE = 2.5

morse = ''
text = ''
blink_start = None
last_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)
    h, w = frame.shape[:2]

    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            ear = get_ear(face_landmarks, w, h)

            if ear < EAR_THRESHOLD:
                if blink_start is None:
                    blink_start = time.time()
            else:
                if blink_start is not None:
                    duration = time.time() - blink_start
                    blink_start = None
                    last_time = time.time()

                    if duration < DOT_DURATION:
                        morse += '.'
                    elif duration < DASH_DURATION:
                        morse += '-'

    if blink_start is None and (time.time() - last_time) > LETTER_PAUSE:
        if morse:
            text += MORSE_CODE_DICT.get(morse, '?')
            morse = ''
        last_time = time.time()

    if blink_start is None and (time.time() - last_time) > WORD_PAUSE:
        text += ' '
        last_time = time.time()

    cv2.putText(frame, f'Morse: {morse}', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
    cv2.putText(frame, f'Text: {text}', (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,100,100), 2)

    cv2.imshow("Morse Code Eye Blink Translator", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
