import React from 'react';
import {UnauthHeader} from '../header';
import {Form} from '../form';

export class UserSignup extends React.Component {
  render() {
    return (
      <React.Fragment>
      <UnauthHeader />
      <Form title="Signup" fields={[{'label': 'Username', 'name': 'username'},
      {'label': 'Email (Optional)', 'name': 'email'},
      {'label': 'Password', 'name': 'password1'},
      {'label': 'Confirm Password', 'name': 'password2'}]} 
      url="/api/users"
      method="POST"
      onSuccess="/leagues" />
      </React.Fragment>
    );
  }
}