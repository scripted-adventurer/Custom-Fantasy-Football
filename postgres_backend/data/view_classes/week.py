# -*- coding: utf-8 -*-
from data.view_classes.custom_view import CustomView
from common.current_week import get_current_week

class Week(CustomView):
  def get(self):
    current_week = get_current_week()
    current_week = {'season_year': current_week[0], 'season_type': current_week[1],
      'week': current_week[2]}
    self.add_response_data('current_week', current_week)
    return self.return_json()