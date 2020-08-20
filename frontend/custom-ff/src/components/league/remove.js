import React from 'react';
import {LeagueHeader} from '../header';
import {Form} from '../form';

export class LeagueRemove extends React.Component {
  render() {
    return (
      <React.Fragment>
      <LeagueHeader />
      <Form title="Remove User From League" fields={[{'label': 'Username', 
      'name': 'username'}]}
      url={"/api/league/" + this.props.league + "/member"}
      method="DELETE"
      onSuccess="/league/settings" />
      </React.Fragment>
    );
  }
}