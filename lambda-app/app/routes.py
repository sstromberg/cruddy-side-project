"""
Flask routes for Employee Directory
Optimized for AWS Lambda deployment
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import get_employees, get_employee, create_employee, update_employee, delete_employee
from . import limiter
import json

main_bp = Blueprint('main', __name__)

# Available badges for the application
BADGES = {
    'apple': 'Mac User',
    'windows': 'Windows User',
    'linux': 'Linux User',
    'video-camera': 'Digital Content Star',
    'trophy': 'Employee of the Month',
    'camera': 'Photographer',
    'plane': 'Frequent Flier',
    'paperclip': 'Paperclip Afficionado',
    'coffee': 'Coffee Snob',
    'gamepad': 'Gamer',
    'bug': 'Bugfixer',
    'umbrella': 'Seattle Fan'
}

@main_bp.route('/')
def home():
    """Home page with employee list"""
    try:
        employees = get_employees()
        return render_template('main.html', employees=employees, badges=BADGES)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'error')
        return render_template('main.html', employees=[], badges=BADGES)

@main_bp.route('/add', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def add():
    """Add new employee"""
    if request.method == 'POST':
        try:
            # Get form data
            employee_data = {
                'fullname': request.form.get('fullname', '').strip(),
                'location': request.form.get('location', '').strip(),
                'job_title': request.form.get('job_title', '').strip(),
                'badges': request.form.get('badges', '').split(',') if request.form.get('badges') else []
            }
            
            # Validate required fields
            if not employee_data['fullname'] or not employee_data['location'] or not employee_data['job_title']:
                flash('All fields are required', 'error')
                return render_template('add-edit.html', employee=None, title='Add Employee', badges=BADGES)
            
            # Clean up badges
            employee_data['badges'] = [badge.strip() for badge in employee_data['badges'] if badge.strip()]
            
            # Create employee
            result = create_employee(employee_data)
            if result:
                flash('Employee added successfully!', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Error adding employee', 'error')
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'error')
    
    return render_template('add-edit.html', employee=None, title='Add Employee', badges=BADGES)

@main_bp.route('/view/<employee_id>')
def view(employee_id):
    """View employee details"""
    try:
        employee = get_employee(employee_id)
        if employee:
            return render_template('view-edit.html', employee=employee, badges=BADGES)
        else:
            flash('Employee not found', 'error')
            return redirect(url_for('main.home'))
    except Exception as e:
        flash(f'Error viewing employee: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@main_bp.route('/edit/<employee_id>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def edit(employee_id):
    """Edit existing employee"""
    try:
        employee = get_employee(employee_id)
        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('main.home'))
        
        if request.method == 'POST':
            # Get form data
            employee_data = {
                'fullname': request.form.get('fullname', '').strip(),
                'location': request.form.get('location', '').strip(),
                'job_title': request.form.get('job_title', '').strip(),
                'badges': request.form.get('badges', '').split(',') if request.form.get('badges') else []
            }
            
            # Validate required fields
            if not employee_data['fullname'] or not employee_data['location'] or not employee_data['job_title']:
                flash('All fields are required', 'error')
                return render_template('add-edit.html', employee=employee, title='Edit Employee', badges=BADGES)
            
            # Clean up badges
            employee_data['badges'] = [badge.strip() for badge in employee_data['badges'] if badge.strip()]
            
            # Update employee
            result = update_employee(employee_id, employee_data)
            if result:
                flash('Employee updated successfully!', 'success')
                return redirect(url_for('main.view', employee_id=employee_id))
            else:
                flash('Error updating employee', 'error')
        
        return render_template('add-edit.html', employee=employee, title='Edit Employee', badges=BADGES)
        
    except Exception as e:
        flash(f'Error editing employee: {str(e)}', 'error')
        return redirect(url_for('main.home'))

@main_bp.route('/delete/<employee_id>', methods=['POST'])
@limiter.limit("5 per minute")
def delete(employee_id):
    """Delete employee"""
    try:
        result = delete_employee(employee_id)
        if result:
            flash('Employee deleted successfully!', 'success')
        else:
            flash('Error deleting employee', 'error')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('main.home'))

# API endpoints for future use
@main_bp.route('/api/employees')
@limiter.limit("100 per hour")
def api_employees():
    """API endpoint to get all employees"""
    try:
        employees = get_employees()
        return jsonify({
            'success': True,
            'data': employees,
            'total': len(employees)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/employees/<employee_id>')
@limiter.limit("100 per hour")
def api_employee(employee_id):
    """API endpoint to get specific employee"""
    try:
        employee = get_employee(employee_id)
        if employee:
            return jsonify({
                'success': True,
                'data': employee
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Employee not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
