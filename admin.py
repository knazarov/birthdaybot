from .model import User, Role
import flask_admin
import flask
import flask_security
from flask_admin.contrib.sqla import ModelView
import wtforms

class AuthenticatedModelView(ModelView):
    @flask_security.roles_required('admin')
    def is_accessible(self):
        return True

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return flask.redirect('/')


class UserAdmin(ModelView):
    column_exclude_list = list = ('password',)
    form_excluded_columns = ('password',)
    column_auto_select_related = True

    def is_accessible(self):
        return flask_security.current_user.has_role('admin')

    def scaffold_form(self):

        form_class = super(UserAdmin, self).scaffold_form()

        form_class.password2 = wtforms.fields.PasswordField('New Password')
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = flask_security.utils.encrypt_password(
                model.password2)


class AdminModelView(ModelView):
    def is_accessible(self):
        return flask_security.current_user.has_role('admin')


def init_admin(app, db):
    admin = flask_admin.Admin(app, name='hiring')

    admin.add_view(AdminModelView(Organization, db.session))
    admin.add_view(AdminModelView(Position, db.session))
    admin.add_view(AdminModelView(Candidate, db.session))
    admin.add_view(AdminModelView(Action, db.session))
    admin.add_view(AdminModelView(GoogleAuth, db.session))
    admin.add_view(AdminModelView(Invitation, db.session))
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(AdminModelView(Role, db.session))
    admin.add_view(AdminModelView(EmailSettings, db.session))
    admin.add_view(AdminModelView(Plan, db.session))
    admin.add_view(AdminModelView(PlanHistory, db.session))
