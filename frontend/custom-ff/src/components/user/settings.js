import React from 'react';
import {Link} from 'react-router-dom';
import {MainHeader} from '../header';

export class UserSettings extends React.Component {
  render() {
    return (
      <React.Fragment>
      <MainHeader />
      <p className="title">Account Settings</p>
      <p className="nav-link"><Link to="/account/update-password">Update Password</Link></p>
      <p className="nav-link"><Link to="/account/delete">Delete Account</Link></p>
      </React.Fragment>
    );
  }
}