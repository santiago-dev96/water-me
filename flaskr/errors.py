from flask import render_template


def setup_error_handlers(app):
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Internal server error: {error}")
        return render_template("errors/internal_server_error.html"), 500
