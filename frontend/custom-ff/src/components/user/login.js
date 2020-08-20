import React from 'react';
import {UnauthHeader} from '../header';
import {Form} from '../form';

export class UserLogin extends React.Component {
  render() {
    return (
      <React.Fragment>
      <UnauthHeader />
      <Form title="Login" fields={[{'label': 'Username', 'name': 'username'},
      {'label': 'Password', 'name': 'password'}]} 
      url="/api/session"
      method="POST"
      onSuccess="/leagues" />
      </React.Fragment>
    );
  }
}