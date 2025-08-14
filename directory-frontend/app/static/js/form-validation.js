/**
 * Enhanced Form Validation System for Corporate Directory
 * Provides real-time validation, character counters, and enhanced user feedback
 */

class FormValidator {
    constructor(formId, options = {}) {
        this.form = document.getElementById(formId);
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            showCharacterCounters: true,
            showRealTimeFeedback: true,
            debounceDelay: 300,
            ...options
        };
        
        this.validationRules = {
            fullname: {
                required: true,
                minLength: 2,
                maxLength: 100,
                pattern: /^[a-zA-Z\s\-\'\.]+$/,
                messages: {
                    required: "Full name is required",
                    minLength: "Full name must be at least 2 characters",
                    maxLength: "Full name cannot exceed 100 characters",
                    pattern: "Full name can only contain letters, spaces, hyphens, apostrophes, and periods"
                }
            },
            location: {
                required: true,
                minLength: 2,
                maxLength: 100,
                pattern: /^[a-zA-Z0-9\s\-\'\.\,]+$/,
                messages: {
                    required: "Location is required",
                    minLength: "Location must be at least 2 characters",
                    maxLength: "Location cannot exceed 100 characters",
                    pattern: "Location can only contain letters, numbers, spaces, hyphens, apostrophes, periods, and commas"
                }
            },
            job_title: {
                required: true,
                minLength: 2,
                maxLength: 100,
                pattern: /^[a-zA-Z\s\-\'\.\,\&]+$/,
                messages: {
                    required: "Job title is required",
                    minLength: "Job title must be at least 2 characters",
                    maxLength: "Job title cannot exceed 100 characters",
                    pattern: "Job title can only contain letters, spaces, hyphens, apostrophes, periods, commas, and ampersands"
                }
            }
        };
        
        this.debounceTimers = {};
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        this.setupFormFields();
        this.setupEventListeners();
        this.setupCharacterCounters();
        this.setupRealTimeValidation();
    }
    
    setupFormFields() {
        // Add validation classes and feedback elements
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.setupField(field, fieldName);
            }
        });
    }
    
    setupField(field, fieldName) {
        const fieldGroup = field.closest('.row');
        if (fieldGroup) {
            fieldGroup.classList.add('form-field-group');
            
            // Add status indicator
            const statusIndicator = document.createElement('div');
            statusIndicator.className = 'field-status';
            statusIndicator.innerHTML = '<div class="status-icon pending">?</div>';
            fieldGroup.appendChild(statusIndicator);
            
            // Add validation feedback
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.id = `${fieldName}-feedback`;
            fieldGroup.appendChild(feedback);
            
            // Add character counter if enabled
            if (this.options.showCharacterCounters) {
                const counter = document.createElement('div');
                counter.className = 'char-counter';
                counter.id = `${fieldName}-counter`;
                counter.textContent = `0 / ${this.validationRules[fieldName].maxLength}`;
                fieldGroup.appendChild(counter);
            }
        }
    }
    
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Field validation events
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                if (this.options.validateOnInput) {
                    field.addEventListener('input', (e) => this.debounceValidation(e.target, fieldName));
                }
                if (this.options.validateOnBlur) {
                    field.addEventListener('blur', (e) => this.validateField(e.target, fieldName));
                }
                field.addEventListener('focus', (e) => this.handleFieldFocus(e.target, fieldName));
            }
        });
    }
    
    setupCharacterCounters() {
        if (!this.options.showCharacterCounters) return;
        
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            const counter = document.getElementById(`${fieldName}-counter`);
            
            if (field && counter) {
                field.addEventListener('input', () => {
                    this.updateCharacterCounter(field, counter, fieldName);
                });
            }
        });
    }
    
    setupRealTimeValidation() {
        if (!this.options.showRealTimeFeedback) return;
        
        // Add validation summary
        const summary = document.createElement('div');
        summary.className = 'validation-summary';
        summary.id = 'validation-summary';
        summary.style.display = 'none';
        summary.innerHTML = `
            <h6><i class="fa fa-exclamation-triangle"></i> Please fix the following errors:</h6>
            <ul id="validation-errors"></ul>
        `;
        
        this.form.insertBefore(summary, this.form.firstChild);
    }
    
    debounceValidation(field, fieldName) {
        clearTimeout(this.debounceTimers[fieldName]);
        this.debounceTimers[fieldName] = setTimeout(() => {
            this.validateField(field, fieldName);
        }, this.options.debounceDelay);
    }
    
    validateField(field, fieldName) {
        const rules = this.validationRules[fieldName];
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Required validation
        if (rules.required && !value) {
            isValid = false;
            errorMessage = rules.messages.required;
        }
        // Length validation
        else if (value) {
            if (value.length < rules.minLength) {
                isValid = false;
                errorMessage = rules.messages.minLength;
            } else if (value.length > rules.maxLength) {
                isValid = false;
                errorMessage = rules.messages.maxLength;
            }
            // Pattern validation
            else if (rules.pattern && !rules.pattern.test(value)) {
                isValid = false;
                errorMessage = rules.messages.pattern;
            }
        }
        
        this.updateFieldValidation(field, fieldName, isValid, errorMessage);
        return isValid;
    }
    
    updateFieldValidation(field, fieldName, isValid, errorMessage = '') {
        const fieldGroup = field.closest('.form-field-group');
        const statusIcon = fieldGroup.querySelector('.status-icon');
        const feedback = document.getElementById(`${fieldName}-feedback`);
        
        // Update field classes
        field.classList.remove('is-valid', 'is-invalid');
        field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        
        // Update status icon
        if (statusIcon) {
            statusIcon.className = `status-icon ${isValid ? 'valid' : 'invalid'}`;
            statusIcon.innerHTML = isValid ? '✓' : '✗';
        }
        
        // Update feedback message
        if (feedback) {
            feedback.textContent = errorMessage;
            feedback.style.display = errorMessage ? 'block' : 'none';
        }
        
        // Update character counter colors
        this.updateCharacterCounterColors(field, fieldName);
    }
    
    updateCharacterCounter(field, counter, fieldName) {
        const currentLength = field.value.length;
        const maxLength = this.validationRules[fieldName].maxLength;
        const percentage = (currentLength / maxLength) * 100;
        
        counter.textContent = `${currentLength} / ${maxLength}`;
        counter.className = 'char-counter';
        
        if (percentage >= 90) {
            counter.classList.add('at-limit');
        } else if (percentage >= 75) {
            counter.classList.add('near-limit');
        }
    }
    
    updateCharacterCounterColors(field, fieldName) {
        const counter = document.getElementById(`${fieldName}-counter`);
        if (counter) {
            const currentLength = field.value.length;
            const maxLength = this.validationRules[fieldName].maxLength;
            const percentage = (currentLength / maxLength) * 100;
            
            counter.className = 'char-counter';
            if (percentage >= 90) {
                counter.classList.add('at-limit');
            } else if (percentage >= 75) {
                counter.classList.add('near-limit');
            }
        }
    }
    
    handleFieldFocus(field, fieldName) {
        // Remove validation classes on focus for better UX
        field.classList.remove('is-valid', 'is-invalid');
        
        const fieldGroup = field.closest('.form-field-group');
        const statusIcon = fieldGroup.querySelector('.status-icon');
        if (statusIcon) {
            statusIcon.className = 'status-icon pending';
            statusIcon.innerHTML = '?';
        }
    }
    
    validateAllFields() {
        let isValid = true;
        const errors = [];
        
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field && !this.validateField(field, fieldName)) {
                isValid = false;
                const rules = this.validationRules[fieldName];
                const value = field.value.trim();
                
                if (!value && rules.required) {
                    errors.push(rules.messages.required);
                } else if (value.length < rules.minLength) {
                    errors.push(rules.messages.minLength);
                } else if (value.length > rules.maxLength) {
                    errors.push(rules.messages.maxLength);
                } else if (rules.pattern && !rules.pattern.test(value)) {
                    errors.push(rules.messages.pattern);
                }
            }
        });
        
        this.updateValidationSummary(errors);
        return isValid;
    }
    
    updateValidationSummary(errors) {
        const summary = document.getElementById('validation-summary');
        const errorsList = document.getElementById('validation-errors');
        
        if (summary && errorsList) {
            if (errors.length > 0) {
                errorsList.innerHTML = errors.map(error => `<li>${error}</li>`).join('');
                summary.style.display = 'block';
                summary.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                summary.style.display = 'none';
            }
        }
    }
    
    handleSubmit(e) {
        if (!this.validateAllFields()) {
            e.preventDefault();
            this.showValidationErrors();
            return false;
        }
        
        // Show loading state
        this.showFormLoading();
        return true;
    }
    
    showValidationErrors() {
        // Focus on first invalid field
        const firstInvalidField = this.form.querySelector('.is-invalid');
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    showFormLoading() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn && window.LoadingManager) {
            window.LoadingManager.showButtonLoading(submitBtn);
        }
    }
    
    // Public methods for external use
    resetValidation() {
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.remove('is-valid', 'is-invalid');
                const fieldGroup = field.closest('.form-field-group');
                const statusIcon = fieldGroup.querySelector('.status-icon');
                if (statusIcon) {
                    statusIcon.className = 'status-icon pending';
                    statusIcon.innerHTML = '?';
                }
            }
        });
        
        const summary = document.getElementById('validation-summary');
        if (summary) {
            summary.style.display = 'none';
        }
    }
    
    getValidationState() {
        const state = {};
        Object.keys(this.validationRules).forEach(fieldName => {
            const field = this.form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                state[fieldName] = {
                    isValid: field.classList.contains('is-valid'),
                    isInvalid: field.classList.contains('is-invalid'),
                    value: field.value,
                    errors: this.getFieldErrors(field, fieldName)
                };
            }
        });
        return state;
    }
    
    getFieldErrors(field, fieldName) {
        const rules = this.validationRules[fieldName];
        const value = field.value.trim();
        const errors = [];
        
        if (rules.required && !value) {
            errors.push(rules.messages.required);
        }
        if (value) {
            if (value.length < rules.minLength) {
                errors.push(rules.messages.minLength);
            }
            if (value.length > rules.maxLength) {
                errors.push(rules.messages.maxLength);
            }
            if (rules.pattern && !rules.pattern.test(value)) {
                errors.push(rules.messages.pattern);
            }
        }
        
        return errors;
    }
}

// Utility functions
const FormValidationUtils = {
    // Sanitize input
    sanitizeInput(input) {
        return input.replace(/[<>]/g, '');
    },
    
    // Format validation message
    formatMessage(message, fieldName) {
        return message.replace('{field}', fieldName.charAt(0).toUpperCase() + fieldName.slice(1));
    },
    
    // Check if field is empty
    isEmpty(value) {
        return !value || value.trim().length === 0;
    },
    
    // Validate email format
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },
    
    // Validate phone format
    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }
};

// Auto-initialize validation for forms with data-validation attribute
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form[data-validation]');
    forms.forEach(form => {
        const formId = form.id || `form-${Math.random().toString(36).substr(2, 9)}`;
        form.id = formId;
        
        const options = JSON.parse(form.dataset.validation || '{}');
        new FormValidator(formId, options);
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FormValidator, FormValidationUtils };
}
