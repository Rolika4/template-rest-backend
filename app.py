"""Flask API application for managing records."""
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from config import Config

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for frontend integration


# Data model
class Record(db.Model):
    """Database model for records."""

    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text, nullable=True)
    # Use timezone-aware datetimes (UTC)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """Convert object to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'message': self.message,
            'note': self.note,
            'created_at': (self.created_at.isoformat()
                           if self.created_at else None),
            'updated_at': (self.updated_at.isoformat()
                           if self.updated_at else None)
        }

    def update_from_dict(self, data):
        """Update record fields from dictionary."""
        if 'name' in data and data['name'].strip():
            self.name = data['name'].strip()
        if 'message' in data and data['message'].strip():
            self.message = data['message'].strip()
        if 'note' in data:
            self.note = data['note'].strip() if data['note'] else None
        # set updated_at to timezone-aware UTC now
        self.updated_at = datetime.now(timezone.utc)


# API endpoints

@app.route('/')
def health_check():
    """Check API health status."""
    return jsonify({
        'status': 'OK',
        'message': 'Flask API is running',
        'timestamp': datetime.now(timezone.utc).isoformat()
    })


@app.route('/api/records/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """Update record by ID."""
    try:
        record = Record.query.get_or_404(record_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update record using the new method
        record.update_from_dict(data)

        db.session.commit()

        return jsonify({
            'message': 'Record updated successfully',
            'record': record.to_dict()
        }), 200

    except (SQLAlchemyError, ValueError) as database_error:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to update record: {str(database_error)}'
        }), 500


@app.route('/api/records/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """Delete record by ID."""
    try:
        record = Record.query.get_or_404(record_id)
        db.session.delete(record)
        db.session.commit()

        return jsonify({'message': 'Record deleted successfully'}), 200

    except SQLAlchemyError as database_error:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to delete record: {str(database_error)}'
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(_error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(_error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


# Create database tables
def create_tables():
    """Create database tables."""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    except SQLAlchemyError as database_error:
        print(f"Error creating database tables: {database_error}")


if __name__ == '__main__':
    # Create tables on startup
    create_tables()

    # Run Flask application
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
