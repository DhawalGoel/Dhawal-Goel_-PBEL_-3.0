"""
AI Student Performance Prediction System
Main Flask Application
Author: ML Engineer
Version: 1.0.0
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
import pickle
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sqlite3
import csv
from io import StringIO, BytesIO
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Global variables for model and preprocessor
model = None
preprocessor = None
model_info = None


def load_model():
    """Load the trained model and preprocessor"""
    global model, preprocessor, model_info
    try:
        model = joblib.load('model/student_performance_model.pkl')
        preprocessor = joblib.load('model/preprocessor.pkl')
        with open('model/model_info.json', 'r') as f:
            model_info = json.load(f)
        logger.info("Model loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False


def init_database():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('database/student_performance.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                student_name TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                pass_fail TEXT NOT NULL,
                features JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Create feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                feedback TEXT NOT NULL,
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database/student_performance.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    """Decorator for login requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator for admin requirement"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('username') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Landing page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM predictions')
        total_predictions = cursor.fetchone()['count']
        cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE prediction = "Excellent"')
        excellent_count = cursor.fetchone()['count']
        conn.close()
        
        return render_template('index.html', 
                             total_predictions=total_predictions,
                             excellent_count=excellent_count)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not username or not email or not password:
                flash('All fields are required', 'danger')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))
            
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return redirect(url_for('register'))
            
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                    (username, email, generate_password_hash(password))
                )
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username or email already exists', 'danger')
            finally:
                conn.close()
        except Exception as e:
            logger.error(f"Error in register: {str(e)}")
            flash('An error occurred during registration', 'danger')
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Username and password are required', 'danger')
                return redirect(url_for('login'))
            
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        except Exception as e:
            logger.error(f"Error in login: {str(e)}")
            flash('An error occurred during login', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE user_id = ?', (session['user_id'],))
        total_predictions = cursor.fetchone()['count']
        
        cursor.execute('''
            SELECT prediction, COUNT(*) as count 
            FROM predictions 
            WHERE user_id = ?
            GROUP BY prediction
        ''', (session['user_id'],))
        performance_dist = {row['prediction']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('''
            SELECT pass_fail, COUNT(*) as count 
            FROM predictions 
            WHERE user_id = ?
            GROUP BY pass_fail
        ''', (session['user_id'],))
        pass_fail_dist = {row['pass_fail']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('''
            SELECT risk_level, COUNT(*) as count 
            FROM predictions 
            WHERE user_id = ?
            GROUP BY risk_level
        ''', (session['user_id'],))
        risk_dist = {row['risk_level']: row['count'] for row in cursor.fetchall()}
        
        # Get recent predictions
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE user_id = ?
            ORDER BY created_at DESC 
            LIMIT 10
        ''', (session['user_id'],))
        recent_predictions = cursor.fetchall()
        
        # Calculate average metrics
        cursor.execute('''
            SELECT AVG(confidence) as avg_confidence 
            FROM predictions 
            WHERE user_id = ?
        ''', (session['user_id'],))
        avg_confidence = cursor.fetchone()['avg_confidence'] or 0
        
        conn.close()
        
        return render_template('dashboard.html',
                             total_predictions=total_predictions,
                             performance_dist=json.dumps(performance_dist),
                             pass_fail_dist=json.dumps(pass_fail_dist),
                             risk_dist=json.dumps(risk_dist),
                             recent_predictions=recent_predictions,
                             avg_confidence=round(avg_confidence, 2))
    except Exception as e:
        logger.error(f"Error in dashboard: {str(e)}")
        flash('Error loading dashboard', 'danger')
        return render_template('dashboard.html')


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Student prediction form and prediction"""
    if request.method == 'POST':
        try:
            # Collect form data
            student_data = {
                'Age': int(request.form.get('age', 0)),
                'Gender': request.form.get('gender', ''),
                'Attendance_%': float(request.form.get('attendance', 0)),
                'Study_Hours_per_Day': float(request.form.get('study_hours', 0)),
                'Assignments_Completed': int(request.form.get('assignments', 0)),
                'Previous_Semester_Marks': float(request.form.get('previous_marks', 0)),
                'Internal_Assessment_Marks': float(request.form.get('internal_marks', 0)),
                'Class_Participation': int(request.form.get('participation', 0)),
                'Discipline_Score': int(request.form.get('discipline', 0)),
                'Internet_Access': request.form.get('internet_access', ''),
                'Parental_Education': request.form.get('parental_education', ''),
                'Family_Income': request.form.get('family_income', ''),
                'Sleep_Hours': float(request.form.get('sleep_hours', 0)),
                'Extra_Curricular_Activities': int(request.form.get('extra_curricular', 0)),
                'Screen_Time_Hours': float(request.form.get('screen_time', 0)),
                'Tuition': request.form.get('tuition', ''),
                'Stress_Level': int(request.form.get('stress_level', 0)),
                'Learning_Style': request.form.get('learning_style', '')
            }
            
            student_id = request.form.get('student_id', f'STU{int(datetime.now().timestamp())}')
            student_name = request.form.get('student_name', 'Anonymous')
            
            if model is None:
                if not load_model():
                    flash('Model not loaded. Please train the model first.', 'danger')
                    return redirect(url_for('predict'))
            
            # Prepare data for prediction
            df = pd.DataFrame([student_data])
            
            # Apply preprocessing
            df_processed = preprocessor.transform(df)
            
            # Make prediction
            prediction = model.predict(df_processed)[0]
            prediction_proba = model.predict_proba(df_processed)[0]
            confidence = np.max(prediction_proba)
            
            # Determine risk level
            if prediction == 'At Risk':
                risk_level = 'High'
            elif prediction == 'Poor':
                risk_level = 'High'
            elif prediction == 'Average':
                risk_level = 'Medium'
            else:
                risk_level = 'Low'
            
            # Determine Pass/Fail
            pass_fail = 'Pass' if prediction != 'Poor' and prediction != 'At Risk' else 'Fail'
            
            # Store prediction in database
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO predictions 
                (student_id, student_name, prediction, confidence, risk_level, pass_fail, features, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (student_id, student_name, prediction, float(confidence), risk_level, 
                  pass_fail, json.dumps(student_data), session['user_id']))
            conn.commit()
            conn.close()
            
            # Get feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = dict(zip(df.columns, model.feature_importances_))
                feature_importance = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            else:
                feature_importance = []
            
            result = {
                'success': True,
                'prediction': prediction,
                'confidence': f"{confidence*100:.2f}%",
                'risk_level': risk_level,
                'pass_fail': pass_fail,
                'student_id': student_id,
                'student_name': student_name,
                'feature_importance': feature_importance
            }
            
            return render_template('predict.html', result=result)
        
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            flash(f'Error making prediction: {str(e)}', 'danger')
            return render_template('predict.html')
    
    return render_template('predict.html')


@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """API endpoint for predictions (JSON)"""
    try:
        data = request.json
        
        student_data = {
            'Age': data.get('age', 0),
            'Gender': data.get('gender', ''),
            'Attendance_%': data.get('attendance', 0),
            'Study_Hours_per_Day': data.get('study_hours', 0),
            'Assignments_Completed': data.get('assignments', 0),
            'Previous_Semester_Marks': data.get('previous_marks', 0),
            'Internal_Assessment_Marks': data.get('internal_marks', 0),
            'Class_Participation': data.get('participation', 0),
            'Discipline_Score': data.get('discipline', 0),
            'Internet_Access': data.get('internet_access', ''),
            'Parental_Education': data.get('parental_education', ''),
            'Family_Income': data.get('family_income', ''),
            'Sleep_Hours': data.get('sleep_hours', 0),
            'Extra_Curricular_Activities': data.get('extra_curricular', 0),
            'Screen_Time_Hours': data.get('screen_time', 0),
            'Tuition': data.get('tuition', ''),
            'Stress_Level': data.get('stress_level', 0),
            'Learning_Style': data.get('learning_style', '')
        }
        
        if model is None:
            load_model()
        
        df = pd.DataFrame([student_data])
        df_processed = preprocessor.transform(df)
        prediction = model.predict(df_processed)[0]
        confidence = np.max(model.predict_proba(df_processed)[0])
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'confidence': float(confidence)
        })
    except Exception as e:
        logger.error(f"API prediction error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/analytics')
@login_required
def analytics():
    """Analytics dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get performance trends
        cursor.execute('''
            SELECT DATE(created_at) as date, prediction, COUNT(*) as count
            FROM predictions
            WHERE user_id = ?
            GROUP BY DATE(created_at), prediction
            ORDER BY date DESC
            LIMIT 30
        ''', (session['user_id'],))
        trends = cursor.fetchall()
        
        # Get categorical analysis
        cursor.execute('''
            SELECT 
                prediction,
                COUNT(*) as count,
                AVG(confidence) as avg_confidence,
                MIN(confidence) as min_confidence,
                MAX(confidence) as max_confidence
            FROM predictions
            WHERE user_id = ?
            GROUP BY prediction
        ''', (session['user_id'],))
        categorical = cursor.fetchall()
        
        conn.close()
        
        return render_template('analytics.html', trends=trends, categorical=categorical)
    except Exception as e:
        logger.error(f"Error in analytics: {str(e)}")
        flash('Error loading analytics', 'danger')
        return render_template('analytics.html')


@app.route('/model-performance')
def model_performance():
    """Model performance metrics"""
    try:
        if model_info:
            return render_template('model_performance.html', model_info=model_info)
        else:
            flash('Model information not available', 'warning')
            return render_template('model_performance.html')
    except Exception as e:
        logger.error(f"Error in model_performance: {str(e)}")
        return render_template('model_performance.html')


@app.route('/prediction-history')
@login_required
def prediction_history():
    """Prediction history page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE user_id = ?', 
                      (session['user_id'],))
        total = cursor.fetchone()['count']
        
        # Get predictions
        cursor.execute('''
            SELECT * FROM predictions 
            WHERE user_id = ?
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        ''', (session['user_id'], per_page, offset))
        predictions = cursor.fetchall()
        
        conn.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template('prediction_history.html', 
                             predictions=predictions,
                             page=page,
                             total_pages=total_pages,
                             total=total)
    except Exception as e:
        logger.error(f"Error in prediction_history: {str(e)}")
        flash('Error loading prediction history', 'danger')
        return render_template('prediction_history.html')


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM predictions')
        total_predictions = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM users')
        total_users = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM predictions WHERE pass_fail = "Fail"')
        at_risk_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(confidence) as avg FROM predictions')
        avg_confidence = cursor.fetchone()['avg'] or 0
        
        cursor.execute('''
            SELECT * FROM predictions ORDER BY created_at DESC LIMIT 20
        ''')
        all_predictions = cursor.fetchall()
        
        conn.close()
        
        return render_template('admin_dashboard.html',
                             total_predictions=total_predictions,
                             total_users=total_users,
                             at_risk_count=at_risk_count,
                             avg_confidence=round(avg_confidence, 2),
                             all_predictions=all_predictions)
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}")
        return render_template('admin_dashboard.html')


@app.route('/admin/delete-prediction/<int:prediction_id>', methods=['POST'])
@admin_required
def delete_prediction(prediction_id):
    """Delete a prediction"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"Prediction {prediction_id} deleted by admin")
        flash('Prediction deleted successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        logger.error(f"Error deleting prediction: {str(e)}")
        flash('Error deleting prediction', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/export-predictions')
@login_required
def export_predictions():
    """Export predictions as CSV"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC
        ''', (session['user_id'],))
        predictions = cursor.fetchall()
        
        conn.close()
        
        # Create CSV
        output = StringIO()
        if predictions:
            writer = csv.writer(output)
            writer.writerow(['ID', 'Student ID', 'Student Name', 'Prediction', 
                           'Confidence', 'Risk Level', 'Pass/Fail', 'Date'])
            for pred in predictions:
                writer.writerow([
                    pred['id'],
                    pred['student_id'],
                    pred['student_name'],
                    pred['prediction'],
                    f"{pred['confidence']:.2%}",
                    pred['risk_level'],
                    pred['pass_fail'],
                    pred['created_at']
                ])
        
        output.seek(0)
        bytes_io = BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            bytes_io,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
    except Exception as e:
        logger.error(f"Error exporting predictions: {str(e)}")
        flash('Error exporting predictions', 'danger')
        return redirect(url_for('prediction_history'))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            # Log contact message
            logger.info(f"Contact form submission: {name} ({email})")
            
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            logger.error(f"Error processing contact form: {str(e)}")
            flash('Error sending message', 'danger')
    
    return render_template('contact.html')


@app.route('/api/statistics')
def api_statistics():
    """API endpoint for statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM predictions')
        total_predictions = cursor.fetchone()['count']
        
        cursor.execute('SELECT prediction, COUNT(*) as count FROM predictions GROUP BY prediction')
        performance_dist = {row['prediction']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute('SELECT AVG(confidence) as avg FROM predictions')
        avg_confidence = cursor.fetchone()['avg'] or 0
        
        conn.close()
        
        return jsonify({
            'total_predictions': total_predictions,
            'performance_distribution': performance_dist,
            'average_confidence': round(avg_confidence, 4)
        })
    except Exception as e:
        logger.error(f"API statistics error: {str(e)}")
        return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def page_not_found(e):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """500 error handler"""
    logger.error(f"Internal server error: {str(e)}")
    return render_template('500.html'), 500


# ============================================================================
# INITIALIZATION AND MAIN
# ============================================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    os.makedirs('model', exist_ok=True)
    
    # Initialize database
    init_database()
    
    # Load model
    load_model()
    
    # Run application
    app.run(debug=True, host='0.0.0.0', port=5000)
