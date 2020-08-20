import React from 'react';
import {LeagueHeader} from '../header';
import {Form} from '../form';

export class LeagueLeave extends React.Component {
  render() {
    return (
      <React.Fragment>
      <LeagueHeader />
      <Form title="Confirm Leaving League" fields={[{'label': 'Password', 
      'name': 'password'}]} 
      url={"/api/league/" + this.props.league + "/member"}
      method="DELETE"
      onSuccess="/leagues" />
      </React.Fragment>
    );
  }
}