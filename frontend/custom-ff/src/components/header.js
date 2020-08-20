import React from 'react';
import {Link} from 'react-router-dom';
import './header.css';

export class UnauthHeader extends React.Component {
  render() {
    return (
      <header>
        <Link to="/signup"><span role="img" aria-label="signup">📝</span></Link>
        <Link to="/login"><span role="img" aria-label="login">🔓</span></Link>
      </header>
    );
  }
}

export class MainHeader extends React.Component {
  render() {
    return (
      <header>
        <Link to="/leagues"><span role="img" aria-label="home">🏠</span></Link>
        <Link to="/account/settings"><span role="img" aria-label="settings">⚙️</span></Link>
        <Link to="/logout"><span role="img" aria-label="logout">🔒</span></Link>
      </header>
    );
  }
}

export class LeagueHeader extends React.Component {
  render() {
    return (
      <header>
        <Link to="/leagues"><span role="img" aria-label="home">🏠</span></Link>
        <Link to="/league/lineup"><span role="img" aria-label="lineup">📋</span></Link>
        <Link to="/league/stats"><span role="img" aria-label="stats">📊</span></Link>
        <Link to="/league/scores"><span role="img" aria-label="scores">🔢</span></Link>
        <Link to="/league/settings"><span role="img" aria-label="settings">⚙️</span></Link>
      </header>
    );
  }
}