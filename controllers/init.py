from .auth import auth_bp
from .admin_controllers.admin import admin_bp
from .user_controllers.user import user_bp


from .admin_controllers.admin_managing import adminManaging_bp
from .admin_controllers.admin_subject import adminManagingSub_bp
from .admin_controllers.admin_chapter import adminManagingChapter_bp
from .admin_controllers.admin_quiz import adminManagingQuiz_bp
from .admin_controllers.admin_questions import adminManagingQuestions_bp

from .user_controllers.user_dashboard import userDashboard_bp
from .user_controllers.user_profile import userProfile_bp
from .user_controllers.user_subjects import userSubjects_bp
from .user_controllers.user_chapters import userChap_bp
from .user_controllers.user_quiz import userQuiz_bp




def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(adminManaging_bp)
    app.register_blueprint(adminManagingSub_bp)
    app.register_blueprint(adminManagingChapter_bp)
    app.register_blueprint(adminManagingQuiz_bp)
    app.register_blueprint(adminManagingQuestions_bp)

    app.register_blueprint(userDashboard_bp)
    app.register_blueprint(userProfile_bp)
    app.register_blueprint(userSubjects_bp)
    app.register_blueprint(userChap_bp)
    app.register_blueprint(userQuiz_bp)
