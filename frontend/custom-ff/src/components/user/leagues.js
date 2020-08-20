import React from 'react';
import {Link} from 'react-router-dom';
import {MainHeader} from '../header';
import {Error} from '../error';
import {requestOptions} from '../../config.js';

export class UserLeagues extends React.Component {
  constructor(props) {
    super(props);
    this.state = {leagues: null};
    this.url = '/api/user';
  }
  componentDidMount() {
    const options = requestOptions('GET');
    fetch(this.url, options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            const leagues = result.leagues.map((league) => 
              <p className="nav-link" key={league}><Link to="/league/lineup" 
              onClick={() => this.props.setLeague(league)}>{league}</Link></p>
            );
            this.setState({leagues: leagues});
          }
          else {
            this.setState({
              leagues: null,
              error: result.errors.join('')
            });
          }
        },
        (error) => {
          this.setState({
            leagues: null,
            error: error.message
          });
        }
      )
  }
  render() {
    return (
      <React.Fragment>
      <MainHeader />
      <p className="title">Leagues</p>
      <p className="subtitle">Go To League:</p>
      {this.state.leagues}
      <p className="subtitle">Or:</p>
      <p className="nav-link"><Link to="/league/create">Create League</Link></p>
      <p className="nav-link"><Link to="/league/join">Join League</Link></p>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}