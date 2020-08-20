import React from 'react';
import {Link} from 'react-router-dom';
import {LeagueHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Error} from '../error';
import {Popup} from '../popup';
import './lineup_show.css';

export class LeagueLineupShow extends React.Component {
  constructor(props) {
    super(props);
    this.state = {lineupRequestComplete: false, updateNeeded: true, 
      popup: null, error: null, table: null};
    this.lineupData = null;
    this.scheduleData = null;
    this.scoreData = {};
    this.displayNews = this.displayNews.bind(this);
    this.closePopup = this.closePopup.bind(this);
  }
  getLineup() {
    let options = requestOptions('GET');
    fetch(('/api/league/' + this.props.league + '/member/lineup'), options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.lineupData = result.lineup;
            this.setState({
              lineupRequestComplete: true,
              updateNeeded: true
            });
            this.getScores();
          }
          else {
            this.setState({
              error: result.errors.join(' '),
              lineupRequestComplete: true,
              updateNeeded: true
            });
          }
        },
        (error) => {
          this.setState({
              error: error.message,
              lineupRequestComplete: true,
              updateNeeded: true
            });
        }
      )
  }
  getSchedule() {
    let options = requestOptions('GET');
    fetch('/api/games', options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.scheduleData = this.formatScheduleData(result.games);
            this.setState({
              updateNeeded: true
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
  getScores() {
    for (const entry of this.lineupData) {
      let options = requestOptions('GET');
      fetch(('/api/league/' + this.props.league + 'stats?playerId=' + entry.id), 
        options)
        .then(response => response.json())
        .then(
          (result) => {
            if (result.success) {
              this.scoreData[entry.id] = (result.stats.length > 0 ? 
                result.stats[0].total : 0);
              this.setState({
                updateNeeded: true
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
  }
  formatScheduleData(gamesData) {
    // transform the list of game objects into a lookup object keyed by team id
    // and containing the opponent, formatted gametime, and game lock status 
    let scheduleData = {}
    for (const game of gamesData) {
      const dateOptions = {weekday: 'short', hour: '2-digit', minute: '2-digit'};
      let gametime = new Date(game.start_time);
      const now = new Date();
      const locked = now > gametime ? true : false;
      gametime = gametime.toLocaleDateString('en-GB', dateOptions);
      scheduleData[game.home_team] = {'opponent': game.away_team, 
        'gametime': gametime, 'locked': locked};
      scheduleData[game.away_team] = {'opponent': game.home_team, 
        'gametime': gametime, 'locked': locked};  
    }
    return scheduleData;
  }
  closePopup() {
    this.setState({
      popup: null
    });
  }
  displayNews(event) {
    const news = event.target.dataset.news;
    const content = <p className="popup-data">{news}</p>;
    const popup = <Popup content={content} close={this.closePopup} />;
    this.setState({
      popup: popup
    });
  }
  // helper functions for buildTable 
  setIcon(entry) {
    // player is locked
    if (entry.team in this.scheduleData && 
      this.scheduleData[entry.team].locked) {
      return '🔒';
    }
    // player is on BYE
    else if (!(entry.team in this.scheduleData)) {
      return '❗';
    }
    // player is hurt or cut
    else if (entry.status !== 'Active') {
      return '❗';
    }
  }
  setOpponent(entry) {
    if (entry.team in this.scheduleData) {
      return this.scheduleData[entry.team].opponent;
    }
    else {
      return 'BYE';
    }
  }
  setGametime(entry) {
    if (entry.team in this.scheduleData) {
      return this.scheduleData[entry.team].gametime;
    }
    else {
      return '';
    }
  }
  setScore(entry) {
    if (entry.id in this.scoreData) {
      return this.scoreData[entry.id];
    }
    else {
      return '-';
    }
  }
  setNews(entry) {
    if (entry.news) {
      return '📰';
    }
    else {
      return null;
    }
  }
  buildTable() {
    const table = this.lineupData.map((entry) =>
      <tr key={entry.id} >
        <td><span role="img" aria-label="icon">{this.setIcon(entry)}</span></td>
        <td>{entry.name} {entry.position} {entry.team}&nbsp;
        <span role="img" aria-label="news" onClick={this.displayNews} 
          className="clickable" data-news={entry.news}> 
          {this.setNews(entry)}
        </span><br />
        {this.setOpponent(entry)} {this.setGametime(entry)}
        </td>
        <td className="score">{this.setScore(entry)}</td>
      </tr>
    );
    return table;
  }
  update() {
    let table = '';
    if (!this.state.lineupRequestComplete) {
      table = <tr><td>Loading...</td></tr>;
    }
    else if (this.state.lineupRequestComplete && !this.lineupData) {
      table = <tr><td>Unable to load lineup data</td></tr>;
    }
    else if (this.lineupData && this.scheduleData) {
      table = this.buildTable();
    }
    return table;
  }
  componentDidMount() {
    this.getLineup();
    this.getSchedule();
  }
  componentDidUpdate() {
    if (this.state.updateNeeded) {
      const table = this.update();
      this.setState({
        table: table,
        updateNeeded: false
      });
    }
  }
  render() {
    return (
      <React.Fragment>
      <LeagueHeader />
      {this.state.popup}
      <p className="title">{'Lineup For ' + this.props.league}</p>
      <table className="lineup-table">
        <tbody>
        {this.state.table}
        </tbody>
      </table>
      <p className="nav-link"><Link to="/league/lineup/edit">Edit Lineup</Link></p>
      <p className="nav-link"><Link to="/player/search">Player Search</Link></p>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}