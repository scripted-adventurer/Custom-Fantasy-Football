import React from 'react';
import {LeagueHeader} from './header';
import {requestOptions} from '../config.js';
import {Error} from './error';

export class PlayerSearch extends React.Component {
  constructor(props) {
    super(props);
    this.state = {searchComplete: true, playerName: null, results: null, 
      error: null, table: null, updateNeeded: false};
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    this.setState({
      playerName: value
    });
  }
  handleSubmit(event) {
    event.preventDefault();
    this.setState({
      searchComplete: false,
      updateNeeded: true
    });
    let options = requestOptions('GET');
    fetch('/api/players?query=' + this.state.playerName, options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.setState({
              results: result.players,
              updateNeeded: true,
              searchComplete: true
            });
          }
          else {
            this.setState({
              error: result.errors.join(' '),
              updateNeeded: true,
              searchComplete: true
            });
          }
        },
        (error) => {
          this.setState({
            error: error.message,
            updateNeeded: true,
            searchComplete: true
          });
        }
      )
  }
  buildTable() {
    let table = [];
    table.push(
      <tr>
        <th>Name</th>
        <th>Team</th>
        <th>Position</th>
      </tr>
    );
    for (const player of this.state.results) {
      table.push(
        <tr key={player.id}>
          <td>{player.name}</td>
          <td>{player.team}</td>
          <td>{player.position}</td>
        </tr>
      );
    }
    return table;
  }
  update() {
    let table = '';
    if (!this.state.searchComplete) {
      table = <tr><td>Loading...</td></tr>;
    }
    else if (this.state.searchComplete && !this.state.results) {
      table = <tr><td>Unable to load search results</td></tr>;
    }
    else if (this.state.results) {
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
      <LeagueHeader />
      <p className="title">Player Search</p>
      <form className="default-form" onSubmit={this.handleSubmit}>
        <p>
          <input type="text" name="playerName" onChange={this.handleInputChange} />
        </p>
        <p>
          <input type="submit" value="Search" />
        </p>
      </form>  
      <table className="stats-table">
        <tbody>
        {this.state.table}
        </tbody>
      </table>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}