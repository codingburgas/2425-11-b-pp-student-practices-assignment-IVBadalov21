/**
 * Main JavaScript file for Language Detector Application
 * Handles UI interactions, form validation, and dynamic content
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    initializeCharacterCount();
    initializeFormValidation();
    initializeTooltips();
    initializeConfidenceSliders();
    initializeLanguageExamples();
    initializeProgressBars();
    initializeConfirmationDialogs();
    initializeAutoRefresh();
}

/**
 * Character count functionality for text areas
 */
function initializeCharacterCount() {
    const textAreas = document.querySelectorAll('textarea[maxlength]');
    
    textAreas.forEach(textArea => {
        const maxLength = textArea.getAttribute('maxlength') || 5000;
        const countElement = document.getElementById('charCount');
        
        if (countElement) {
            updateCharCount(textArea, countElement, maxLength);
            
            textArea.addEventListener('input', function() {
                updateCharCount(this, countElement, maxLength);
            });
        }
    });
}

/**
 * Update character count display
 */
function updateCharCount(textArea = null, countElement = null, maxLength = 5000) {
    if (!textArea) {
        textArea = document.getElementById('input_text') || document.getElementById('text_sample');
    }
    if (!countElement) {
        countElement = document.getElementById('charCount');
    }
    
    if (textArea && countElement) {
        const currentLength = textArea.value.length;
        countElement.textContent = `${currentLength} / ${maxLength}`;
        
        // Color coding based on usage
        if (currentLength > maxLength * 0.9) {
            countElement.className = 'text-danger';
        } else if (currentLength > maxLength * 0.7) {
            countElement.className = 'text-warning';
        } else {
            countElement.className = 'text-muted';
        }
    }
}

/**
 * Form validation enhancements
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this)) {
                event.preventDefault();
                event.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    
    // Text area validation
    const textAreas = form.querySelectorAll('textarea[required]');
    textAreas.forEach(textArea => {
        const text = textArea.value.trim();
        if (text.length < 5) {
            showFieldError(textArea, 'Text must be at least 5 characters long');
            isValid = false;
        } else if (text.length > 5000) {
            showFieldError(textArea, 'Text must be less than 5000 characters');
            isValid = false;
        }
    });
    
    // Email validation
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(email => {
        if (email.value && !isValidEmail(email.value)) {
            showFieldError(email, 'Please enter a valid email address');
            isValid = false;
        }
    });
    
    // Password confirmation
    const password = form.querySelector('input[name="password"]');
    const password2 = form.querySelector('input[name="password2"]');
    if (password && password2 && password.value !== password2.value) {
        showFieldError(password2, 'Passwords do not match');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Show field error message
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    errorDiv.textContent = message;
}

/**
 * Email validation
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (tooltipTriggerList.length > 0 && typeof bootstrap !== 'undefined') {
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
            new bootstrap.Tooltip(tooltipTriggerEl)
        );
    }
}

/**
 * Confidence slider enhancements
 */
function initializeConfidenceSliders() {
    const confidenceSlider = document.getElementById('confidence');
    const confidenceDisplay = document.getElementById('confidenceDisplay');
    
    if (confidenceSlider && confidenceDisplay) {
        confidenceSlider.addEventListener('input', function() {
            const value = Math.round(this.value * 100);
            confidenceDisplay.textContent = `${value}%`;
            
            // Color coding
            if (value >= 80) {
                confidenceDisplay.className = 'badge bg-success';
            } else if (value >= 60) {
                confidenceDisplay.className = 'badge bg-warning';
            } else {
                confidenceDisplay.className = 'badge bg-danger';
            }
        });
    }
}

/**
 * Language example insertion
 */
function initializeLanguageExamples() {
    const exampleButtons = document.querySelectorAll('[onclick^="setExampleText"]');
    
    exampleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const text = this.getAttribute('onclick').match(/setExampleText\('(.+)'\)/)[1];
            setExampleText(text);
        });
    });
}

/**
 * Set example text in form
 */
function setExampleText(text) {
    const textField = document.getElementById('input_text') || document.getElementById('text_sample');
    if (textField) {
        textField.value = text.replace(/\\'/g, "'");
        updateCharCount();
        
        // Scroll to text field and focus
        textField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        textField.focus();
        
        // Add visual feedback
        textField.classList.add('border-success');
        setTimeout(() => {
            textField.classList.remove('border-success');
        }, 2000);
    }
}

/**
 * Animated progress bars
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    // Intersection Observer for scroll-triggered animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                
                setTimeout(() => {
                    progressBar.style.width = width;
                    progressBar.style.transition = 'width 1s ease-out';
                }, 100);
                
                observer.unobserve(progressBar);
            }
        });
    }, { threshold: 0.5 });
    
    progressBars.forEach(bar => {
        observer.observe(bar);
    });
}

/**
 * Confirmation dialogs for dangerous actions
 */
function initializeConfirmationDialogs() {
    const dangerousButtons = document.querySelectorAll('[data-confirm]');
    
    dangerousButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Auto-refresh functionality for admin pages
 */
function initializeAutoRefresh() {
    const autoRefreshElements = document.querySelectorAll('[data-auto-refresh]');
    
    autoRefreshElements.forEach(element => {
        const interval = parseInt(element.getAttribute('data-auto-refresh')) * 1000;
        const url = element.getAttribute('data-refresh-url') || window.location.href;
        
        if (interval > 0) {
            setInterval(() => {
                fetch(url)
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');
                        const newElement = doc.querySelector(element.tagName + element.className.split(' ').map(c => '.' + c).join(''));
                        
                        if (newElement) {
                            element.innerHTML = newElement.innerHTML;
                        }
                    })
                    .catch(error => {
                        console.warn('Auto-refresh failed:', error);
                    });
            }, interval);
        }
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Text copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

/**
 * Fallback copy function
 */
function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Text copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy text: ', err);
        showNotification('Failed to copy text', 'error');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.style.minWidth = '300px';
    
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

/**
 * Format confidence scores for display
 */
function formatConfidenceScores(scores) {
    const sortedScores = Object.entries(scores)
        .sort(([,a], [,b]) => b - a);
    
    return sortedScores.map(([lang, score]) => {
        const percentage = (score * 100).toFixed(1);
        const langName = getLanguageName(lang);
        return `${langName}: ${percentage}%`;
    }).join(', ');
}

/**
 * Get language display name
 */
function getLanguageName(code) {
    const languages = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'bg': 'Bulgarian',
        'de': 'German'
    };
    return languages[code] || code.toUpperCase();
}

/**
 * Get language flag emoji
 */
function getLanguageFlag(code) {
    const flags = {
        'en': '🇺🇸',
        'es': '🇪🇸',
        'fr': '🇫🇷',
        'bg': '🇧🇬',
        'de': '🇩🇪'
    };
    return flags[code] || '🌐';
}

/**
 * Smooth scroll to element
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    }
}

/**
 * Loading state management
 */
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        const originalText = element.textContent;
        element.setAttribute('data-original-text', originalText);
        element.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        const originalText = element.getAttribute('data-original-text');
        if (originalText) {
            element.textContent = originalText;
            element.removeAttribute('data-original-text');
        }
    }
}

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format numbers with appropriate suffixes
 */
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

/**
 * Format time duration
 */
function formatDuration(seconds) {
    if (seconds < 1) {
        return `${(seconds * 1000).toFixed(0)}ms`;
    } else if (seconds < 60) {
        return `${seconds.toFixed(2)}s`;
    } else {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = (seconds % 60).toFixed(0);
        return `${minutes}m ${remainingSeconds}s`;
    }
}

/**
 * Check if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Local storage helpers
 */
const Storage = {
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('localStorage not available');
        }
    },
    
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('localStorage not available');
            return defaultValue;
        }
    },
    
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('localStorage not available');
        }
    }
};

/**
 * Theme management (if needed for future enhancements)
 */
const Theme = {
    toggle: function() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        Storage.set('theme', newTheme);
    },
    
    init: function() {
        const savedTheme = Storage.get('theme', 'dark');
        document.documentElement.setAttribute('data-bs-theme', savedTheme);
    }
};

// Initialize theme on load
Theme.init();

// Global utility functions for backward compatibility
window.updateCharCount = updateCharCount;
window.setExampleText = setExampleText;
window.copyToClipboard = copyToClipboard;
window.showNotification = showNotification;
window.scrollToElement = scrollToElement;
