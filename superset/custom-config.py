
FORWARDED_ALLOW_IPS = '*'
ENABLE_PROXY_FIX = True
#PREFERRED_URL_SCHEME = 'https'

####
from flask import flash, redirect, session, url_for, request, g, make_response, jsonify, abort
from werkzeug.security import generate_password_hash
from wtforms import validators, PasswordField
from wtforms.validators import EqualTo
from flask_babel import lazy_gettext

from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.forms import LoginForm_db, LoginForm_oid, ResetPasswordForm, UserInfoEdit
####

import logging

# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from flask import Flask, redirect, url_for, g, flash, request, make_response, session as web_session
from flask_appbuilder.security.views import UserDBModelView,AuthDBView,AuthRemoteUserView
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.views import expose
from flask_appbuilder.security.manager import BaseSecurityManager
from flask_login import login_user, logout_user

class CustomAuthRemoteView(AuthRemoteUserView):

    @expose('/odata/<dataset_code>', methods=['GET'])
    def download_csv(self, dataset_code):
        
        import requests, json, re, os

		if os.environ.get('CLIENTID') and os.environ.get('CLIENTSECRET'):
            m = re.search('(.[a-z_]*)_(.[0-9]*)', dataset_code)
            datasetCode = m.group(1)
            datasetId = m.group(2)
    
            client_id = dict()
            client_secret = dict()

            token_url = "https://api.smartdatanet.it/api/token"

            base_url = 'https://api.smartdatanet.it/api/'
            api_url = base_url + dataset_code +'/download/' + datasetId + '/all'

            logger.debug('URL for downloading CSV: %s', api_url)

            #client (application) credentials
            client_id['dipendente'] = os.environ.get('CLIENTID')
            client_secret['dipendente'] = os.environ.get('CLIENTSECRET')

            # Recupera utente loggato e suo ruolo
            logger.debug('Downloading as user: %s', g.user)
              
            sm = self.appbuilder.sm     
            if any([ r in [sm.find_role('Admin'), sm.find_role('csi_piemonte')] for r in g.user.roles ]):
                ruolo = 'dipendente'
            else:
                ruolo = 'non dipendente'
                return redirect('/')

            logger.debug('Ruolo: Admin/%s', ruolo) 

            #step A, B - single call with client credentials as the basic auth header - will return access_token			
            data = {'grant_type': 'client_credentials'}
            access_token_response = requests.post(token_url, data=data, verify=False, allow_redirects=False, auth=(client_id[ruolo], client_secret[ruolo]))
            tokens = json.loads(access_token_response.text)

            logger.debug('Access token in use: ' + tokens['access_token'])

            #step B - with the returned access_token we can make as many calls as we want
            api_call_headers = {'Authorization': 'Bearer ' + tokens['access_token']}
            api_call_response = requests.get(api_url, headers=api_call_headers, verify=False)

            csv = api_call_response.content

            response = make_response(csv)
            cd = 'attachment; filename=export.csv'
            response.headers['Content-Disposition'] = cd
            response.mimetype='text/csv'

            return response
        else:
            logger.debug('No CLIENTID and CLIENTSECRET provided')

    @expose('/logout/')
    def logout(self):
        redirect_url = "https://intranet.csi.it/csis_liv1_icsi/Shibboleth.sso/Logout"

        if g and g.user is not None and g.user.is_authenticated:
            logger.debug('g.user is not None -> %s (auth: %s)', g.user, g.user.is_authenticated)
            logout_user()
            return redirect(redirect_url)
            
        return redirect(redirect_url)

    @expose('/login/', methods=['GET', 'POST'])
    def login(self):

        ruolo_dipendente = 'csi_piemonte'
        ruolo_consulente = 'csi_piemonte_consulente'

        redirect_url = "/csi_sii" + self.appbuilder.get_url_for_index

        # Flushing flash message "Access is denied"
        if web_session and '_flashes' in web_session:
            web_session.pop('_flashes')
       
        if g and g.user is not None and g.user.is_authenticated:
            logger.debug('g.user: %s  (auth? %s)', g.user, g.user.is_authenticated)
            return redirect(redirect_url)

        sm = self.appbuilder.sm
        session = sm.get_session
		
        # Two headers are required: Shib-Identita-Matricola and Shib-Tipo-Risorsa
        if any([
                k not in request.headers
                for k in ['Shib-Identita-Matricola', 'Shib-Tipo-Risorsa']]):
            # Here handle standard Superset login, if no Shibboleth headers are set
            logger.debug('Header Shibboleth non presenti: %s', url_for(self.appbuilder.sm.auth_view.__class__.__name__ + '.login'))
            logger.debug('form data: %s', request.form)

            login_template = 'appbuilder/general/security/login_ldap.html'
            form = LoginForm_db()
            if not request.form.get('username') and not request.form.get('password') :
                logger.debug('request.form has no data: %s | %s', request.form.get('username'), request.form.get('password'))
                return self.render_template(login_template,
                               title='Sign in',
                               form=form,
                               appbuilder=self.appbuilder)
            else:
                logger.debug('request.form has data: %s | %s', request.form.get('username'), request.form.get('password'))
                user = session.query(sm.user_model).filter_by(username=request.form.get('username')).first()
                if user and login_user(user) :
                    logger.debug('user \'%s\' has logged in', user)
                    return redirect("/superset/welcome")
                else:
                    logger.debug('user \'%s\' did not log in', user)
                    return self.render_template(login_template,
                               title='Sign in',
                               form=form,
                               appbuilder=self.appbuilder)
            
        matricola = request.headers.get('Shib-Identita-Matricola')
        risorsa = request.headers.get('Shib-Tipo-Risorsa').lower()

        nome = request.headers.get('Shib-Identita-Nome')
        cognome = request.headers.get('Shib-Identita-Cognome')
        #email = request.headers.get('socialMail')
        #id = request.headers.get('socialUniqueID')

        logger.debug('[Login] Username logging in: %s', matricola)
        logger.debug('[Login] Resource Type: %s', risorsa)
        logger.debug('[Login] Nome, Cognome: %s, %s', nome, cognome)
        #logger.debug('[Login] Email: %s', email)
        #logger.debug('[Login] Id: %s', id)

        user = session.query(sm.user_model).filter_by(username=matricola).first()
		
        # Check if User is not active
        if user and not user.is_active:
            logger.debug('User and not user.is_active: %s', user, user.is_active)
            return (
                "Your account is not activated, "
                "ask an admin to check the 'Is Active?' box in your "
                "user profile")
				
        # Assign Superset role according to header
        role = sm.find_role(risorsa)
        logger.debug('Ruolo individuato: %s', role)
		
        # Check the User
        if user is None and matricola:
            user = sm.add_user(
                username=matricola,
                first_name=nome,
                last_name=cognome,
                email='{}.{}@csi.it'.format(nome, cognome),
                role=role)

            user = sm.auth_user_remote_user(matricola)
            logger.debug('User \'%s\' autenticato', user)
        
        elif role and  not any([ r in [sm.find_role('Admin'), role] for r in user.roles ]):
            logger.debug('role %s is not in %s', role, user.roles)
            user = session.query(sm.user_model).get(user.id)
            user.roles += [role]
            session.commit()
        
        login_user(user)
        
        return redirect(redirect_url)


class CustomSecurityManager(SupersetSecurityManager):
    authremoteuserview = CustomAuthRemoteView

AUTH_TYPE = 3
CUSTOM_SECURITY_MANAGER = CustomSecurityManager



