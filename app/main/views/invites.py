from flask import (
    redirect,
    url_for,
    session,
    flash,
    render_template,
    abort,
    current_app
)
from itsdangerous import SignatureExpired
from markupsafe import Markup
from notifications_utils.url_safe_token import check_token
from flask_login import current_user

from app.main import main
from app import (
    invite_api_client,
    user_api_client,
    service_api_client
)


@main.route("/invitation/<token>")
def accept_invite(token):
    try:
        check_token(
            token,
            current_app.config['SECRET_KEY'],
            current_app.config['DANGEROUS_SALT'],
            current_app.config['INVITATION_EXPIRY_SECONDS']
        )
    except SignatureExpired:
        errors = [
            'Your invitation to GOV.UK Notify has expired. '
            'Please ask the person that invited you to send you another one'
        ]
        return render_template("error/400.html", message=errors), 400

    invited_user = invite_api_client.check_token(token)

    if not current_user.is_anonymous and current_user.email_address != invited_user.email_address:
        message = Markup("""
            You’re signed in as {}.
            This invite is for another email address.
            <a href={}>Sign out</a> and click the link again to accept this invite.
            """.format(
            current_user.email_address,
            url_for("main.sign_out", _external=True)))

        flash(message=message)

        abort(403)

    if invited_user.status == 'cancelled':
        from_user = user_api_client.get_user(invited_user.from_user)
        service = service_api_client.get_service(invited_user.service)['data']
        return render_template('views/cancelled-invitation.html',
                               from_user=from_user.name,
                               service_name=service['name'])

    if invited_user.status == 'accepted':
        session.pop('invited_user', None)
        return redirect(url_for('main.service_dashboard', service_id=invited_user.service))

    session['invited_user'] = invited_user.serialize()

    existing_user = user_api_client.get_user_by_email_or_none(invited_user.email_address)
    service_users = user_api_client.get_users_for_service(invited_user.service)

    if existing_user:
        invite_api_client.accept_invite(invited_user.service, invited_user.id)
        if existing_user in service_users:
            return redirect(url_for('main.service_dashboard', service_id=invited_user.service))
        else:
            service = service_api_client.get_service(invited_user.service)['data']
            # if the service you're being added to can modify auth type, then check if this is relevant
            if 'email_auth' in service['permissions'] and (
                    # they have a phone number, we want them to start using it. if they dont have a mobile we just
                    # ignore that option of the invite
                    (existing_user.mobile_number and invited_user.auth_type == 'sms_auth') or
                    # we want them to start sending emails. it's always valid, so lets always update
                    invited_user.auth_type == 'email_auth'
            ):
                user_api_client.update_user_attribute(existing_user.id, auth_type=invited_user.auth_type)
            user_api_client.add_user_to_service(invited_user.service,
                                                existing_user.id,
                                                invited_user.permissions)
            return redirect(url_for('main.service_dashboard', service_id=invited_user.service))
    else:
        return redirect(url_for('main.register_from_invite'))
