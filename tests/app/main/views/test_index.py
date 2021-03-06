import pytest
from bs4 import BeautifulSoup
from flask import url_for


def test_non_logged_in_user_can_see_homepage(
    client,
):
    response = client.get(url_for('main.index'))
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert page.select_one('meta[name=description]')['content'].startswith(
        'GOV.UK Notify lets you send emails and text messages'
    )


def test_logged_in_user_redirects_to_choose_service(
    logged_in_client,
    api_user_active,
    mock_get_user,
    mock_get_user_by_email,
    mock_login,
):
    response = logged_in_client.get(url_for('main.index'))
    assert response.status_code == 302

    response = logged_in_client.get(url_for('main.sign_in', follow_redirects=True))
    assert response.location == url_for('main.choose_service', _external=True)


@pytest.mark.parametrize('view', [
    'cookies', 'using_notify', 'pricing', 'terms', 'integration_testing', 'roadmap',
    'features', 'information_risk_management', 'callbacks'
])
def test_static_pages(
    client,
    view,
):
    response = client.get(url_for('main.{}'.format(view)))
    assert response.status_code == 200

    page = BeautifulSoup(response.data.decode('utf-8'), 'html.parser')

    assert not page.select_one('meta[name=description]')


@pytest.mark.parametrize('view, expected_anchor', [
    ('delivery_and_failure', 'messagedeliveryandfailure'),
    ('trial_mode', 'trial-mode'),
])
def test_old_static_pages(
    client,
    view,
    expected_anchor,
):
    response = client.get(url_for('main.{}'.format(view)))
    assert response.status_code == 301
    assert response.location == url_for(
        'main.using_notify',
        _anchor=expected_anchor,
        _external=True
    )
