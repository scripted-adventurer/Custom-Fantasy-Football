from flask import Flask, request, jsonify, Response

def create_app():
  """Create and configure an instance of the Flask application."""
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
      # a default secret that should be overridden by instance config
      SECRET_KEY="dev",
  )

  def bad_request():
    return Response(jsonify({'success': False, 'errors': ['HTTP 400: Bad Request']}), 
      status=400, mimetype='application/json')

  @app.route('/games', methods=['GET'])
  def games():
    return servicer.Servicer(endpoint='get_games', request=request).response()

  @app.route('/league/<league_name>/member', methods=['GET', 'DELETE'])
  def league_member(league_name):
    if request.method == 'GET':
      return servicer.Servicer(endpoint='get_member_info', request=request, 
        required_params=['league_name'], url_data={'league_name': league_name}
        ).response()
    elif request.method == 'DELETE' and request.json.get('password'):  
      return servicer.Servicer(endpoint='leave_league', request=request, 
        required_params=['league_name', 'password'], url_data={'league_name': 
        league_name}).response()
    elif request.method == 'DELETE' and request.json.get('password'):  
      return servicer.Servicer(endpoint='remove_from_league', request=request, 
        required_params=['league_name', 'username'], url_data={'league_name': 
        league_name}).response()  
    else:
      return bad_request()   

  @app.route('/league/<league_name>/member/lineup', methods=['GET', 'PUT'])
  def league_member_lineup(league_name):
    if request.method == 'GET':
      return servicer.Servicer(endpoint='get_lineup', request=request, 
        required_params=['league_name'], url_data={'league_name': league_name}
        ).response()
    elif request.method == 'PUT':  
      return servicer.Servicer(endpoint='edit_lineup', request=request, 
        required_params=['league_name', 'lineup'], url_data={'league_name': 
        league_name}).response()

  @app.route('/league/<league_name>/members', methods=['POST'])
  def league_members(league_name):
    return servicer.Servicer(endpoint='join_league', request=request, 
      required_params=['league_name', 'password'], url_data={'league_name': 
      league_name}).response()

  @app.route('/league/<league_name>/scores', methods=['GET'])
  def league_scores(league_name):
    return servicer.Servicer(endpoint='get_league_scores', request=request, 
      required_params=['league_name'], url_data={'league_name': league_name}
      ).response()

  @app.route('/league/<league_name>/stats', methods=['GET'])
  def league_stats(league_name):
    return servicer.Servicer(endpoint='get_league_stats', request=request, 
      required_params=['league_name'], url_data={'league_name': league_name}
      ).response()

  @app.route('/league/<league_name>', methods=['GET', 'PATCH'])
  def league(league_name):
    if request.method == 'GET':
      return servicer.Servicer(endpoint='get_league', request=request, 
        required_params=['league_name'], url_data={'league_name': league_name}
        ).response()
    elif request.method == 'PATCH' and request.json.get('property') == 'password':
      return servicer.Servicer(endpoint='update_league_password', request=request, 
        required_params=['property', 'data'], url_data={'league_name': 
        league_name}).response()
    elif request.method == 'PATCH' and request.json.get('property') == 'lineup_settings':
      return servicer.Servicer(endpoint='update_league_lineup', request=request, 
        required_params=['property', 'data'], url_data={'league_name': 
        league_name}).response()
    elif request.method == 'PATCH' and request.json.get('property') == 'scoring_settings':
      return servicer.Servicer(endpoint='update_league_scoring', request=request, 
        required_params=['property', 'data'], url_data={'league_name': league_name}
        ).response()      
    else:
      return bad_request() 

  @app.route('/leagues', methods=['POST'])
  def leagues():
    return servicer.Servicer(endpoint='create_league', request=request, 
      required_params=['new_league_name', 'password1', 'password2']).response() 

  @app.route('/player', methods=['GET'])
  def player():
    return servicer.Servicer(endpoint='get_player', request=request, 
      required_params=['player_id']).response()

  @app.route('/players', methods=['GET'])
  def players():
    if request.args.get('query'):
      return servicer.Servicer(endpoint='player_query', request=request, 
        required_params=['query']).response()
    elif request.args.get('available'):
      return servicer.Servicer(endpoint='available_players', request=request, 
        required_params=['available']).response()
    else:
      return bad_request()  

  @app.route('/session', methods=['POST', 'DELETE'])
  def session():
    if request.method == 'POST':
      return servicer.Servicer(endpoint='login', request=request, 
        required_params=['username', 'password']).response()
    elif request.method == 'DELETE':
      return servicer.Servicer(endpoint='logout', request=request).response()

  @app.route('/team', methods=['GET'])
  def team():
    return servicer.Servicer(endpoint='get_team', request=request, 
      required_params=['team_id']).response()

  @app.route('/teams', methods=['GET'])
  def teams():
    return servicer.Servicer(endpoint='get_teams', request=request).response()    

  @app.route('/user', methods=['GET', 'DELETE', 'PATCH'])
  def user():
    if request.method == 'GET':
      return servicer.Servicer(endpoint='get_user', request=request).response()
    elif request.method == 'DELETE':
      return servicer.Servicer(endpoint='delete_user', request=request, 
        required_params=['password']).response()
    elif request.method == 'PATCH' and request.json.get('property') == 'password':
      return servicer.Servicer(endpoint='update_user_password', request=request, 
        required_params=['property', 'data']).response()
    else:
      return bad_request()

  @app.route('/users', methods=['POST'])
  def users():
    # check for matched passwords 
    return servicer.Servicer(endpoint='create_user', request=request, 
      required_params=['username', 'password1', 'password2']).response()

  @app.route('/week', methods=['GET'])
  def week():
    return servicer.Servicer(endpoint='get_week', request=request).response()

  return app