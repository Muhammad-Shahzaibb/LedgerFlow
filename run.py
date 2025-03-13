from Project import app, db  # Ensure db is imported from your project
from flask_migrate import Migrate

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Run the Flask app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
