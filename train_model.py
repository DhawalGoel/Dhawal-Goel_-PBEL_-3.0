"""
AI Student Performance Prediction System
Data Generation and Model Training Script
Author: ML Engineer
Version: 1.0.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, confusion_matrix, 
                             classification_report, roc_curve, auc)
import joblib
import json
import warnings
import os
from datetime import datetime

warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("=" * 80)
print("AI STUDENT PERFORMANCE PREDICTION SYSTEM")
print("Data Generation and Model Training")
print("=" * 80)


# ============================================================================
# STEP 1: GENERATE REALISTIC DATASET
# ============================================================================

def generate_student_dataset(n_samples=10000, random_state=42):
    """Generate a realistic student performance dataset"""
    print("\n[STEP 1] Generating Student Dataset...")
    
    np.random.seed(random_state)
    
    data = {
        'Student_ID': [f'STU{i+1000}' for i in range(n_samples)],
        'Age': np.random.randint(16, 25, n_samples),
        'Gender': np.random.choice(['Male', 'Female', 'Other'], n_samples),
        'Attendance_%': np.random.uniform(40, 100, n_samples),
        'Study_Hours_per_Day': np.random.uniform(0, 8, n_samples),
        'Assignments_Completed': np.random.randint(0, 11, n_samples),
        'Previous_Semester_Marks': np.random.uniform(30, 100, n_samples),
        'Internal_Assessment_Marks': np.random.uniform(20, 100, n_samples),
        'Class_Participation': np.random.randint(0, 11, n_samples),
        'Discipline_Score': np.random.randint(0, 11, n_samples),
        'Internet_Access': np.random.choice(['Yes', 'No', 'Limited'], n_samples),
        'Parental_Education': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD'], n_samples),
        'Family_Income': np.random.choice(['Low', 'Medium', 'High', 'Very High'], n_samples),
        'Sleep_Hours': np.random.uniform(3, 12, n_samples),
        'Extra_Curricular_Activities': np.random.randint(0, 6, n_samples),
        'Screen_Time_Hours': np.random.uniform(0, 12, n_samples),
        'Tuition': np.random.choice(['Yes', 'No', 'Partial'], n_samples),
        'Stress_Level': np.random.randint(1, 11, n_samples),
        'Learning_Style': np.random.choice(['Visual', 'Auditory', 'Kinesthetic', 'Reading'], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable based on features
    # Performance is influenced by multiple factors
    performance_score = (
        df['Attendance_%'] * 0.2 +
        df['Study_Hours_per_Day'] * 8 +
        df['Assignments_Completed'] * 5 +
        df['Previous_Semester_Marks'] * 0.3 +
        df['Internal_Assessment_Marks'] * 0.3 +
        df['Class_Participation'] * 3 +
        df['Discipline_Score'] * 2 +
        (df['Sleep_Hours'] - 3) * 2 +
        df['Extra_Curricular_Activities'] * 1.5 -
        df['Screen_Time_Hours'] * 1 -
        df['Stress_Level'] * 1.5
    )
    
    # Add some randomness
    performance_score += np.random.normal(0, 50, n_samples)
    
    # Classify into performance categories
    def classify_performance(score):
        if score >= 400:
            return 'Excellent'
        elif score >= 300:
            return 'Good'
        elif score >= 200:
            return 'Average'
        elif score >= 100:
            return 'Poor'
        else:
            return 'At Risk'
    
    df['Performance_Category'] = performance_score.apply(classify_performance)
    
    # Create Pass/Fail column
    df['Pass_Fail'] = df['Performance_Category'].apply(
        lambda x: 'Fail' if x in ['Poor', 'At Risk'] else 'Pass'
    )
    
    # Final Grade (0-100)
    df['Final_Grade'] = np.clip(
        (performance_score / 5) + np.random.normal(0, 5, n_samples),
        0, 100
    )
    
    print(f"✓ Generated {n_samples} student records")
    print(f"✓ Dataset shape: {df.shape}")
    print(f"✓ Dataset columns: {df.columns.tolist()}")
    
    return df


# ============================================================================
# STEP 2: EXPLORATORY DATA ANALYSIS
# ============================================================================

def perform_eda(df, save_path='dataset/'):
    """Perform exploratory data analysis"""
    print("\n[STEP 2] Performing Exploratory Data Analysis...")
    
    os.makedirs(save_path, exist_ok=True)
    
    # Basic statistics
    print("\n--- Dataset Info ---")
    print(f"Shape: {df.shape}")
    print(f"Missing values:\n{df.isnull().sum().sum()}")
    print(f"\nData types:\n{df.dtypes}")
    
    # Performance distribution
    print(f"\nPerformance Distribution:\n{df['Performance_Category'].value_counts()}")
    print(f"\nPass/Fail Distribution:\n{df['Pass_Fail'].value_counts()}")
    
    # Numerical statistics
    print(f"\nNumerical Statistics:\n{df.describe()}")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # 1. Performance Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    df['Performance_Category'].value_counts().plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title('Performance Distribution', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count')
    ax.set_xlabel('Performance Category')
    plt.tight_layout()
    plt.savefig(f'{save_path}01_performance_distribution.png', dpi=300)
    plt.close()
    
    # 2. Attendance Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['Attendance_%'], bins=30, color='lightgreen', edgecolor='black')
    ax.set_title('Attendance Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Attendance %')
    ax.set_ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{save_path}02_attendance_distribution.png', dpi=300)
    plt.close()
    
    # 3. Marks Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['Final_Grade'], bins=30, color='salmon', edgecolor='black')
    ax.set_title('Final Grade Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Final Grade')
    ax.set_ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{save_path}03_marks_distribution.png', dpi=300)
    plt.close()
    
    # 4. Gender Comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    gender_perf = pd.crosstab(df['Gender'], df['Performance_Category'])
    gender_perf.plot(kind='bar', ax=ax)
    ax.set_title('Performance by Gender', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count')
    ax.set_xlabel('Gender')
    plt.xticks(rotation=0)
    plt.legend(title='Performance')
    plt.tight_layout()
    plt.savefig(f'{save_path}04_gender_comparison.png', dpi=300)
    plt.close()
    
    # 5. Study Hours Analysis
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['Study_Hours_per_Day'], bins=30, color='lightblue', edgecolor='black')
    ax.set_title('Study Hours Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Study Hours per Day')
    ax.set_ylabel('Count')
    plt.tight_layout()
    plt.savefig(f'{save_path}05_study_hours_distribution.png', dpi=300)
    plt.close()
    
    # 6. Correlation Heatmap
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr_matrix = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', ax=ax, cbar_kws={'label': 'Correlation'})
    ax.set_title('Feature Correlation Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{save_path}06_correlation_heatmap.png', dpi=300)
    plt.close()
    
    # 7. Stress Level vs Performance
    fig, ax = plt.subplots(figsize=(10, 6))
    stress_perf = pd.crosstab(df['Stress_Level'], df['Performance_Category'])
    stress_perf.plot(kind='bar', ax=ax)
    ax.set_title('Performance by Stress Level', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count')
    ax.set_xlabel('Stress Level')
    plt.xticks(rotation=0)
    plt.legend(title='Performance')
    plt.tight_layout()
    plt.savefig(f'{save_path}07_stress_vs_performance.png', dpi=300)
    plt.close()
    
    # 8. Sleep Hours vs Performance
    fig, ax = plt.subplots(figsize=(10, 6))
    for perf in df['Performance_Category'].unique():
        data = df[df['Performance_Category'] == perf]['Sleep_Hours']
        ax.hist(data, alpha=0.5, label=perf, bins=15)
    ax.set_title('Sleep Hours by Performance', fontsize=14, fontweight='bold')
    ax.set_xlabel('Sleep Hours')
    ax.set_ylabel('Count')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{save_path}08_sleep_vs_performance.png', dpi=300)
    plt.close()
    
    # 9. Attendance vs Final Grade (Scatter)
    fig, ax = plt.subplots(figsize=(10, 6))
    for perf in df['Performance_Category'].unique():
        mask = df['Performance_Category'] == perf
        ax.scatter(df[mask]['Attendance_%'], df[mask]['Final_Grade'], 
                  label=perf, alpha=0.5, s=20)
    ax.set_title('Attendance vs Final Grade', fontsize=14, fontweight='bold')
    ax.set_xlabel('Attendance %')
    ax.set_ylabel('Final Grade')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{save_path}09_attendance_vs_grade.png', dpi=300)
    plt.close()
    
    # 10. Assignment Completion Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    assign_perf = pd.crosstab(df['Assignments_Completed'], df['Performance_Category'])
    assign_perf.plot(kind='bar', ax=ax)
    ax.set_title('Performance by Assignments Completed', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count')
    ax.set_xlabel('Assignments Completed')
    plt.xticks(rotation=45)
    plt.legend(title='Performance')
    plt.tight_layout()
    plt.savefig(f'{save_path}10_assignments_vs_performance.png', dpi=300)
    plt.close()
    
    print("✓ EDA visualizations saved to 'dataset/' directory")
    
    return df


# ============================================================================
# STEP 3: DATA PREPROCESSING
# ============================================================================

def preprocess_data(df):
    """Preprocess the data for model training"""
    print("\n[STEP 3] Preprocessing Data...")
    
    # Create a copy
    df_processed = df.copy()
    
    # Remove Student_ID as it's just an identifier
    if 'Student_ID' in df_processed.columns:
        df_processed = df_processed.drop('Student_ID', axis=1)
    
    # Check for missing values
    print(f"✓ Missing values: {df_processed.isnull().sum().sum()}")
    
    # Remove duplicates
    df_processed = df_processed.drop_duplicates()
    print(f"✓ After removing duplicates: {df_processed.shape[0]} records")
    
    # Outlier detection and handling (IQR method)
    numeric_cols = df_processed.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        Q1 = df_processed[col].quantile(0.25)
        Q3 = df_processed[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        df_processed = df_processed[(df_processed[col] >= lower_bound) & (df_processed[col] <= upper_bound)]
    
    print(f"✓ After outlier removal: {df_processed.shape[0]} records")
    
    # Separate features and target
    X = df_processed.drop(['Performance_Category', 'Pass_Fail', 'Final_Grade'], axis=1)
    y = df_processed['Performance_Category']
    
    print(f"✓ Features shape: {X.shape}")
    print(f"✓ Target shape: {y.shape}")
    print(f"✓ Target classes: {y.unique()}")
    print(f"✓ Class distribution:\n{y.value_counts()}")
    
    # Identify categorical and numerical columns
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    print(f"✓ Categorical columns: {categorical_cols}")
    print(f"✓ Numerical columns: {numerical_cols}")
    
    return X, y, categorical_cols, numerical_cols


# ============================================================================
# STEP 4: FEATURE ENGINEERING AND SCALING
# ============================================================================

def create_preprocessing_pipeline(categorical_cols, numerical_cols):
    """Create preprocessing pipeline"""
    print("\n[STEP 4] Creating Preprocessing Pipeline...")
    
    # Preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ]
    )
    
    print("✓ Preprocessing pipeline created")
    return preprocessor


# ============================================================================
# STEP 5: TRAIN MULTIPLE MODELS
# ============================================================================

def train_models(X_train, X_test, y_train, y_test, preprocessor):
    """Train multiple models and compare performance"""
    print("\n[STEP 5] Training Multiple Models...")
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=20, 
                                                random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=5, 
                                                        random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=20, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Support Vector Machine': SVC(kernel='rbf', probability=True, random_state=42)
    }
    
    results = {}
    
    for model_name, model in models.items():
        print(f"\n--- Training {model_name} ---")
        
        # Create pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('model', model)
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Predict
        y_pred = pipeline.predict(X_test)
        y_pred_proba = pipeline.predict_proba(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # ROC-AUC for binary classification
        try:
            roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', average='weighted')
        except:
            roc_auc = 0
        
        results[model_name] = {
            'model': pipeline,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': roc_auc,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        print(f"✓ Accuracy:  {accuracy:.4f}")
        print(f"✓ Precision: {precision:.4f}")
        print(f"✓ Recall:    {recall:.4f}")
        print(f"✓ F1-Score:  {f1:.4f}")
        print(f"✓ ROC-AUC:   {roc_auc:.4f}")
    
    return results


# ============================================================================
# STEP 6: MODEL EVALUATION AND COMPARISON
# ============================================================================

def evaluate_and_select_best_model(results, y_test, save_path='dataset/'):
    """Evaluate models and select the best one"""
    print("\n[STEP 6] Model Evaluation and Selection...")
    
    # Create comparison dataframe
    comparison_df = pd.DataFrame({
        model_name: {
            'Accuracy': results[model_name]['accuracy'],
            'Precision': results[model_name]['precision'],
            'Recall': results[model_name]['recall'],
            'F1-Score': results[model_name]['f1_score'],
            'ROC-AUC': results[model_name]['roc_auc']
        }
        for model_name in results.keys()
    }).T
    
    print("\n--- Model Comparison ---")
    print(comparison_df)
    
    # Select best model based on F1-Score
    best_model_name = comparison_df['F1-Score'].idxmax()
    best_model = results[best_model_name]['model']
    
    print(f"\n✓ Best Model Selected: {best_model_name}")
    print(f"  F1-Score: {comparison_df.loc[best_model_name, 'F1-Score']:.4f}")
    
    # Generate visualizations
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Accuracy comparison
    comparison_df['Accuracy'].plot(kind='barh', ax=axes[0, 0], color='skyblue')
    axes[0, 0].set_title('Model Accuracy Comparison', fontweight='bold')
    axes[0, 0].set_xlabel('Accuracy')
    
    # Precision comparison
    comparison_df['Precision'].plot(kind='barh', ax=axes[0, 1], color='lightgreen')
    axes[0, 1].set_title('Model Precision Comparison', fontweight='bold')
    axes[0, 1].set_xlabel('Precision')
    
    # Recall comparison
    comparison_df['Recall'].plot(kind='barh', ax=axes[1, 0], color='salmon')
    axes[1, 0].set_title('Model Recall Comparison', fontweight='bold')
    axes[1, 0].set_xlabel('Recall')
    
    # F1-Score comparison
    comparison_df['F1-Score'].plot(kind='barh', ax=axes[1, 1], color='gold')
    axes[1, 1].set_title('Model F1-Score Comparison', fontweight='bold')
    axes[1, 1].set_xlabel('F1-Score')
    
    plt.tight_layout()
    plt.savefig(f'{save_path}11_model_comparison.png', dpi=300)
    plt.close()
    
    # Confusion Matrix for best model
    y_pred_best = results[best_model_name]['y_pred']
    cm = confusion_matrix(y_test, y_pred_best)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=np.unique(y_test),
                yticklabels=np.unique(y_test))
    ax.set_title(f'Confusion Matrix - {best_model_name}', fontweight='bold')
    ax.set_ylabel('True Label')
    ax.set_xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'{save_path}12_confusion_matrix.png', dpi=300)
    plt.close()
    
    # Classification Report
    print(f"\n--- Classification Report ({best_model_name}) ---")
    print(classification_report(y_test, y_pred_best))
    
    print("✓ Evaluation visualizations saved")
    
    return best_model, best_model_name, comparison_df.T.to_dict()


# ============================================================================
# STEP 7: FEATURE IMPORTANCE ANALYSIS
# ============================================================================

def analyze_feature_importance(best_model, X_train, categorical_cols, 
                               numerical_cols, save_path='dataset/'):
    """Analyze and visualize feature importance"""
    print("\n[STEP 7] Analyzing Feature Importance...")
    
    # Get the actual model from pipeline
    actual_model = best_model.named_steps['model']
    
    if hasattr(actual_model, 'feature_importances_'):
        # Get preprocessor
        preprocessor = best_model.named_steps['preprocessor']
        
        # Get feature names
        feature_names = []
        
        # Numerical features
        feature_names.extend(numerical_cols)
        
        # Categorical features (after one-hot encoding)
        cat_encoder = preprocessor.named_transformers_['cat']
        if hasattr(cat_encoder, 'get_feature_names_out'):
            cat_feature_names = cat_encoder.get_feature_names_out(categorical_cols)
            feature_names.extend(cat_feature_names)
        else:
            for col in categorical_cols:
                feature_names.extend([f"{col}_{val}" for val in cat_encoder.categories_[categorical_cols.index(col)]])
        
        # Get importance
        importances = actual_model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'Feature': feature_names[:len(importances)],
            'Importance': importances
        }).sort_values('Importance', ascending=False)
        
        print("\n--- Top 20 Important Features ---")
        print(feature_importance_df.head(20))
        
        # Visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        feature_importance_df.head(20).plot(x='Feature', y='Importance', kind='barh', ax=ax, color='steelblue')
        ax.set_title('Top 20 Feature Importance', fontweight='bold', fontsize=14)
        ax.set_xlabel('Importance Score')
        plt.tight_layout()
        plt.savefig(f'{save_path}13_feature_importance.png', dpi=300)
        plt.close()
        
        print("✓ Feature importance visualization saved")
        
        return feature_importance_df.head(20).to_dict('records')
    else:
        print("⚠ Model does not support feature importance")
        return []


# ============================================================================
# STEP 8: SAVE MODEL AND ARTIFACTS
# ============================================================================

def save_model_and_artifacts(best_model, preprocessor, best_model_name, 
                             model_metrics, feature_importance, X_train):
    """Save trained model and preprocessing artifacts"""
    print("\n[STEP 8] Saving Model and Artifacts...")
    
    os.makedirs('model', exist_ok=True)
    
    # Save model
    joblib.dump(best_model, 'model/student_performance_model.pkl')
    print("✓ Model saved: model/student_performance_model.pkl")
    
    # Save preprocessor
    joblib.dump(preprocessor, 'model/preprocessor.pkl')
    print("✓ Preprocessor saved: model/preprocessor.pkl")
    
    # Save model info
    model_info = {
        'name': best_model_name,
        'accuracy': float(model_metrics[best_model_name]['Accuracy']),
        'precision': float(model_metrics[best_model_name]['Precision']),
        'recall': float(model_metrics[best_model_name]['Recall']),
        'f1_score': float(model_metrics[best_model_name]['F1-Score']),
        'roc_auc': float(model_metrics[best_model_name]['ROC-AUC']),
        'feature_importance': feature_importance,
        'training_date': datetime.now().isoformat(),
        'feature_names': X_train.columns.tolist()
    }
    
    with open('model/model_info.json', 'w') as f:
        json.dump(model_info, f, indent=4)
    
    print("✓ Model info saved: model/model_info.json")
    
    # Save training data sample
    X_train.head(100).to_csv('model/training_sample.csv', index=False)
    print("✓ Training sample saved: model/training_sample.csv")
    
    print("\n✓ All artifacts saved successfully")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    try:
        # Step 1: Generate Dataset
        df = generate_student_dataset(n_samples=10000)
        df.to_csv('dataset/student_performance_data.csv', index=False)
        print("✓ Dataset saved: dataset/student_performance_data.csv")
        
        # Step 2: EDA
        df = perform_eda(df)
        
        # Step 3: Preprocessing
        X, y, categorical_cols, numerical_cols = preprocess_data(df)
        
        # Step 4: Create preprocessing pipeline
        preprocessor = create_preprocessing_pipeline(categorical_cols, numerical_cols)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        print(f"\nTrain-Test Split:")
        print(f"✓ X_train shape: {X_train.shape}")
        print(f"✓ X_test shape: {X_test.shape}")
        
        # Step 5: Train models
        results = train_models(X_train, X_test, y_train, y_test, preprocessor)
        
        # Step 6: Evaluate and select best model
        best_model, best_model_name, model_metrics = evaluate_and_select_best_model(results, y_test)
        
        # Step 7: Feature importance
        feature_importance = analyze_feature_importance(best_model, X_train, 
                                                       categorical_cols, numerical_cols)
        
        # Step 8: Save artifacts
        save_model_and_artifacts(best_model, preprocessor, best_model_name, 
                                model_metrics, feature_importance, X)
        
        print("\n" + "=" * 80)
        print("✓ MODEL TRAINING COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nBest Model: {best_model_name}")
        print(f"Model Accuracy: {model_metrics[best_model_name]['Accuracy']:.4f}")
        print(f"Model F1-Score: {model_metrics[best_model_name]['F1-Score']:.4f}")
        print("\nYou can now run the Flask application with: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
