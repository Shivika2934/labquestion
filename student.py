from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required
from models import Topic, Question, User, QuestionAssignment
from app import db
import random
import logging

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if session.get('role') != 'student':
        flash('Student access required', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Get all available topics
    topics = Topic.query.all()
    
    # Get user's assignments
    assignments = db.session.query(QuestionAssignment, Topic, Question).join(
        Topic, QuestionAssignment.topic_id == Topic.id
    ).join(
        Question, QuestionAssignment.question_id == Question.id
    ).filter(QuestionAssignment.user_id == user_id).all()
    
    return render_template('student/dashboard.html', topics=topics, assignments=assignments)

@student_bp.route('/get_question/<int:topic_id>')
@login_required
def get_question(topic_id):
    if session.get('role') != 'student':
        flash('Student access required', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    topic = Topic.query.get_or_404(topic_id)
    
    # Check if user already has an assignment for this topic
    existing_assignment = QuestionAssignment.query.filter_by(
        user_id=user_id, 
        topic_id=topic_id
    ).first()
    
    if existing_assignment:
        return redirect(url_for('student.view_question', assignment_id=existing_assignment.id))
    
    # Get all unassigned questions for this topic
    unassigned_questions = Question.query.filter_by(
        topic_id=topic_id, 
        is_assigned=False
    ).all()
    
    if not unassigned_questions:
        flash('No available questions for this topic. Please contact your administrator.', 'error')
        return redirect(url_for('student.dashboard'))
    
    # Randomly assign a question to ensure fairness
    selected_question = random.choice(unassigned_questions)
    
    # Create assignment
    assignment = QuestionAssignment(
        user_id=user_id,
        question_id=selected_question.id,
        topic_id=topic_id
    )
    
    # Mark question as assigned
    selected_question.is_assigned = True
    
    db.session.add(assignment)
    db.session.commit()
    
    logging.info(f"Assigned question {selected_question.id} to user {user_id} for topic {topic_id}")
    
    return redirect(url_for('student.view_question', assignment_id=assignment.id))

@student_bp.route('/question/<int:assignment_id>')
@login_required
def view_question(assignment_id):
    if session.get('role') != 'student':
        flash('Student access required', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    # Get assignment details
    assignment_data = db.session.query(QuestionAssignment, Topic, Question).join(
        Topic, QuestionAssignment.topic_id == Topic.id
    ).join(
        Question, QuestionAssignment.question_id == Question.id
    ).filter(
        QuestionAssignment.id == assignment_id,
        QuestionAssignment.user_id == user_id
    ).first()
    
    if not assignment_data:
        flash('Assignment not found or access denied', 'error')
        return redirect(url_for('student.dashboard'))
    
    assignment, topic, question = assignment_data
    
    return render_template('student/question.html', 
                         assignment=assignment, 
                         topic=topic, 
                         question=question)

@student_bp.route('/complete_question/<int:assignment_id>', methods=['POST'])
@login_required
def complete_question(assignment_id):
    if session.get('role') != 'student':
        flash('Student access required', 'error')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    assignment = QuestionAssignment.query.filter_by(
        id=assignment_id, 
        user_id=user_id
    ).first()
    
    if not assignment:
        flash('Assignment not found or access denied', 'error')
        return redirect(url_for('student.dashboard'))
    
    assignment.completed = True
    db.session.commit()
    
    flash('Question marked as completed!', 'success')
    return redirect(url_for('student.dashboard'))
