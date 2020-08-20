import React from 'react';
import {LeagueHeader} from '../header';
import {ScoreTable} from './score_table';

export class LeagueStats extends React.Component {
  render() {
    return (
      <React.Fragment>
      <LeagueHeader />
      <ScoreTable league={this.props.league} 
        type={this.props.type} columns={this.props.columns} />
      </React.Fragment>
    );
  }
}