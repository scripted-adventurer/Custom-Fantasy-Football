import React from 'react';
import {Redirect} from 'react-router-dom';
import {LeagueHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Error} from '../error';

export class LeagueSettingsLineup extends React.Component {
  constructor(props) {
    super(props);
    this.state = {message: null, error: null, redirect: false,
      lineupSettings: {'DB': 0, 'DL': 0, 'K': 0, 'LB': 0, 'OL': 0, 'P': 0, 
      'QB': 0, 'RB': 0, 'TE': 0, 'WR': 0}};
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;
    this.setState({
      lineupSettings: {...this.state.lineupSettings, [name]: value}  
    });
  }
  handleSubmit(event) {
    event.preventDefault();
    let options = requestOptions('PATCH');
    options.body = {'property': 'lineup_settings', 'data': 
      this.state.lineupSettings};
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
              message: result.errors.join(' ')
            });
          }
        },
        (error) => {
          this.setState({
              message: error.message
            });
        }
      )
  }
  componentDidMount() {
    // get the existing settings 
    let options = requestOptions('GET');
    fetch(('/api/league/' + this.props.league), options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            let lineupSettings = this.state.lineupSettings;
            for (const position in result.lineup_settings) {
              lineupSettings[position] = result.lineup_settings[position];
            }
            this.setState({
              lineupSettings: lineupSettings
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
    if (this.state.redirect) {
      return <Redirect to='/league/settings' />;
    }
    return (
      <React.Fragment>
      <LeagueHeader />
      <p className="title">Update Lineup Settings</p>
      <div className="form-message">{this.state.message}</div>
      <form className="default-form" onSubmit={this.handleSubmit}>
        <p><label>DB
          <input type="number" name="DB" min="0" 
          value={this.state.lineupSettings.DB} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>DL
          <input type="number" name="DL" min="0" 
          value={this.state.lineupSettings.DL} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>K
          <input type="number" name="K" min="0" 
          value={this.state.lineupSettings.K} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>LB
          <input type="number" name="LB" min="0" 
          value={this.state.lineupSettings.LB} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>OL
          <input type="number" name="OL" min="0" 
          value={this.state.lineupSettings.OL} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>P
          <input type="number" name="P" min="0" 
          value={this.state.lineupSettings.P} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>QB
          <input type="number" name="QB" min="0" 
          value={this.state.lineupSettings.QB} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>RB
          <input type="number" name="RB" min="0" 
          value={this.state.lineupSettings.RB} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>TE
          <input type="number" name="TE" min="0" 
          value={this.state.lineupSettings.TE} 
          onChange={this.handleInputChange} />
        </label></p>
        <p><label>WR
          <input type="number" name="WR" min="0" 
          value={this.state.lineupSettings.WR} 
          onChange={this.handleInputChange} />
        </label></p>
        <input type="submit" value="Submit" />
      </form>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}