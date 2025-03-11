from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime
from db.db import get_db_connection

app = Flask(__name__)

cursor = get_db_connection().cursor(dictionary=True)
app.secret_key = 'secret_key'
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bookslot')
def bookslot():
    slots = get_available_slots()  # Fetch available slots
    return render_template('bookslot.html', slots=slots)


@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get form data
    slot_id = request.form.get('slot_id')
    user_name = request.form.get('user_name')

    # Fetch slot details
    cursor.execute("SELECT * FROM slots WHERE id = %s", (slot_id,))
    slot = cursor.fetchone()

    if not slot or slot['is_available'] == 0:
        db.close()
        return "Slot is no longer available.", 400  # Error if slot is already booked

    # Update slot as booked
    booking_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "UPDATE slots SET is_available = 0, booked_by = %s, booking_time = %s WHERE id = %s",
        (user_name, booking_time, slot_id)
    )
    db.commit()
    db.close()

    return render_template('confirm_booking.html', slot=slot, user_name=user_name, booking_time=booking_time)

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
    db.close()

    return render_template("payment_success.html", slot_id=slot_id, upi_id=upi_id)

@app.route('/update_sensor', methods=['POST'])
def update_sensor():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    slot_name = request.json.get('slot_name')  # Sensor sends slot name
    status = request.json.get('status')  # 0 = Empty, 1 = Occupied

    if slot_name:
        cursor.execute("UPDATE slots SET sensor_status = %s WHERE slot_name = %s", (status, slot_name))
        db.commit()
        db.close()
        return {"message": "Sensor data updated successfully"}, 200
    else:
        db.close()
        return {"error": "Invalid slot name"}, 400
    
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
    return redirect(url_for('admin_login'))

@app.before_request
def require_admin_login():
    if request.endpoint in ['admin_dashboard', 'release_slot'] and 'admin' not in session:
        return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
