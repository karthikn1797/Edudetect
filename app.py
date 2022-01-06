from flask import Flask, render_template, Response, request, jsonify
import cv2
import face_recognition
import numpy as np
from PIL import Image
import mysql.connector
from mysql.connector.constants import ClientFlag
from datetime import datetime
app = Flask(__name__)

config = {
		'user': 'root',
		'password': 'cloudcomputing123',
		'host': '34.68.4.80',
		'client_flags': [ClientFlag.SSL],
		'database': 'edudatabase',
		'ssl_ca': 'server-ca.pem',
		'ssl_cert': 'client-cert.pem',
		'ssl_key': 'client-key.pem'
	}

	# now we establish our connection
cnxn = mysql.connector.connect(**config)
print(cnxn)

cursor = cnxn.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS Attendance (id int NOT NULL PRIMARY KEY AUTO_INCREMENT,dateAndTime varchar(255),name varchar(255));')
cnxn.commit()

aneesh_image = face_recognition.load_image_file("static/training_images/aneesh/aneesh.jpg")
aneesh_face_encoding = face_recognition.face_encodings(aneesh_image)[0]

archana_image = face_recognition.load_image_file("static/training_images/archana/archana.jpeg")
archana_face_encoding = face_recognition.face_encodings(archana_image)[0]

rohan_image = face_recognition.load_image_file("static/training_images/rohan/rohan.jpg")
rohan_face_encoding = face_recognition.face_encodings(rohan_image)[0]

karthik_image = face_recognition.load_image_file("static/training_images/karthik/karthik.jpg")
karthik_face_encoding = face_recognition.face_encodings(karthik_image)[0]

habeeb_image = face_recognition.load_image_file("static/training_images/habeeb/habeeb.jpg")
habeeb_face_encoding = face_recognition.face_encodings(habeeb_image)[0]

known_face_encodings = [
    aneesh_face_encoding,
    archana_face_encoding,
    rohan_face_encoding,
    karthik_face_encoding,
    habeeb_face_encoding,
]
known_face_names = [
    "Aneesh",
    "Archana",
    "Rohan",
    "Karthik",
    "Habeeb Olufowobi"
]

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def gen_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)
            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top),
                              (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35),
                              (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 1.0, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/auto')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def manual_recognize():
    return render_template('manual.html')


@app.route('/viewAttendance')
def view_attendance():
    cursor = cnxn.cursor()
    cursor.execute('Select * from Attendance;')
    result = cursor.fetchall()
    cursor.close()
    print(result)
    return render_template('attendence.html',results=result)

@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        file = request.files['file']
        image = Image.open(file)
        numpydata = np.asarray(image)
        small_frame = cv2.resize(numpydata, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        nameString = ""
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(
                known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)
        cursor = cnxn.cursor()
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        sql = "Insert into Attendance(dateAndTime,name) Values(%s,%s);"
        val = (date_time, ','.join(face_names))
        cursor.execute(sql,val)
        cnxn.commit()
        cursor.close()
        return jsonify(face_names)
    except Exception as e:
        print(e)
        return jsonify([str(e)])

if __name__ == '__main__':
    app.run(debug=True)
