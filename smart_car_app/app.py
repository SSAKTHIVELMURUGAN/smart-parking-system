from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, session
import mysql.connector
from datetime import datetime
from db.db import get_db_connection
import qrcode
import os
from flask import send_file
import os
import cv2
import numpy as np
import easyocr
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, session, send_from_directory
import mysql.connector
import os
import cv2
import numpy as np
import easyocr
from datetime import datetime
from werkzeug.utils import secure_filename
from db.db import get_db_connection

app = Flask(__name__)

cursor = get_db_connection().cursor(dictionary=True)
app.secret_key = 'secret_key'

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Load OCR model
reader = easyocr.Reader(['en'])

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    detected_plates = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 30 == 0:  # Process every 30th frame
            plate_text, plate_image_path = detect_plate(frame, frame_count)
            if plate_text:
                detected_plates.append({"text": plate_text, "image": plate_image_path})

    cap.release()
    return detected_plates

def detect_plate(frame, frame_id):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 100, 200)

    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:  # Assuming a number plate has 4 sides
            x, y, w, h = cv2.boundingRect(approx)
            if w > 100 and h > 30:  # Plate size filter
                plate_img = frame[y:y+h, x:x+w]
                plate_text = reader.readtext(plate_img, detail=0)

                if plate_text:
                    plate_text = " ".join(plate_text)
                    image_path = os.path.join(app.config['PROCESSED_FOLDER'], f"plate_{frame_id}.jpg")
                    cv2.imwrite(image_path, plate_img)
                    return plate_text, image_path
    return None, None


@app.route("/processed/<filename>")
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

cursor = get_db_connection().cursor(dictionary=True)
app.secret_key = 'secret_key'
@app.route('/')
def index():
    return render_template('index.html')


@app.route("/upload_video", methods=["GET", "POST"])
def upload_video():
    if request.method == "POST":
        if "video" not in request.files:
            flash("No file uploaded", "danger")
            return redirect(request.url)

        file = request.files["video"]
        if file.filename == "":
            flash("No selected file", "danger")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(video_path)

        detected_plates = process_video(video_path)

        return render_template("results.html", detected_plates=detected_plates)

    return render_template("upload.html")

@app.route('/bookslot')
def bookslot():
    slots = get_available_slots()  # Fetch available slots
    return render_template('bookslot.html', slots=slots)

@app.route('/parking_status')
def parking_status():
    return render_template('parking_status.html')

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get form data
    user_name = request.form.get('user_name')
    mobile_number = request.form.get('mobile_number')
    vehicle_type = request.form.get('vehicle_type')
    vehicle_number = request.form.get('vehicle_number')
    slot_id = request.form.get('slot_id')
    booking_start_time = request.form.get('booking_start_time')
    booking_end_time = request.form.get('booking_end_time')


    # Fetch slot details
    cursor.execute("SELECT * FROM slots WHERE id = %s", (slot_id,))
    slot = cursor.fetchone()

    if not slot or slot['is_available'] == 0:
        db.close()
        return "Slot is no longer available.", 400  # Error if slot is already booked
    
    # Insert booking details into the database
    cursor.execute(
        "INSERT INTO booking_details (user_name, mobile_number, vehicle_type, vehicle_number, slot_id, booking_start_time, booking_end_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user_name, mobile_number, vehicle_type, vehicle_number, slot_id, booking_start_time, booking_end_time)
    )

    # Update slot as booked
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "UPDATE slots SET is_available = 0, booked_by = %s, booking_time = %s WHERE id = %s",
        (user_name, booking_time, slot_id)
    )
    db.commit()
    db.close()

    return render_template('confirm_booking.html', 
                        slot=slot, 
                        user_name=user_name, 
                        mobile_number=mobile_number, 
                        vehicle_type=vehicle_type, 
                        vehicle_number=vehicle_number,
                        booking_start_time=booking_start_time, 
                        booking_end_time=booking_end_time)

# Function to fetch available slots
def get_available_slots():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM slots WHERE is_available = 1")
    slots = cursor.fetchall()
    db.close()
    return slots


@app.route('/payment/<int:slot_id>')
def payment(slot_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM slots WHERE id = %s", (slot_id,))
    slot = cursor.fetchone()

    db.close()

    if not slot:
        return "Invalid Slot ID!", 400

    return render_template('payment.html', slot=slot)

# QR Code Generation Function
def generate_qr(data, filename):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    qr_path = f"static/qr_codes/{filename}.png"
    
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    img.save(qr_path)
    return qr_path

@app.route("/process_payment", methods=["POST"])
def process_payment():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    slot_id = request.form["slot_id"]
    upi_id = request.form["upi_id"]
    user_name = request.form.get("user_name", "Unknown User")
    amount = 50.00  # Fixed parking amount

    if "@" not in upi_id:
        return "Invalid UPI ID format. Please enter a valid UPI ID.", 400

    # Insert payment record
    cursor.execute(
        "INSERT INTO payments (slot_id, user_name, upi_id, amount) VALUES (%s, %s, %s, %s)",
        (slot_id, user_name, upi_id, amount)
    )
    db.commit()
        # Generate QR Code for Entry
    qr_data = f"{user_name}-{slot_id}-{upi_id}"
    qr_path = generate_qr(qr_data, f"{user_name}_{slot_id}")

    db.close()
    
    return render_template("payment_success.html", slot_id=slot_id, upi_id=upi_id, qr_code=qr_path)

    db.close()

    return render_template("payment_success.html", slot_id=slot_id, upi_id=upi_id)

@app.route('/update_sensor', methods=['POST'])
def update_sensor():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    slot_name = request.json.get('slot_name')  # ESP32 sends slot name
    sensor_status = request.json.get('status')  # 0 = Occupied, 1 = Empty

    if slot_name:
        cursor.execute("UPDATE slots SET sensor_status = %s WHERE slot_name = %s", (sensor_status, slot_name))
        db.commit()
        db.close()
        return jsonify({"message": "Sensor data updated successfully"}), 200
    else:
        db.close()
        return jsonify({"error": "Invalid slot name"}), 400

@app.route("/scan_qr", methods=["POST"])
def scan_qr():
    scanned_data = request.form["scanned_data"]  # Data extracted from QR scanner

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Extract user details from QR code data
    user_name, slot_id, upi_id = scanned_data.split("-")

    # Check if the user has a valid booking
    cursor.execute("SELECT * FROM payments WHERE slot_id = %s AND user_name = %s AND upi_id = %s", (slot_id, user_name, upi_id))
    booking = cursor.fetchone()

    db.close()

    if booking:
        return jsonify({"status": "success", "message": "Access Granted!"})
    else:
        return jsonify({"status": "error", "message": "Invalid QR Code. Access Denied."})


@app.route('/get_parking_status')
def get_parking_status():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT slot_name, is_available, sensor_status FROM slots WHERE place IN ('A', 'B')")
    slots = cursor.fetchall()

    db.close()
    return jsonify(slots)

@app.route('/admin')
def admin_dashboard():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch parking slots & status
    cursor.execute("SELECT * FROM slots")
    slots = cursor.fetchall()

    # Fetch payment records
    cursor.execute("SELECT * FROM payments")
    payments = cursor.fetchall()

    db.close()
    return render_template('admin.html', slots=slots, payments=payments)

@app.route('/release_slot/<int:slot_id>', methods=['POST'])
def release_slot(slot_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Free the slot in the database
    cursor.execute("UPDATE slots SET is_available = 1, booked_by = NULL, booking_time = NULL WHERE id = %s", (slot_id,))
    db.commit()
    db.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "admin123": 
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials. Try again."

    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

@app.before_request
def require_admin_login():
    if request.endpoint in ['admin_dashboard', 'release_slot'] and 'admin' not in session:
        return redirect(url_for('admin_login'))
    
@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            flash("User already exists. Please log in.", "warning")
            return redirect(url_for('user_login'))  # Redirect to login page

        # Insert new user
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()
        db.close()

        flash("Account created! Please log in.", "success")
        return redirect(url_for('user_login'))  # Redirect to login

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user:
            session['username'] = user['username']  # Store user in session
            flash("Login successful!", "success")
            return redirect(url_for('index'))  # Login successful
        else:
            flash("Invalid username or password. Try again.", "danger")
            return redirect(url_for('user_login'))  # Redirect to login

    return render_template('login.html')
    
@app.route('/logout')
def user_logout():
    session.pop('username', None)  # Remove user session
    flash("You have been logged out.", "info")
    return redirect(url_for('user_login'))  # Redirect to login page

@app.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('user_login'))  # Redirect if not logged in

    username = session['username']
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    # Fetch booking details
    cursor.execute("""
        SELECT b.*, s.slot_name, s.place 
        FROM booking_details b
        LEFT JOIN slots s ON b.slot_id = s.id
        WHERE b.user_name = %s
    """, (username,))
    bookings = cursor.fetchall()

    # Fetch payment details
    cursor.execute("""
        SELECT p.*, s.slot_name, s.place 
        FROM payments p
        LEFT JOIN slots s ON p.slot_id = s.id
        WHERE p.user_name = %s
    """, (username,))
    payments = cursor.fetchall()

    # Fetch booked vehicle details
    cursor.execute("""
        SELECT s.* FROM slots s
        WHERE s.booked_by = %s
    """, (username,))
    slots = cursor.fetchall()

    db.close()

    return render_template(
        'user_dashboard.html',
        user=user,
        bookings=bookings,
        payments=payments,
        slots=slots
    )

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'username' not in session:
        flash("You must be logged in to checkout.", "danger")
        return redirect(url_for('user_login'))  # Redirect to login if not logged in

    user_name = session['username']  # Get username from session

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch the active booking of the user
    cursor.execute("""
        SELECT * FROM booking_details 
        WHERE user_name = %s 
        ORDER BY booking_start_time DESC 
        LIMIT 1
    """, (user_name,))
    booking = cursor.fetchone()

    if not booking:
        db.close()
        flash("No active bookings found.", "warning")
        return redirect(url_for('user_dashboard'))  # Redirect back to dashboard

    slot_id = booking['slot_id']

    # Update the booking status to completed
    # cursor.execute("""
    #     UPDATE booking_details 
    #     SET status = 'Completed', checkout_time = %s 
    #     WHERE id = %s
    # """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), booking['id']))

    # Free the slot
    cursor.execute("""
        UPDATE slots 
        SET is_available = 1, booked_by = NULL, booking_time = NULL 
        WHERE id = %s
    """, (slot_id,))

    db.commit()
    db.close()

    flash("Checkout successful! Your slot has been released.", "success")
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
