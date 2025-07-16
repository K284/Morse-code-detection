import cv2
import time

# Thresholds and timings
BRIGHTNESS_THRESHOLD = 200  # Brightness above this = flashlight ON
DOT_DURATION = 0.3          # Seconds for a dot
DASH_DURATION = 0.8         # Seconds for a dash
GAP_BETWEEN_LETTERS = 1.0   # Seconds of darkness = new letter
GAP_BETWEEN_WORDS = 2.0     # Seconds of darkness = new word

# Morse Code Dictionary
MORSE_DICT = {
    '.-': 'A',    '-...': 'B',  '-.-.': 'C',  '-..': 'D',    '.': 'E',
    '..-.': 'F',  '--.': 'G',   '....': 'H',  '..': 'I',     '.---': 'J',
    '-.-': 'K',   '.-..': 'L',  '--': 'M',    '-.': 'N',     '---': 'O',
    '.--.': 'P',  '--.-': 'Q',  '.-.': 'R',   '...': 'S',    '-': 'T',
    '..-': 'U',   '...-': 'V',  '.--': 'W',   '-..-': 'X',   '-.--': 'Y',
    '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3',  '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8',  '----.': '9'
}

cap = cv2.VideoCapture(0)

morse_sequence = ''
translated_text = ''
light_on = False
on_start = None
last_off_time = time.time()

print("▶ Flash your light towards the webcam to type in Morse code.")
print("✴ Press 'q' to stop.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[100:300, 200:400]  # Region of interest to check light
    brightness = roi.mean()

    cv2.rectangle(frame, (200, 100), (400, 300), (0, 255, 0), 2)
    cv2.putText(frame, f"Brightness: {int(brightness)}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    current_time = time.time()

    if brightness > BRIGHTNESS_THRESHOLD:
        if not light_on:
            on_start = current_time
            light_on = True
    else:
        if light_on:
            duration = current_time - on_start
            if duration < DOT_DURATION:
                morse_sequence += '.'
            elif duration < DASH_DURATION:
                morse_sequence += '-'
            # else: ignore too long flashes
            last_off_time = current_time
            light_on = False

        # Check for end of letter
        if current_time - last_off_time > GAP_BETWEEN_LETTERS and morse_sequence:
            letter = MORSE_DICT.get(morse_sequence, '?')
            translated_text += letter
            morse_sequence = ''

        # Check for end of word
        if current_time - last_off_time > GAP_BETWEEN_WORDS:
            if translated_text and not translated_text.endswith(' '):
                translated_text += ' '

    # Show live output
    cv2.putText(frame, f"Morse: {morse_sequence}", (10, 420),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, f"Text: {translated_text}", (10, 470),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)

    cv2.imshow("Morse Code via Flashlight", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print("\nFinal Message:", translated_text.strip())
