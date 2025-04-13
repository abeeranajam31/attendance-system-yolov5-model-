import os
import psycopg2
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import torch
from PIL import Image
import io
import numpy as np
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Make sure to keep this secure!

# Ensure the uploads directory exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create uploads directory if it doesn't exist

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='./best-4.pt')  # Update the path to your model
model.eval()

def get_conn():
    """Establish connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname="attendance_system",  # Update your database name
            user="postgres",  # Update your username
            password="123456789",  # Update your password
            host="localhost"  # Ensure your database is running locally or update the host if needed
        )
        return conn
    except Exception as e:
        flash(f"Error connecting to the database: {e}", "error")
        return None

def process_image(image):
    """Process the uploaded image with YOLO model."""
    results = model(image)
    # Get unique predictions and their counts
    # Initialize detections with all classes as 'Absent'
    detections = {name: 'Absent' for name in model.names.values()}
    
    # Update detections for present students
    for pred in results.pred[0]:
        class_id = int(pred[5])
        if class_id in model.names:
            label = model.names[class_id]
            detections[label] = 'Present'
    
        
    # Render results
    rendered_img = results.render()[0]  # returns list of images
    return Image.fromarray(rendered_img), detections

# @app.route('/')
# def index():
#     """Render the home page."""
#     return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle student registration and insert data into the database."""
    if request.method == 'POST':
        # Retrieve form data
        student_name = request.form['student_name']
        student_email = request.form['student_email']
        student_roll_number = request.form['student_roll_number']
        student_department = request.form['student_department']

        # Retrieve the image file
        student_image = request.files['student_image']
        if student_image.filename == '':
            flash('No image selected', 'error')
            return redirect(url_for('register'))

        # Save the image file
        image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + student_image.filename
        save_path = os.path.join(UPLOAD_FOLDER, image_filename)
        student_image.save(save_path)

        # Establish database connection
        conn = get_conn()
        if not conn:
            flash("Error connecting to the database", "error")
            return redirect(url_for('index'))

        try:
            # Insert the data into the database along with the image filename
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO students (name, email, roll_number, department, image_filename)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_name, student_email, student_roll_number, student_department, image_filename))

            conn.commit()
            cur.close()
            conn.close()

            # Render the success page
            #flash("Student registered successfully!", "success")
            return render_template('success.html')
        except psycopg2.Error as e:
            conn.rollback()
            flash(f"Database error: {e}", "error")
            return redirect(url_for('register'))  # Redirect back to registration form on error
        finally:
            conn.close()  # Ensure connection is closed even if an error occurs

    # If request method is GET, render the registration form
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Render the home page with upload functionality."""
    global img_io
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file uploaded'
        
        file = request.files['file']
        if file.filename == '':
            return 'No file selected'

        img = Image.open(file.stream)
        processed_img, detections = process_image(img)
        
        img_io = io.BytesIO()
        processed_img.save(img_io, 'PNG')
        img_io.seek(0)
        
        # Update attendance in database
        conn = get_conn()
        if conn:
            cur = conn.cursor()
            current_date = datetime.now().date()
            
            # Insert attendance records
            for student_name, status in detections.items():
                cur.execute("""
                    INSERT INTO attendance (student_name, status, date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (student_name, date) 
                    DO UPDATE SET status = EXCLUDED.status
                """, (student_name, status, current_date))
            
            conn.commit()
            cur.close()
            conn.close()

        # Store processed image in session or temp storage
        img_io.seek(0)
            
        # Return detections data as JSON and image URL
        response = {
            'detections': detections,
            'image_url': url_for('get_processed_image', _external=True)
        }
        return response
    

    return render_template('index.html')  # Move your HTML to a template file

@app.route('/processed_image')
def get_processed_image():
    """Serve the processed image."""
    if 'img_io' in globals():
        return send_file(img_io, mimetype='image/png')
    return 'No image found', 404

if __name__ == '__main__':
    app.run(debug=True)