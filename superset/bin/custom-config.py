FORWARDED_ALLOW_IPS = '*'
ENABLE_PROXY_FIX = True

####
from flask import flash, redirect, session, url_for, request, g, make_response, jsonify, abort
from werkzeug.security import generate_password_hash
from wtforms import validators, PasswordField
from wtforms.validators import EqualTo
from flask_babel import lazy_gettext

from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.forms import LoginForm_db, LoginForm_oid, ResetPasswordForm, UserInfoEdit
####

import logging, os

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from flask import Flask, redirect, url_for, g, flash, request, make_response, session as web_session
from flask_appbuilder.security.views import UserDBModelView,AuthDBView,AuthRemoteUserView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user

# Change Metadata DB if env variable is set
if os.get('SQLALCHEMY_METADATA_URI') is not None:
    SQLALCHEMY_DATABASE_URI = 'SQLALCHEMY_METADATA_URI'

class CustomAuthRemoteView(AuthRemoteUserView):

    @expose('/logout/')
    def logout(self):
        redirect_url = os.getenv('LOGOUT_REDIRECTURL','/')

        if g and g.user is not None and g.user.is_authenticated:
            logger.debug('g.user is not None -> %s (auth: %s)', g.user, g.user.is_authenticated)
            logout_user()
            return redirect(redirect_url)
            
        return redirect(redirect_url)

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):

        intent = request.args.get('next','')
        logger.debug('intent: %s', intent)
        if len(intent) > 0:
            redirect_url = intent
        else:
            redirect_url = "/" + self.appbuilder.get_url_for_index

        # Flushing flash message "Access is denied"
        if web_session and '_flashes' in web_session:
            web_session.pop('_flashes')
       
        if g and g.user is not None and g.user.is_authenticated:
            logger.debug('g.user: %s  (auth? %s)', g.user, g.user.is_authenticated)
            return redirect(redirect_url)

        sm = self.appbuilder.sm
        session = sm.get_session
		
        # Two headers are required: Shib-Identita-Matricola and Shib-Tipo-Risorsa (others may be present): 
  	#	All Possible Headers: "Shib-Identita-Matricola, Shib-Tipo-Risorsa, Shib-Identita-Nome, Shib-Identita-Cognome, socialMail, socialUniqueID"
        all_headers = os.getenv('SHIB_HEADERS','');
        headers = [x.strip() for x in all_headers.split(',')]
		
        if any([k not in request.headers
                for k in [headers[0], headers[1]] ]):
            # Here handle standard Superset login, if no Shibboleth headers are set
            logger.debug('There are no Shibboleth header: %s', url_for(self.appbuilder.sm.auth_view.__class__.__name__ + '.login'))
            logger.debug('form data: %s', request.form)

            login_template = 'appbuilder/general/security/login_ldap.html'
            form = LoginForm_db()
            if not request.form.get('username') and not request.form.get('password') :
                logger.debug('request.form has no data: %s | %s', request.form.get('username'), request.form.get('password'))
                return self.render_template(login_template, title='Sign in', form=form, appbuilder=self.appbuilder)
            else:
                logger.debug('request.form has some data: %s | %s', request.form.get('username'), request.form.get('password'))
                user = session.query(sm.user_model).filter_by(username=request.form.get('username')).first()
                if user and login_user(user) :
                    logger.debug('user \'%s\' has logged in', user)
                    return redirect(redirect_url)
                else:
                    logger.debug('user \'%s\' did not log in', user)
                    return self.render_template(login_template, title='Sign in', form=form, appbuilder=self.appbuilder)
            
        resource_id = request.headers.get(headers[0])
        resource_type = request.headers.get(headers[1]).lower()

        name = request.headers.get(headers[2])
        lastname = request.headers.get(headers[3])
        email = request.headers.get(headers[4])
        id = request.headers.get(headers[5])

        logger.debug('[Login] Username logging in: %s', resource_id)
        logger.debug('[Login] Resource Type: %s', resource_type)
        logger.debug('[Login] First Name, Last Name: %s, %s', name, lastname)
        logger.debug('[Login] Email: %s', email)
        logger.debug('[Login] Social Id: %s', id)

        user = session.query(sm.user_model).filter_by(username=resource_id).first()
		
        # Check if User is not active
        if user and not user.is_active:
            logger.debug('User and not user.is_active: %s', user, user.is_active)
            return ("Your account is not activated, ask an admin to check the 'Is Active?' box in your user profile")
				
        # Assign Superset role according to header
        role = sm.find_role(resource_type)
        logger.debug('Role found: %s', role)
		
        # Check the User
        if user is None and resource_id:
            user = sm.add_user(username=resource_id, first_name=name, last_name=lastname, email='{}.{}@csi.it'.format(name, lastname), role=role)

            user = sm.auth_user_remote_user(resource_id)
            logger.debug('User \'%s\' authenticated', user)
        
        elif role and  not any([ r in [sm.find_role('Admin'), role] for r in user.roles ]):
            logger.debug('Role %s is not in %s', role, user.roles)
            user = session.query(sm.user_model).get(user.id)
            user.roles += [role]
            session.commit()
        
        login_user(user)
        
        return redirect(redirect_url)


class CustomSecurityManager(SupersetSecurityManager):
    authremoteuserview = CustomAuthRemoteView

AUTH_TYPE = 3
CUSTOM_SECURITY_MANAGER = CustomSecurityManager
