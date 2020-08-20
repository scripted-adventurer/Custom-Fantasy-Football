import React from 'react';
import {Redirect} from 'react-router-dom';
import './form.css';
import {requestOptions} from '../config.js';

export class Form extends React.Component {
  constructor(props) {
    super(props);
    this.state = {error: null, body: {}, redirect: false};
    this.url = this.props.url;
    this.method = this.props.method;
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.fields = this.props.fields.map((field) => 
      <p key={field.name}>
        <label>{field.label}<br />
          <input type={(field.name.includes('password')) ? "password" : "text"} 
          name={field.name} onChange={this.handleInputChange} />
        </label>
      </p>
    );
  }
  handleInputChange(event) {
    const target = event.target;
    const value = target.value;
    const name = target.name;
    this.setState({
      body: {...this.state.body, [name]: value}  
    });
  }
  handleSubmit(event) {
    event.preventDefault();
    let options = requestOptions(this.method);
    options.body = this.state.body;
    options.body = JSON.stringify(options.body);
    fetch(this.url, options)
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
    let error = null;
    if (this.state.redirect) {
      return <Redirect to={this.props.onSuccess} />;
    }
    if (this.state.error) {
      error = this.state.error;
    }
    return (
      <React.Fragment>
      <p className="default-form-title">{this.props.title}</p>
      <p className="default-form-error">{error}</p>
      <form className="default-form" onSubmit={this.handleSubmit}>
        {this.fields}
        <input type="submit" value="Submit" />
      </form>
      </React.Fragment>
    );
  }
}