# -*- coding: utf-8 -*-
from flaskr import models
from flaskr import security 

def test_security(app):

  def test_user_basic():
    name = 'test_user'
    main = security.User(username=f'{name}_0', password='password').save()
    same = security.User.objects.get(username=f'{name}_0')
    different = security.User(username=f'{name}_1', password='password').save()
    other = models.Team(team_id='GB', name='Green Bay Packers')
    assert repr(main) == f"{{'model': 'User', 'username': '{name}_0'}}"
    assert str(main) == main.get_id()
    assert main == same
    assert hash(main) == hash(same)
    assert main != different
    assert hash(main) != hash(different)
    assert not main == other

  def test_additional():
    password_hash = security.generate_hash('password')
    user = security.User(username='test_additional', 
      password=password_hash).save()
    user.set_password('new_password')
    assert security.get_user('test_additional') == user 
    assert not security.get_user('invalid_username')
    assert security.compare_hash(user.password, 'new_password')

  test_user_basic()
  test_additional()