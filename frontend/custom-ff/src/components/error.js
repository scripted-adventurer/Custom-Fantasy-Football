import React from 'react';
import './error.css';

export class Error extends React.Component {
  // TODO: methods to show and hide 
  constructor(props) {
    super(props);
    this.state = {visible: true};
  }
  componentDidMount() {
    this.setTimer();
  }
  setTimer() {
    // hide error box after 5 seconds
    if (this.timer) {
      clearTimeout(this.timer);
    }
    this.timer = setTimeout(function() {
      this.setState({visible: false});
    }.bind(this), 5000);
  }
  componentWillUnmount() {
    clearTimeout(this.timer);
  }
  render() {
    if (this.state.visible) {
      return (<div className="error-message">ERROR<br />
        {this.props.message}</div>);
    }
    else {
      return null;
    }
  }
}