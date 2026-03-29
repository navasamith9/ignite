// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOut 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
});

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                isValid = false;
            } else {
                field.classList.remove('error');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showNotification('Please fill all required fields', 'error');
        }
    });
});

// OTP input auto-focus
const otpInputs = document.querySelectorAll('input[name="otp"]');
otpInputs.forEach(input => {
    input.addEventListener('input', function(e) {
        if (this.value.length === 6) {
            this.form.submit();
        }
    });
});

// Date picker minimum date
const dateInputs = document.querySelectorAll('input[type="date"]');
dateInputs.forEach(input => {
    if (!input.value) {
        const today = new Date().toISOString().split('T')[0];
        input.min = today;
    }
});

// Number of tickets validation
const ticketInput = document.querySelector('input[name="num_tickets"]');
if (ticketInput) {
    ticketInput.addEventListener('change', function() {
        const max = parseInt(this.max);
        const value = parseInt(this.value);
        if (value > max) {
            this.value = max;
            showNotification(`Maximum ${max} tickets allowed per booking`, 'warning');
        }
        if (value < 1) {
            this.value = 1;
        }
    });
}

// Room capacity warning
const strengthInput = document.querySelector('input[name="estimated_strength"]');
const roomSelect = document.querySelector('select[name="room"]');
if (strengthInput && roomSelect) {
    function checkCapacity() {
        const selectedRoom = roomSelect.options[roomSelect.selectedIndex];
        if (selectedRoom && selectedRoom.dataset.capacity) {
            const capacity = parseInt(selectedRoom.dataset.capacity);
            const strength = parseInt(strengthInput.value);
            
            if (strength > capacity) {
                strengthInput.classList.add('error');
                showNotification(`Room capacity is ${capacity}. Please choose a larger room.`, 'warning');
            } else if (strength > capacity * 0.9) {
                strengthInput.classList.add('warning');
                showNotification(`Room is nearly full! ${strength}/${capacity} seats`, 'info');
            } else {
                strengthInput.classList.remove('error', 'warning');
            }
        }
    }
    
    strengthInput.addEventListener('change', checkCapacity);
    roomSelect.addEventListener('change', checkCapacity);
}

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.messages');
    if (container) {
        container.appendChild(notification);
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 5000);
    }
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .error {
        border-color: #dc3545 !important;
        background-color: #fff5f5 !important;
    }
    
    .warning {
        border-color: #ffc107 !important;
        background-color: #fffbf0 !important;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 5px;
        transition: width 0.3s ease;
    }
    
    .seats-progress {
        background: #e1e1e1;
        border-radius: 5px;
        height: 8px;
        overflow: hidden;
        margin-top: 5px;
    }
`;

document.head.appendChild(style);