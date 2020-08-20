import React from 'react';
import {MainHeader} from '../header';
import {Form} from '../form';

export class UserDelete extends React.Component {
  render() {
    return (
      <React.Fragment>
      <MainHeader />
      <Form title="Confirm Account Deletion" fields={[
      {'label': 'Password', 'name': 'password'}]} 
      url="/api/user"
      method="DELETE"
      onSuccess="/" />
      </React.Fragment>
    );
  }
}