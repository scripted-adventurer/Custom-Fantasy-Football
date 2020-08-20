import React from 'react';
import {MainHeader} from '../header';
import {Form} from '../form';

export class LeagueCreate extends React.Component {
  render() {
    return (
      <React.Fragment>
      <MainHeader />
      <Form title="Create New League" fields={[
      {'label': 'League Name', 'name': 'new_league_name'},
      {'label': 'Password', 'name': 'password1'},
      {'label': 'Confirm Password', 'name': 'password2'}]} 
      url="/api/leagues"
      method="POST"
      onSuccess="/leagues" />
      </React.Fragment>
    );
  }
}