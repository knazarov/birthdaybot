from model import User, Role, Birthday, Payment, Deposit
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
        app = flask.current_app
        return flask_security.current_user.id == int(app.config['ADMIN_ID'])

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
        app = flask.current_app
        return flask_security.current_user.id == int(app.config['ADMIN_ID'])


def init_admin(app, db):
    admin = flask_admin.Admin(app, name='birthday')

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(AdminModelView(Role, db.session))
    admin.add_view(AdminModelView(Birthday, db.session))
    admin.add_view(AdminModelView(Payment, db.session))
    admin.add_view(AdminModelView(Deposit, db.session))
