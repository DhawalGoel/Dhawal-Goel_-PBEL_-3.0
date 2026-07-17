# Installation & Setup Guide

## Quick Start (5 Minutes)

### Windows Users
```batch
# 1. Extract the zip file
# 2. Open Command Prompt in the folder
# 3. Run:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train_model.py
python app.py
```

### macOS/Linux Users
```bash
# 1. Extract the zip file
# 2. Open Terminal in the folder
# 3. Run:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python train_model.py
python app.py
```

---

## Detailed Installation

### Prerequisites Check
```bash
python --version     # Should be 3.9 or higher
pip --version        # Should be 21.0 or higher
```

If not, download from https://www.python.org/downloads/

### Step-by-Step Installation

#### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed flask-2.3.3 pandas-2.0.3 scikit-learn-1.3.0 ...
```

#### 3. Create Necessary Directories
```bash
mkdir -p database model dataset logs uploads
```

#### 4. Generate Training Data & Train Model
```bash
python train_model.py
```

**This process:**
- Generates 10,000 student records
- Creates 13 EDA visualizations
- Trains 5 ML algorithms
- Selects the best model
- Saves all artifacts

**Expected time:** 2-5 minutes

**Output files created:**
- `dataset/student_performance_data.csv` - Generated dataset
- `dataset/*.png` - Visualizations
- `model/student_performance_model.pkl` - Trained model
- `model/preprocessor.pkl` - Data preprocessor
- `model/model_info.json` - Model metadata

#### 5. Initialize Database (Optional - Auto-created)
```bash
python -c "from app import init_database; init_database(); print('✓ Database initialized')"
```

#### 6. Create Admin User (Optional)
```bash
python -c "
from app import app, init_database, get_db_connection
from werkzeug.security import generate_password_hash

init_database()
conn = get_db_connection()
try:
    conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                ('admin', 'admin@example.com', generate_password_hash('admin123')))
    conn.commit()
    print('✓ Admin user created: admin / admin123')
except:
    print('✓ Admin user already exists')
finally:
    conn.close()
"
```

#### 7. Run the Application
```bash
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

#### 8. Access the Application
Open your browser and go to:
```
http://localhost:5000
```

---

## Using the Application

### First Time Setup

1. **Register Account**
   - Click "Register" on the home page
   - Enter username, email, password
   - Click "Create Account"
   - Login with your credentials

2. **Make Your First Prediction**
   - Click "Predict" in navigation
   - Fill in all student details
   - Click "Predict Performance"
   - View results and recommendations

3. **Explore Dashboard**
   - Go to "Dashboard" to view analytics
   - Check "History" for past predictions
   - View "Analytics" for advanced insights

### Default Credentials
```
Username: admin
Password: admin123
```

---

## Troubleshooting

### Issue: "Python not found"
**Solution:**
```bash
# Check if Python is installed
python --version

# If not, download from python.org
# After installation, restart terminal/command prompt
```

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Then reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Model file not found"
**Solution:**
```bash
# Train the model
python train_model.py

# Verify model files exist
ls -la model/  # macOS/Linux
dir model\    # Windows
```

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Option 1: Use different port
python -c "from app import app; app.run(port=5001)"

# Option 2: Kill process using port 5000
# macOS/Linux:
lsof -ti:5000 | xargs kill -9

# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: "Database locked"
**Solution:**
```bash
# Remove old database
rm database/student_performance.db

# Reinitialize
python app.py
```

### Issue: "Out of memory during model training"
**Solution:**
```bash
# Reduce dataset size in train_model.py
# Line: df = generate_student_dataset(n_samples=5000)  # Changed from 10000

python train_model.py
```

---

## Configuration

### Change Application Port
Edit `app.py` (last line):
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)  # Changed from 5000
```

### Change Secret Key (Important for Production)
Edit `app.py` (line 22):
```python
app.config['SECRET_KEY'] = 'your-very-secure-key-here-32-chars-min'
```

### Enable/Disable Debug Mode
```python
app.run(debug=False)  # False for production
```

---

## Production Deployment

### Using Gunicorn
```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run on specific port
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker
```bash
# Build image
docker build -t student-performance-app .

# Run container
docker run -p 5000:5000 student-performance-app
```

### Using Heroku
```bash
# 1. Create Procfile
echo "web: gunicorn app:app" > Procfile

# 2. Deploy
heroku login
heroku create your-app-name
git push heroku main
```

---

## Updating the Project

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Retrain Model
```bash
# Back up old model
mv model/student_performance_model.pkl model/backup_model.pkl

# Retrain
python train_model.py
```

### Clear Cache
```bash
# Remove __pycache__
find . -type d -name __pycache__ -exec rm -r {} +

# Remove .pyc files
find . -type f -name '*.pyc' -delete
```

---

## System Requirements

### Minimum
- **CPU**: Dual-core processor
- **RAM**: 2 GB
- **Storage**: 500 MB
- **OS**: Windows 7+, macOS 10.14+, Linux

### Recommended
- **CPU**: Quad-core processor
- **RAM**: 4 GB
- **Storage**: 2 GB
- **OS**: Windows 10+, macOS 11+, Ubuntu 18.04+

---

## Verification Checklist

After installation, verify:

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (pip list shows flask, pandas, etc.)
- [ ] Model files exist in `model/` directory
- [ ] Database created in `database/` directory
- [ ] Application runs without errors
- [ ] Landing page loads at http://localhost:5000
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can make a prediction
- [ ] Dashboard displays data

---

## Support

For issues:
1. Check Troubleshooting section above
2. Review `logs/app.log` for error details
3. Check GitHub Issues
4. Contact support@aistudent.com

---

## Next Steps

After successful installation:

1. **Read README.md** for full documentation
2. **Explore the UI** - Try making predictions
3. **Review EDA** - Check visualizations in `dataset/` folder
4. **Customize** - Modify app.py for your needs
5. **Deploy** - Use Gunicorn/Docker for production

Enjoy your AI Student Performance Prediction System! 🎉
