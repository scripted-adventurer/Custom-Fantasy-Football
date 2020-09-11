# -*- coding: utf-8 -*-
from .custom_view import CustomView
from flaskr import models

class Week(CustomView):
  def get(self):
    current_week = db_models.get_current_week()
    current_week = {'season_year': current_week[0], 'season_type': current_week[1],
      'week': current_week[2]}
    self.add_response_data('current_week', current_week)
    return self.return_json()