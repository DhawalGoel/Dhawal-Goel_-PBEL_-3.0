/**
 * AI Student Performance Prediction System
 * Main JavaScript File
 */

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Show loading spinner
 */
function showLoading(element) {
    const loader = document.createElement('div');
    loader.className = 'loader mx-auto';
    element.innerHTML = '';
    element.appendChild(loader);
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Get performance badge color
 */
function getPerformanceBadgeClass(performance) {
    const colors = {
        'Excellent': 'badge-excellent',
        'Good': 'badge-good',
        'Average': 'badge-average',
        'Poor': 'badge-poor',
        'At Risk': 'badge-at-risk'
    };
    return colors[performance] || 'badge-secondary';
}

/**
 * Get risk level badge color
 */
function getRiskBadgeClass(riskLevel) {
    const colors = {
        'Low': 'bg-success',
        'Medium': 'bg-warning',
        'High': 'bg-danger'
    };
    return colors[riskLevel] || 'bg-secondary';
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

/**
 * Validate prediction form
 */
function validatePredictionForm() {
    const form = document.getElementById('predictionForm');
    const inputs = form.querySelectorAll('input, select');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

/**
 * Validate registration form
 */
function validateRegistrationForm() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    
    if (password.value !== confirmPassword.value) {
        alert('Passwords do not match');
        return false;
    }
    
    if (password.value.length < 6) {
        alert('Password must be at least 6 characters');
        return false;
    }
    
    return true;
}

// ============================================================================
// CHARTS AND VISUALIZATIONS
// ============================================================================

/**
 * Initialize performance distribution chart
 */
function initPerformanceChart(elementId, data) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    const colors = {
        'Excellent': '#10b981',
        'Good': '#3b82f6',
        'Average': '#f59e0b',
        'Poor': '#ef4444',
        'At Risk': '#8b008b'
    };

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: Object.keys(data).map(key => colors[key]),
                borderColor: '#1e293b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize bar chart
 */
function initBarChart(elementId, labels, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                backgroundColor: '#6366f1',
                borderColor: '#8b5cf6',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0'
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#e2e8f0'
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#e2e8f0'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize line chart
 */
function initLineChart(elementId, labels, datasets) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;

    const colors = ['#6366f1', '#8b5cf6', '#10b981', '#ef4444', '#f59e0b'];

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map((dataset, index) => ({
                label: dataset.label,
                data: dataset.data,
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                tension: 0.4,
                fill: true,
                borderWidth: 2
            }))
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0'
                    }
                }
            },
            scales: {
                y: {
                    ticks: {
                        color: '#e2e8f0'
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#e2e8f0'
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// ============================================================================
// API CALLS
// ============================================================================

/**
 * Make API prediction call
 */
async function makeAPIPrediction(formData) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            throw new Error('API error');
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Prediction Error:', error);
        return null;
    }
}

/**
 * Fetch statistics
 */
async function fetchStatistics() {
    try {
        const response = await fetch('/api/statistics');
        if (!response.ok) throw new Error('Failed to fetch statistics');
        return await response.json();
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return null;
    }
}

// ============================================================================
// INITIALIZATION ON PAGE LOAD
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// ============================================================================
// PREDICTION FORM HANDLERS
// ============================================================================

/**
 * Handle prediction form submission
 */
function handlePredictionSubmit(form) {
    if (!validatePredictionForm()) {
        alert('Please fill in all fields');
        return false;
    }
    return true;
}

// ============================================================================
// TABLE OPERATIONS
// ============================================================================

/**
 * Delete prediction (admin)
 */
function deletePrediction(predictionId) {
    if (confirm('Are you sure you want to delete this prediction?')) {
        document.getElementById(`deleteForm${predictionId}`).submit();
    }
}

/**
 * Filter table
 */
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const rows = table.getElementsByTagName('tr');
    const filter = input.value.toUpperCase();

    for (let i = 1; i < rows.length; i++) {
        const text = rows[i].textContent || rows[i].innerText;
        rows[i].style.display = text.toUpperCase().indexOf(filter) > -1 ? '' : 'none';
    }
}

/**
 * Sort table column
 */
function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    const rows = Array.from(table.getElementsByTagName('tr')).slice(1);
    const isAsc = !table.getAttribute('data-sort-asc');

    rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent;
        const bVal = b.cells[columnIndex].textContent;
        return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });

    table.setAttribute('data-sort-asc', isAsc);
    rows.forEach(row => table.appendChild(row));
}

// ============================================================================
// EXPORT FUNCTIONALITY
// ============================================================================

/**
 * Export table to CSV
 */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        cols.forEach(col => {
            csvRow.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        csv.push(csvRow.join(','));
    });

    downloadCSV(csv.join('\n'), filename);
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
    const link = document.createElement('a');
    link.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
    link.download = filename;
    link.click();
}

// ============================================================================
// DARK MODE TOGGLE
// ============================================================================

/**
 * Toggle dark/light mode
 */
function toggleDarkMode() {
    document.body.classList.toggle('light-mode');
    localStorage.setItem('darkMode', !document.body.classList.contains('light-mode'));
}

// Load dark mode preference
window.addEventListener('load', function() {
    const isDarkMode = localStorage.getItem('darkMode') !== 'false';
    if (!isDarkMode) {
        document.body.classList.add('light-mode');
    }
});

// ============================================================================
// NOTIFICATION SYSTEM
// ============================================================================

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';

    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    const container = document.querySelector('.container-fluid');
    container.insertBefore(alert, container.firstChild);

    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
}

// ============================================================================
// UTILITY ANIMATIONS
// ============================================================================

/**
 * Animate number counting
 */
function animateCounter(element, target, duration = 1000) {
    let current = 0;
    const increment = target / (duration / 16);
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

/**
 * Add fade-in animation
 */
function fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease-in`;
    
    setTimeout(() => {
        element.style.opacity = '1';
    }, 10);
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K: Focus search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) searchInput.focus();
    }

    // Escape: Close modals
    if (event.key === 'Escape') {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            bootstrap.Modal.getInstance(modal).hide();
        }
    }
});

// ============================================================================
// LOCAL STORAGE UTILITIES
// ============================================================================

/**
 * Save to local storage
 */
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Storage error:', error);
    }
}

/**
 * Load from local storage
 */
function loadFromStorage(key) {
    try {
        return JSON.parse(localStorage.getItem(key));
    } catch (error) {
        console.error('Storage error:', error);
        return null;
    }
}

/**
 * Clear storage
 */
function clearStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('Storage error:', error);
    }
}

console.log('AI Student Performance System - JavaScript Loaded Successfully');
