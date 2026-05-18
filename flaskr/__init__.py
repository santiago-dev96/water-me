import os

from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_prefixed_env()
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'app_db.sqlite'),
        IMAGES=os.path.join(app.instance_path, 'images'),
        MAX_CONTENT_LENGTH = 3 * 1000 * 1000 # 3 MB limit for file uploads
    )

    if test_config is not None:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists. It usually is located at the project root.
    os.makedirs(app.instance_path, exist_ok=True)
    # and the image uploads dir
    os.makedirs(os.path.join(app.instance_path, app.config['IMAGES']), exist_ok=True)

    from . import db
    db.init_app(app)

    from . import errors
    errors.setup_error_handlers(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import plants
    app.register_blueprint(plants.bp)

    return app

