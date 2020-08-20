import React from 'react';
import './popup.css';

export class Popup extends React.Component {
  render() {
    return (
      <div className="popup">
        <div id="popup-close" onClick={this.props.close}>
        <span role="img" aria-label="home">❎</span></div>
        {this.props.content}
      </div>
    );
  }
}