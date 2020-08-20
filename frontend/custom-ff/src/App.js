import React from 'react';
import './App.css';
import {Switch, Route} from 'react-router-dom';
import {Home} from './components/home';

import {UserSignup} from './components/user/signup';
import {UserLogin} from './components/user/login';
import {UserLogout} from './components/user/logout';
import {UserSettings} from './components/user/settings';
import {UserUpdatePassword} from './components/user/update_password';
import {UserDelete} from './components/user/delete';
import {UserLeagues} from './components/user/leagues';

import {LeagueCreate} from './components/league/create';
import {LeagueJoin} from './components/league/join';
import {LeagueLineupShow} from './components/league/lineup_show';
import {LeagueLineupEdit} from './components/league/lineup_edit';
import {LeagueSettings} from './components/league/settings';
import {LeagueSettingsPassword} from './components/league/settings_password';
import {LeagueSettingsLineup} from './components/league/settings_lineup';
import {LeagueSettingsScoring} from './components/league/settings_scoring';
import {LeagueLeave} from './components/league/leave';
import {LeagueRemove} from './components/league/remove';
import {LeagueStats} from './components/league/stats';
import {LeagueScores} from './components/league/scores';

import {PlayerSearch} from './components/player_search';

import {requestOptions} from './config.js';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {league: null, admin: false};
    this.setLeague = this.setLeague.bind(this);
  }
  setLeague(leagueName) {
    let options = requestOptions('GET');
    fetch('/api/league/' + leagueName + '/member', options)
      .then(response => response.json())
      .then(
        (result) => {
          if (result.success) {
            this.setState({
              admin: result.admin
            });
          }
          else {
            console.log("Error: unable to retrieve admin information for " + 
              `league ${leagueName}. ${result.errors.join(' ')}`);
          }
        },
        (error) => {
          console.log("Error: unable to retrieve admin information for " + 
            `league ${leagueName}. ${error.message}`);
        }
      ) 
    this.setState({
      league: leagueName
    });   
  }
  render() {
    return (
      <Switch>
        <Route exact path="/" component={Home} />
        <Route path="/signup" component={UserSignup} />
        <Route path="/login" component={UserLogin} />
        <Route path="/logout" component={UserLogout} />
        <Route path="/account/settings" component={UserSettings} />
        <Route path="/account/update-password" component={UserUpdatePassword} />
        <Route path="/account/delete" component={UserDelete} />
        <Route 
          path="/leagues"
          render={(props) => <UserLeagues {...props} 
          setLeague={this.setLeague} />}
        />
        <Route path="/league/create" component={LeagueCreate} />
        />
        <Route path="/league/join" component={LeagueJoin} />
        <Route 
          path="/league/settings" exact
          render={(props) => <LeagueSettings {...props} 
          league={this.state.league} admin={this.state.admin} />}
        />
        <Route 
          path="/league/settings/password"
          render={(props) => <LeagueSettingsPassword {...props} 
          league={this.state.league} admin={this.state.admin} />}
        />
        <Route 
          path="/league/settings/lineup"
          render={(props) => <LeagueSettingsLineup {...props} 
          league={this.state.league} admin={this.state.admin} />}
        />
        <Route 
          path="/league/settings/scoring"
          render={(props) => <LeagueSettingsScoring {...props} 
          league={this.state.league} admin={this.state.admin} />}
        />
        <Route 
          path="/league/leave"
          render={(props) => <LeagueLeave {...props} 
          league={this.state.league} />}
        />
        <Route 
          path="/league/remove"
          render={(props) => <LeagueRemove {...props} 
          league={this.state.league} />}
        />
        <Route 
          path="/league/lineup" exact
          render={(props) => <LeagueLineupShow {...props} 
          league={this.state.league} />}
        />
        <Route 
          path="/league/lineup/edit"
          render={(props) => <LeagueLineupEdit {...props} 
          league={this.state.league} />}
        />
        <Route 
          path="/league/stats"
          render={(props) => <LeagueStats {...props} 
          league={this.state.league} 
          type="stats" columns={['name', 'team', 'position', 'total']} />}
        />
        <Route 
          path="/league/scores"
          render={(props) => <LeagueScores {...props} 
          league={this.state.league} 
          type="scores" columns={['user', 'total']} />}
        /> 
        <Route path="/player/search" component={PlayerSearch} />
      </Switch>
    );
  }
}

export default App;