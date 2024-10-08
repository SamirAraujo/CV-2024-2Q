import face_recognition
import os
import sys
import cv2
import numpy as np
import math
import csv
from datetime import datetime

DIRECTORY = r'./faces'

output_directory = './lista_presenca'
os.makedirs(output_directory, exist_ok=True)

current_date = datetime.now().strftime("%Y-%m-%d")
filename = os.path.join(output_directory, f"aula_{current_date}.txt")

def face_confidence(face_distance, face_match_threshold=0.6):
    range_val = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range_val * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_locations = []
        self.face_names = []
        self.process_current_frame = True
        self.identified_names = set()
        self.encode_faces()

    def encode_faces(self):
        for image_filename in os.listdir(DIRECTORY):
            full_file_path = os.path.join(DIRECTORY, image_filename)
            face_image = face_recognition.load_image_file(full_file_path)
            face_encodings = face_recognition.face_encodings(face_image)
            if face_encodings:
                face_encoding = face_encodings[0]
                name = os.path.splitext(image_filename)[0]
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(name)

        print(self.known_face_names)

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        self.face_locations = face_recognition.face_locations(rgb_small_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

        self.face_names = []
        if self.face_encodings:
            for face_encoding in self.face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.5)
                name = "Desconhecido"
                confidence = "Desconhecido"

                if self.known_face_encodings:
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    if face_distances.size > 0:
                        best_match_index = np.argmin(face_distances)

                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            confidence = face_confidence(face_distances[best_match_index])

                        self.face_names.append(f'{name} ({confidence})')

                        if name not in self.identified_names and name != "Desconhecido":
                            self.identified_names.add(name)
                            self.write_to_csv(name)

    def write_to_csv(self, name):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([name, date])

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit('fonte de vídeo não encontrada...')

        while True:
            ret, frame = video_capture.read()

            if not ret:
                print("Falha em recuperar o frame")
                break

            self.process_frame(frame)
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                color = (0, 255, 0) 
                if '(' in name and ')' in name:
                    try:
                        confidence = float(name.split('(')[-1].split(')')[0].strip('%')) / 100
                        if confidence < 0.9:
                            color = (0, 0, 255)
                    except ValueError:
                        color = (0, 0, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow('Reconhecimento de face', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    if not os.path.exists('faces_identificadas.csv'):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['nome', 'data'])

    fr = FaceRecognition()
    fr.run_recognition()