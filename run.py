# from Project import app, db  # Ensure db is imported from your project
# from flask_migrate import Migrate

# # Initialize Flask-Migrate
# migrate = Migrate(app, db)

# # Run the Flask app
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5000, debug=True)


# for render
import os
from Project import app, db
from flask_migrate import Migrate

migrate = Migrate(app, db)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use Render's PORT variable
    app.run(host="0.0.0.0", port=port, debug=True)
