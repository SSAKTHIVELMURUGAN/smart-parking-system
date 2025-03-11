from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from datetime import datetime
from db.db import get_db_connection

app = Flask(__name__)

cursor = get_db_connection().cursor(dictionary=True)

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


if __name__ == '__main__':
    app.run(debug=True)
