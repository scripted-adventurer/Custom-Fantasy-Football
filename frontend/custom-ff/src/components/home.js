import React from 'react';
import {UnauthHeader} from './header';

export class Home extends React.Component {
  render() {
    return (
      <React.Fragment>
      <UnauthHeader />
      <p>Test explanatory content goes here.</p>
      </React.Fragment>
    );
  }
}