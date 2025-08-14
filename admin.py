from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth import login_required, admin_required
from models import Topic, Question, User, QuestionAssignment
from app import db
from openai_service import generate_question_variations
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    topics = Topic.query.all()
    total_questions = Question.query.count()
    total_students = User.query.filter_by(role='student').count()
    total_assignments = QuestionAssignment.query.count()
    
    return render_template('admin/dashboard.html', 
                         topics=topics,
                         total_questions=total_questions,
                         total_students=total_students,
                         total_assignments=total_assignments)

@admin_bp.route('/create_topic', methods=['GET', 'POST'])
@login_required
@admin_required
def create_topic():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        difficulty = request.form['difficulty']
        category = request.form['category']
        
        topic = Topic(
            name=name,
            description=description,
            difficulty=difficulty,
            category=category,
            created_by=session['user_id']
        )
        
        db.session.add(topic)
        db.session.commit()
        
        flash('Topic created successfully! Now generate AI questions for this topic.', 'success')
        return redirect(url_for('admin.generate_questions', topic_id=topic.id))
    
    return render_template('admin/create_topic.html')

@admin_bp.route('/generate_questions/<int:topic_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_questions(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    
    if request.method == 'POST':
        num_variations = int(request.form['num_variations'])
        base_question = request.form['base_question']
        
        try:
            logging.info(f"Starting question generation for topic {topic.id}: {topic.name}")
            
            # Generate question variations using OpenAI
            variations = generate_question_variations(
                base_question=base_question,
                topic_name=topic.name,
                difficulty=topic.difficulty,
                category=topic.category,
                num_variations=num_variations
            )
            
            logging.info(f"Successfully generated {len(variations)} variations from AI")
            
            # Save generated questions to database
            questions_added = 0
            for i, variation in enumerate(variations):
                try:
                    question = Question(
                        topic_id=topic.id,
                        question_text=variation['question'],
                        expected_answer=variation.get('expected_answer', ''),
                        difficulty=topic.difficulty,
                        variation_number=i + 1
                    )
                    db.session.add(question)
                    questions_added += 1
                    logging.debug(f"Added question {i+1}: {variation['question'][:50]}...")
                except Exception as q_error:
                    logging.error(f"Error adding question {i+1}: {q_error}")
                    continue
            
            # Commit all questions at once
            db.session.commit()
            logging.info(f"Successfully committed {questions_added} questions to database")
            
            flash(f'🎉 Successfully generated {questions_added} question variations! Total questions for this topic: {Question.query.filter_by(topic_id=topic.id).count()}', 'success')
            return redirect(url_for('admin.view_questions', topic_id=topic.id))
            
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error generating questions: {e}")
            logging.error(f"Exception type: {type(e).__name__}")
            import traceback
            logging.error(f"Traceback: {traceback.format_exc()}")
            flash(f'Error generating questions: {str(e)}', 'error')
    
    return render_template('admin/generate_questions.html', topic=topic)

@admin_bp.route('/view_questions/<int:topic_id>')
@login_required
@admin_required
def view_questions(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    questions = Question.query.filter_by(topic_id=topic_id).all()
    
    return render_template('admin/view_questions.html', topic=topic, questions=questions)

@admin_bp.route('/delete_topic/<int:topic_id>')
@login_required
@admin_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    
    # Delete all related questions and assignments
    Question.query.filter_by(topic_id=topic_id).delete()
    QuestionAssignment.query.filter_by(topic_id=topic_id).delete()
    
    db.session.delete(topic)
    db.session.commit()
    
    flash('Topic and all related questions deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/view_assignments')
@login_required
@admin_required
def view_assignments():
    assignments = db.session.query(QuestionAssignment, User, Topic, Question).join(
        User, QuestionAssignment.user_id == User.id
    ).join(
        Topic, QuestionAssignment.topic_id == Topic.id
    ).join(
        Question, QuestionAssignment.question_id == Question.id
    ).all()
    
    return render_template('admin/view_assignments.html', assignments=assignments)
