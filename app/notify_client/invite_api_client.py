
from app.notify_client import _attach_current_user, NotifyAdminAPIClient
from app.notify_client.models import InvitedUser


class InviteApiClient(NotifyAdminAPIClient):
    def __init__(self):
        super().__init__("a" * 73, "b")

    def init_app(self, app):
        self.base_url = app.config['API_HOST_NAME']
        self.service_id = app.config['ADMIN_CLIENT_USER_NAME']
        self.api_key = app.config['ADMIN_CLIENT_SECRET']

    def create_invite(self, invite_from_id, service_id, email_address, permissions, auth_type):
        data = {
            'service': str(service_id),
            'email_address': email_address,
            'from_user': invite_from_id,
            'permissions': permissions,
            'auth_type': auth_type
        }
        data = _attach_current_user(data)
        resp = self.post(url='/service/{}/invite'.format(service_id), data=data)
        return InvitedUser(**resp['data'])

    def get_invites_for_service(self, service_id):
        endpoint = '/service/{}/invite'.format(service_id)
        resp = self.get(endpoint)
        invites = resp['data']
        invited_users = self._get_invited_users(invites)
        return invited_users

    def check_token(self, token):
        resp = self.get(url='/invite/{}'.format(token))
        return InvitedUser(**resp['data'])

    def cancel_invited_user(self, service_id, invited_user_id):
        data = {'status': 'cancelled'}
        data = _attach_current_user(data)
        self.post(url='/service/{0}/invite/{1}'.format(service_id, invited_user_id),
                  data=data)

    def accept_invite(self, service_id, invited_user_id):
        data = {'status': 'accepted'}
        self.post(url='/service/{0}/invite/{1}'.format(service_id, invited_user_id),
                  data=data)

    def _get_invited_users(self, invites):
        invited_users = []
        for invite in invites:
            invited_user = InvitedUser(**invite)
            invited_users.append(invited_user)
        return invited_users
