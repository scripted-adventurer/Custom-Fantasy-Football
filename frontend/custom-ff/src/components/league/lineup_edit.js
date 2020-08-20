import React from 'react';
import {Redirect} from 'react-router-dom';
import {LeagueHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Error} from '../error';

class LineupDropDown extends React.Component {
  constructor(props) {
    super(props);
    this.state = {update: false};
    this.options = null;
  }
  update() {
    this.options = this.props.players.map((player) => 
      <option key={player.id} value={player.id}>{player.name}</option>
    );
  }
  componentDidUpdate() {
    if (!this.state.update) {
      this.update();
      this.setState({
        update: true
      });
    }
  }
  componentDidMount() {
    this.update();
  }
  render() {
    return (
      <div className="label-input-box">
        <label>{this.props.locked ? <span role="img" aria-label="logout">🔒 </span>
        : null}{this.props.label}&nbsp;</label>
        <select name={this.props.label} onChange={this.props.onChange}
        value={this.props.selectedPlayer} disabled={this.props.locked}>
          <option value=""></option>
          {this.options}
        </select>
      </div>
    );
  }
}

export class LeagueLineupEdit extends React.Component {
  constructor(props) {
    super(props);
    this.state = {settingsRequestComplete: false, playersRequestComplete: false,
      requestedLineup: false, updateNeeded: true, requestError: null, 
      formError: null, form: null, redirect: false};
    // determines how many dropdowns to build and the label for each (ex. QB1)
    this.leagueSettings = null;
    // used to build the drop down options
    this.availablePlayers = null;
    this.oldLineup = null;
    this.newLineup = {};
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleInputChange = this.handleInputChange.bind(this);
  }
  seedNewLineup() {
    // add the corresponding position labels from the league's lineup settings 
    // to newLineup so lineup changes can be tracked 
    for (const position of Object.keys(this.leagueSettings)) {
      for (let pos_num = 1; pos_num <= this.leagueSettings[position]; pos_num++) {
        const positionLabel = position + pos_num;
        this.newLineup[positionLabel] = {};
      }
    }
  }
  getLineupSettings() {
    let options = requestOptions('GET');
    fetch(('/api/league/' + this.props.league), options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.leagueSettings = result.lineup_settings;
            this.seedNewLineup();
            this.setState({
              settingsRequestComplete: true,
              updateNeeded: true
            });
          }
          else {
            this.setState({
              requestError: result.errors.join(' '),
              settingsRequestComplete: true,
              updateNeeded: true
            });
          }
        },
        (error) => {
          this.setState({
              requestError: error.message,
              settingsRequestComplete: true,
              updateNeeded: true
            });
        }
      )
  }
  getAvailablePlayers() {
    const options = requestOptions('GET');
    fetch('/api/players?available=true', options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.availablePlayers = result.players;
            this.setState({
              playersRequestComplete: true,
              updateNeeded: true
            });
          }
          else {
            this.setState({
              requestError: result.errors.join(''),
              playersRequestComplete: true,
              updateNeeded: true
            });
          }
        },
        (error) => {
          this.setState({
            requestError: error.message,
            playersRequestComplete: true,
            updateNeeded: true
          });
        }
      )
  }
  // helper for addOldLineup
  playerIsAvailable(playerToCheck) {
    // checks if a player object is in the availablePlayers position array
    if (!(playerToCheck.position in this.availablePlayers)) {
      return false;
    }
    for (const availablePlayer of this.availablePlayers[playerToCheck.position]) {
      if (availablePlayer.id === playerToCheck.id) {
        return true;
      }
    }
    return false;
  }
  addOldLineup(lineup) {
    // adds the existing lineup players as options in the dropdowns and sets 
    // each dropdown's value to that player
    for (const oldPlayer of lineup) {
      let newPlayer = {'id': oldPlayer.id, 'name': oldPlayer.name, 'locked': 
        false}
      // player is locked and can't be edited if it's not available
      if (!this.playerIsAvailable(oldPlayer)) {
        newPlayer.locked = true;
      }
      // set the value to the player 
      for (const positionLabel of Object.keys(this.newLineup)) {
        if (oldPlayer.position === positionLabel.slice(0, -1) && 
          !this.newLineup[positionLabel].id) {
          this.newLineup[positionLabel] = newPlayer;
          // only set the first match 
          break;
        }
      }
    }
  }
  getLineup() {
    let options = requestOptions('GET');
    fetch(('/api/league/' + this.props.league + '/member/lineup'), options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.addOldLineup(result.lineup);
            this.setState({
              updateNeeded: true
            });
          }
          else {
            this.setState({
              requestError: result.errors.join(' ')
            });
          }
        },
        (error) => {
          this.setState({
              requestError: error.message
            });
        }
      )
  }
  handleSubmit(event) {
    event.preventDefault();
    let lineup = [];
    for (const positionLabel in this.newLineup) {
      lineup.push(this.newLineup[positionLabel].id);
    }
    let options = requestOptions('PUT');
    options.body = {'lineup': lineup};
    options.body = JSON.stringify(options.body);
    fetch(('/api/league/' + this.props.league + 'member/lineup'), options)
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
              formError: result.errors.join(' ')
            });
          }
        },
        (error) => {
          this.setState({
            formError: error.message
          });
        }
      )
  }
  handleInputChange(event) {
    const positionLabel = event.target.name;
    const value = event.target.value;
    this.newLineup[positionLabel] = {'id': value, 'name': '', 'locked': false};
    this.setState({
      updateNeeded: true
    });
  }
  buildForm() {
    // build the lineup dropdowns in alpha order, adding the correct number of
    // dropdowns for each position in the league's lineup settings
    let fields = [];
    for (const position of Object.keys(this.leagueSettings).sort()) {
      for (let pos_num = 1; pos_num <= this.leagueSettings[position]; pos_num++) {
        let availablePlayers = (position in this.availablePlayers ? 
          this.availablePlayers[position] : []);
        const positionLabel = position + pos_num;
        const newPlayer = this.newLineup[positionLabel];
        // if the player is locked, add him to the dropdown fields so his name 
        // will display in the form
        if (newPlayer.locked) {
          availablePlayers.push(newPlayer);
        }
        fields.push(
          <LineupDropDown key={positionLabel} label={positionLabel}
          onChange={this.handleInputChange} players={availablePlayers}
          selectedPlayer={newPlayer.id} locked={newPlayer.locked} />
        );
      }
    }
    return (
      <form className="default-form" onSubmit={this.handleSubmit}>
        {fields}
        <input type="submit" value="Submit" />
      </form>
    );
  }
  update() {
    let form = '';
    if (!this.state.settingsRequestComplete || !this.state.playersRequestComplete) {
      form = <div>Loading...</div>;
    }
    else if ((this.state.settingsRequestComplete && this.state.playersRequestComplete) 
      && (!this.leagueSettings || !this.availablePlayers)){
      form = <div>Unable to load lineup form</div>;
    }
    else if (this.leagueSettings && this.availablePlayers) {
      form = this.buildForm();
    }
    return form;
  }
  componentDidMount() {
    this.getLineupSettings();
    this.getAvailablePlayers();
  }
  componentDidUpdate() {
    // old lineup is added after data is returned and new lineup is seeded with 
    // the correct position labels from the league's settings
    if (this.leagueSettings && this.availablePlayers && 
      !this.state.requestedLineup) {
      this.getLineup();
      this.setState({
        requestedLineup: true
      });
    }
    if (this.state.updateNeeded) {
      const form = this.update();
      this.setState({
        form: form,
        updateNeeded: false
      });
    }
  }
  render() {
    if (this.state.redirect) {
      return <Redirect to='/league/lineup' />;
    }
    return (
      <React.Fragment>
      <LeagueHeader />
      <p className="title">{'Edit lineup for ' + this.props.league}</p>
      <p className="default-form-error">{this.state.formError}</p>
      {this.state.form}
      {this.state.requestError && <Error message={this.state.requestError} />}
      </React.Fragment>
    );
  }
}