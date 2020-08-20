import React from 'react';
import {Redirect} from 'react-router-dom';
import {requestOptions} from '../../config.js';
import {MainHeader} from '../header';
import {Error} from '../error';

export class UserLogout extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null, redirect: false};
  }
  componentDidMount() {
    let options = requestOptions('DELETE');
    options.body = JSON.stringify({});
    fetch('/api/session', options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.setState({redirect: true});
          }
          else {
            this.setState({error: result.errors.join(')')});
          }
        },
        (error) => {
          this.setState({error: error.message});
        }
      )
  }
  render() {
    if (this.state.redirect) {
      return <Redirect to="/" />;
    }
    return (
      <React.Fragment>
      <MainHeader />
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}