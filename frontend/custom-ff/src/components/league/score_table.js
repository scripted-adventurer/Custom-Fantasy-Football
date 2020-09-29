import React from 'react';
import {Error} from '../error';
import {Popup} from '../popup';
import {requestOptions} from '../../config.js';
import './score_table.css';

class StatsDetail extends React.Component {
  constructor(props) {
    super(props);
    this.data = {'id': '', 'name': '', 'team': '', 'position': '', 
      'total': ''};
    this.stats = [];
    for (const field in this.props.row) {
      if (field in this.data) {
        this.data[field] = this.props.row[field];
      }
      else {
        this.stats[field] = this.props.row[field];
      }
    }
    this.data.stats = Object.keys(this.stats).map((statName) =>
      <p key={statName} className="popup-data">{statName}:&nbsp; 
      {this.stats[statName]}</p>
    );
  }
  render() {
    return (
      <React.Fragment>
      <p className="subtitle">{this.data.name} {this.data.position}&nbsp;
      {this.data.team}</p>
      {this.data.stats}
      <p className="popup-data">Total: {this.data.total}</p>
      </React.Fragment>
    );
  }
}

class ScoreDetail extends React.Component {
  constructor(props) {
    super(props);
    this.scores = [];
    for (const playerScore of this.props.row.player_scores) {
      this.scores.push(
        <p key={playerScore.id} className="popup-data">{playerScore.name}:&nbsp; 
        {playerScore.total}</p> 
      );
    }
  }
  render() {
    return (
      <React.Fragment>
      <p className="subtitle">Lineup For {this.props.row.user}</p>
      {this.scores}
      <p className="popup-data">Total: {this.props.row.total}</p>
      </React.Fragment>
    );
  }
}

export class ScoreTable extends React.Component {
  constructor(props) {
    super(props);
    this.state = {seasonWeek: null, requestComplete: false,
      data: null, updateNeeded: true, table: null, error: null, popup: null,
      subtitle: 'Current Week'};
    if (this.props.type === 'stats') {
      this.title = 'Player Stats For ' + this.props.league;
      this.dataUrl = '/api/league/' + this.props.league + '/stats?sort=desc';
      this.responseParam = 'stats';
    }
    else if (this.props.type === 'scores') {
      this.title = 'League Scores For ' + this.props.league;
      this.dataUrl = '/api/league/' + this.props.league + '/scores?sort=desc';
      this.responseParam = 'league_scores';
    }
    // set options for the select new week dropdown
    this.currentYear = new Date().getFullYear();
    const weeks = Array.from({length: 17}, (x,i) => i + 1);
    this.weekOptions = weeks.map((week) => 
      <option key={week} value={week}>{week}</option>
    );
    this.weekOptions.unshift(<option key='None' value=''></option>);
    this.handleInputChange = this.handleInputChange.bind(this);
    this.pickNewWeek = this.pickNewWeek.bind(this);
    this.showDetailed = this.showDetailed.bind(this);
    this.closePopup = this.closePopup.bind(this);
  }
  setDataOptions() {
    this.dataOptions = requestOptions('GET');
    if (this.state.seasonWeek) {
      this.dataUrl += ('&seasonType=' + this.state.seasonWeek.season_type + 
        '&seasonYear=' + this.state.seasonWeek.season_year + '&week=' + 
        this.state.seasonWeek.week)
    }
  }
  getData() { 
    this.setDataOptions();
    fetch(this.dataUrl, this.dataOptions)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            const data = result[this.responseParam];
            this.setState({
              data: data,
              requestComplete: true,
              updateNeeded: true
            });
          }
          else {
            this.setState({
              error: result.errors.join(' '),
              requestComplete: true,
              updateNeeded: true
            });
          }
        },
        (error) => {
          this.setState({
              error: error.message,
              requestComplete: true,
              updateNeeded: true
            });
        }
      ) 
  }
  showDetailed(event) {
    event.preventDefault();
    const index = event.target.dataset.index;
    let detailedData = '';
    if (this.props.type === 'stats') { 
      detailedData = <StatsDetail row={this.state.data[index]} />;
    }
    else if (this.props.type === 'scores') {
      detailedData = <ScoreDetail row={this.state.data[index]} />;
    }
    const popup = <Popup content={detailedData} close={this.closePopup} />;
    this.setState({
      popup: popup
    });
  }
  closePopup() {
    this.setState({
      popup: null
    });
  }
  pickNewWeek(event) {
    event.preventDefault();
    this.setState({
      subtitle: (this.state.seasonWeek.season_type + ' ' + 
        this.state.seasonWeek.season_year + ' ' + this.state.seasonWeek.week),
      requestComplete: false,
      updateNeeded: true
    });
    this.getData();
  }
  handleInputChange(event) {
    const target = event.target;
    let value = target.value;
    const name = target.name;
    // special case for season_year and week, which need to be ints
    if (name === 'season_year' || name === 'week') {
      value = parseInt(value, 10);
    }
    this.setState({
      seasonWeek: {...this.state.seasonWeek, [name]: value}
    });
  }
  buildHeader() {
    const cells = this.props.columns.map((column) =>
      <th key={column}>{column}</th>
    );
    return (
      <tr key='header'>{cells}</tr>
    );
  }
  buildRow(index, data) {
    const cells = this.props.columns.map((column) =>
      <td key={column} data-index={index}>{data[column]}</td>
    );
    return (
      <tr key={'row' + index} onClick={this.showDetailed}>{cells}</tr>
    );
  }
  buildTable() {
    let table = [];
    table.push(this.buildHeader());
    for (const [index, row] of this.state.data.entries()) {
      table.push(this.buildRow(index, row));
    }
    return table;
  }
  componentDidMount() {
    this.getData();
  }
  update() {
    let table = '';
    if (!this.state.requestComplete) {
      table = <tr><td>Loading...</td></tr>;
    }
    else if (this.state.requestComplete && !this.state.data) {
      table = <tr><td>Unable to load data</td></tr>;
    }
    else if (this.state.data) {
      table = this.buildTable();
    }
    return table;
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
      {this.state.popup}
      <p className="title">{this.title}</p>
      <p className="subtitle">{this.state.subtitle}</p>
      <table className="stats-table">
        <tbody>
        {this.state.table}
        </tbody>
      </table>
      <p>Select New Week:</p>
      <form className="week-select" onSubmit={this.pickNewWeek}>
        <p><label htmlFor="season_type">Season Type&nbsp;
        <select name="season_type" onChange={this.handleInputChange}>
          <option value=""></option>
          <option value="PRE">PRE</option>
          <option value="REG">REG</option>
          <option value="POST">POST</option>
        </select>
        </label></p>
        <p><label htmlFor="season_year">Season Year&nbsp;
        <select name="season_year" onChange={this.handleInputChange}>
          <option value=""></option>
          <option value={this.currentYear}>{this.currentYear}</option>
          <option value={this.currentYear - 1}>{this.currentYear - 1}</option>
        </select>
        </label></p>
        <p><label htmlFor="week">Week&nbsp;
        <select name="week" onChange={this.handleInputChange}>
          {this.weekOptions}
        </select>
        </label></p>
        <input type="submit" value="Go" />
      </form>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}