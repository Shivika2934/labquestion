# AI Lab Question Generator

## Overview

An educational platform that uses AI to generate unique lab questions for students. The system allows administrators to create topics and generate question variations using OpenAI's API, while students receive personalized assignments. Built with Flask and designed for academic institutions to ensure each student gets a unique but equivalent question for fair assessment.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask-based web application** with Blueprint architecture for modular organization
- **SQLAlchemy ORM** with SQLite database (configurable to PostgreSQL via DATABASE_URL)
- **Session-based authentication** with role-based access control (admin/student)
- **Werkzeug password hashing** for secure credential storage

### Database Design
- **User management**: Stores usernames, emails, password hashes, and roles
- **Topic hierarchy**: Categories, difficulty levels, and descriptions for lab subjects
- **Question variations**: AI-generated questions linked to topics with variation tracking
- **Assignment system**: One-to-one mapping between users and topics with completion status
- **Unique constraints**: Prevents duplicate assignments per user-topic combination

### AI Integration
- **OpenAI GPT-4o integration** for generating question variations
- **Prompt engineering**: Structured prompts ensure equivalent difficulty and learning objectives
- **JSON response parsing**: Extracts generated questions and expected answers
- **Variation tracking**: Numbers each generated question for administrative oversight

### Authentication & Authorization
- **Role-based access control**: Separate interfaces for admins and students
- **Session management**: Flask sessions store user identity and permissions
- **Route protection**: Decorators enforce login and admin requirements
- **Default admin creation**: Automatic setup of initial administrator account

### User Interface
- **Bootstrap 5 with Replit dark theme** for consistent styling
- **Responsive design**: Mobile-friendly interface with Bootstrap grid system
- **Template inheritance**: Base template with navigation and flash messaging
- **Role-specific dashboards**: Different interfaces for administrators and students

### Question Assignment Logic
- **Intelligent distribution**: Ensures students get unassigned questions when available
- **Random selection**: Falls back to random assignment when all questions are used
- **One question per topic**: Students can only have one active assignment per topic
- **Completion tracking**: Marks assignments as completed for progress monitoring

## External Dependencies

### Required Services
- **OpenAI API**: GPT-4o model for generating question variations (requires OPENAI_API_KEY)
- **Database**: SQLite by default, PostgreSQL support via DATABASE_URL environment variable

### Python Packages
- **Flask**: Web framework and session management
- **Flask-SQLAlchemy**: Database ORM and migration support
- **OpenAI**: Official Python client for GPT API integration
- **Werkzeug**: Password hashing and security utilities

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with Replit dark theme variant
- **Bootstrap Icons**: Icon library for UI elements
- **CDN delivery**: All frontend assets loaded from external CDNs

### Environment Configuration
- **SESSION_SECRET**: Flask session encryption key
- **DATABASE_URL**: Optional PostgreSQL connection string
- **OPENAI_API_KEY**: Required for AI question generation functionality