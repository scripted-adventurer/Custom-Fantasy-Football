import React from 'react';
import {Link} from 'react-router-dom';
import {LeagueHeader} from '../header';

export class LeagueSettings extends React.Component {
  constructor(props) {
    super(props);
    this.admin = this.props.admin;
    this.league = this.props.league;
    this.state = {adminFields: null};
  }
  componentDidMount() {
    if (this.admin === true) {
      const adminFields = (
        <React.Fragment>
        <p className="nav-link">
          <Link to="/league/remove">Remove From League</Link>
        </p>
        <p className="nav-link">
          <Link to="/league/settings/password">Update Password</Link>
        </p>
        <p className="nav-link">
          <Link to="/league/settings/lineup">Update Lineup Settings</Link>
        </p>
        <p className="nav-link">
          <Link to="/league/settings/scoring">Update Scoring Settings</Link>
        </p>
        </React.Fragment>
      );
      this.setState({
        adminFields: adminFields
      });
    }
  }
  render() {
    return (
      <React.Fragment>
      <LeagueHeader />
      <p className="title">Settings For League {this.league}</p>
      <p className="nav-link"><Link to="/league/leave">Leave League</Link></p>
      {this.state.adminFields}
      </React.Fragment>
    );
  }
}