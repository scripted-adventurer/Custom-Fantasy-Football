import React from 'react';
import {MainHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Redirect} from 'react-router-dom';

/* uses a custom form implementation to handle dynamically changing the URL based
on the league name input */

export class LeagueJoin extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null, redirect: false};
    this.leagueName = '';
    this.leaguePassword = '';
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;
    if (name === 'leagueName') {
      this.leagueName = value;
    }
    else if (name === 'leaguePassword') {
      this.leaguePassword = value;
    }
  }
  handleSubmit(event) {
    event.preventDefault();
    let options = requestOptions('POST');
    options.body = {'password': this.leaguePassword};
    options.body = JSON.stringify(options.body);
    fetch(('/api/league/' + this.leagueName + '/members'), options)
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
      return <Redirect to="/leagues" />;
    }
    if (this.state.error) {
      error = this.state.error;
    }
    return (
      <React.Fragment>
      <MainHeader />
      <p className="default-form-title">Join League</p>
      <p className="default-form-error">{error}</p>
      <form className="default-form" onSubmit={this.handleSubmit}>
        <p key="leagueName">
          <label>League Name<br />
            <input type="text" name="leagueName" 
            onChange={this.handleInputChange} />
          </label>
        </p>
        <p key="password">
          <label>Password<br />
            <input type="password" name="leaguePassword" 
            onChange={this.handleInputChange} />
          </label>
        </p>
        <input type="submit" value="Submit" />
      </form>
      </React.Fragment>
    );
  }
}