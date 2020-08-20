import React from 'react';
import {LeagueHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Redirect} from 'react-router-dom';

/* uses a custom form implementation to handle setting the nested request data */

export class LeagueSettingsPassword extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null, redirect: false};
    this.data = {};
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;
    this.data[name] = value;
  }
  handleSubmit(event) {
    event.preventDefault();
    let options = requestOptions('PATCH');
    options.body = {'property': 'password', 'data': this.data};
    options.body = JSON.stringify(options.body);
    fetch(('/api/league/' + this.props.league), options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.setState({
              redirect: true
            });
          }
          else {
            this.setState({
              error: result.errors.join(' ')
            });
          }
        },
        (error) => {
          this.setState({
            error: error.message
          });
        }
      )
  }
  render() {
    let error = null;
    if (this.state.redirect) {
      return <Redirect to="/league/settings" />;
    }
    if (this.state.error) {
      error = this.state.error;
    }
    return (
      <React.Fragment>
      <LeagueHeader />
      <p className="default-form-title">Update League Password</p>
      <p className="default-form-error">{error}</p>
      <form className="default-form" onSubmit={this.handleSubmit}>
        <p key="password1">
          <label>New Password<br />
            <input type="password" name="password1" 
            onChange={this.handleInputChange} />
          </label>
        </p>
        <p key="password2">
          <label>Confirm New Password<br />
            <input type="password" name="password2" 
            onChange={this.handleInputChange} />
          </label>
        </p>
        <input type="submit" value="Submit" />
      </form>
      </React.Fragment>
    );
  }
}