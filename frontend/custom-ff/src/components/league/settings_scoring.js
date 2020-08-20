import React from 'react';
import {Redirect} from 'react-router-dom';
import {LeagueHeader} from '../header';
import {requestOptions} from '../../config.js';
import {Error} from '../error';
import './settings_scoring.css';

class TableField extends React.Component {
  render() {
    return (
      <div className="label-input-box">
        <label>Table:&nbsp;</label>
        <select name="table" onChange={this.props.onChange} 
        data-stat-index={this.props.statIndex}
        data-stat-field={this.props.statField} 
        data-condition-index={this.props.conditionIndex}
        data-condition-field={this.props.conditionField}
        value={this.props.value}>
          <option value=""></option>
          <option value="play_player">play_player</option>
          <option value="play">play</option>
          <option value="agg_play">agg_play</option>
        </select>
      </div>
    );
  }
}

class ColumnField extends React.Component {
  render() {
    return (
      <div className="label-input-box">
        <label>Column:&nbsp;</label>
        <select name="table" onChange={this.props.onChange} 
        data-stat-index={this.props.statIndex}
        data-stat-field={this.props.statField} 
        data-condition-index={this.props.conditionIndex}
        data-condition-field={this.props.conditionField}
        value={this.props.value}>
          <option value=""></option>
          <option value="defense_ast">defense_ast</option>
          <option value="defense_ffum">defense_ffum</option>
          <option value="defense_fgblk">defense_fgblk</option>
          <option value="defense_frec">defense_frec</option>
          <option value="defense_frec_tds">defense_frec_tds</option>
          <option value="defense_frec_yds">defense_frec_yds</option>
          <option value="defense_int">defense_int</option>
          <option value="defense_int_tds">defense_int_tds</option>
          <option value="defense_int_yds">defense_int_yds</option>
          <option value="defense_misc_tds">defense_misc_tds</option>
          <option value="defense_misc_yds">defense_misc_yds</option>
          <option value="defense_pass_def">defense_pass_def</option>
          <option value="defense_puntblk">defense_puntblk</option>
          <option value="defense_qbhit">defense_qbhit</option>
          <option value="defense_safe">defense_safe</option>
          <option value="defense_sk">defense_sk</option>
          <option value="defense_sk_yds">defense_sk_yds</option>
          <option value="defense_tkl">defense_tkl</option>
          <option value="defense_tkl_loss">defense_tkl_loss</option>
          <option value="defense_tkl_loss_yds">defense_tkl_loss_yds</option>
          <option value="defense_tkl_primary">defense_tkl_primary</option>
          <option value="defense_xpblk">defense_xpblk</option>
          <option value="down">down</option>
          <option value="first_down">first_down</option>
          <option value="fourth_down_att">fourth_down_att</option>
          <option value="fourth_down_conv">fourth_down_conv</option>
          <option value="fourth_down_failed">fourth_down_failed</option>
          <option value="fumbles_forced">fumbles_forced</option>
          <option value="fumbles_lost">fumbles_lost</option>
          <option value="fumbles_notforced">fumbles_notforced</option>
          <option value="fumbles_oob">fumbles_oob</option>
          <option value="fumbles_rec">fumbles_rec</option>
          <option value="fumbles_rec_tds">fumbles_rec_tds</option>
          <option value="fumbles_rec_yds">fumbles_rec_yds</option>
          <option value="fumbles_tot">fumbles_tot</option>
          <option value="kicking_all_yds">kicking_all_yds</option>
          <option value="kicking_downed">kicking_downed</option>
          <option value="kicking_fga">kicking_fga</option>
          <option value="kicking_fgb">kicking_fgb</option>
          <option value="kicking_fgm">kicking_fgm</option>
          <option value="kicking_fgm_yds">kicking_fgm_yds</option>
          <option value="kicking_fgmissed">kicking_fgmissed</option>
          <option value="kicking_fgmissed_yds">kicking_fgmissed_yds</option>
          <option value="kicking_i20">kicking_i20</option>
          <option value="kicking_rec">kicking_rec</option>
          <option value="kicking_rec_tds">kicking_rec_tds</option>
          <option value="kicking_tot">kicking_tot</option>
          <option value="kicking_touchback">kicking_touchback</option>
          <option value="kicking_xpa">kicking_xpa</option>
          <option value="kicking_xpb">kicking_xpb</option>
          <option value="kicking_xpmade">kicking_xpmade</option>
          <option value="kicking_xpmissed">kicking_xpmissed</option>
          <option value="kicking_yds">kicking_yds</option>
          <option value="kickret_fair">kickret_fair</option>
          <option value="kickret_oob">kickret_oob</option>
          <option value="kickret_ret">kickret_ret</option>
          <option value="kickret_tds">kickret_tds</option>
          <option value="kickret_touchback">kickret_touchback</option>
          <option value="kickret_yds">kickret_yds</option>
          <option value="passing_att">passing_att</option>
          <option value="passing_cmp">passing_cmp</option>
          <option value="passing_cmp_air_yds">passing_cmp_air_yds</option>
          <option value="passing_first_down">passing_first_down</option>
          <option value="passing_incmp">passing_incmp</option>
          <option value="passing_incmp_air_yds">passing_incmp_air_yds</option>
          <option value="passing_int">passing_int</option>
          <option value="passing_sk">passing_sk</option>
          <option value="passing_sk_yds">passing_sk_yds</option>
          <option value="passing_tds">passing_tds</option>
          <option value="passing_twopta">passing_twopta</option>
          <option value="passing_twoptm">passing_twoptm</option>
          <option value="passing_twoptmissed">passing_twoptmissed</option>
          <option value="passing_yds">passing_yds</option>
          <option value="penalty">penalty</option>
          <option value="penalty_first_down">penalty_first_down</option>
          <option value="penalty_yds">penalty_yds</option>
          <option value="punting_blk">punting_blk</option>
          <option value="punting_i20">punting_i20</option>
          <option value="punting_tot">punting_tot</option>
          <option value="punting_touchback">punting_touchback</option>
          <option value="punting_yds">punting_yds</option>
          <option value="puntret_downed">puntret_downed</option>
          <option value="puntret_fair">puntret_fair</option>
          <option value="puntret_oob">puntret_oob</option>
          <option value="puntret_tds">puntret_tds</option>
          <option value="puntret_tot">puntret_tot</option>
          <option value="puntret_touchback">puntret_touchback</option>
          <option value="puntret_yds">puntret_yds</option>
          <option value="receiving_rec">receiving_rec</option>
          <option value="receiving_tar">receiving_tar</option>
          <option value="receiving_tds">receiving_tds</option>
          <option value="receiving_twopta">receiving_twopta</option>
          <option value="receiving_twoptm">receiving_twoptm</option>
          <option value="receiving_twoptmissed">receiving_twoptmissed</option>
          <option value="receiving_yac_yds">receiving_yac_yds</option>
          <option value="receiving_yds">receiving_yds</option>
          <option value="rushing_att">rushing_att</option>
          <option value="rushing_first_down">rushing_first_down</option>
          <option value="rushing_loss">rushing_loss</option>
          <option value="rushing_loss_yds">rushing_loss_yds</option>
          <option value="rushing_tds">rushing_tds</option>
          <option value="rushing_twopta">rushing_twopta</option>
          <option value="rushing_twoptm">rushing_twoptm</option>
          <option value="rushing_twoptmissed">rushing_twoptmissed</option>
          <option value="rushing_yds">rushing_yds</option>
          <option value="third_down_att">third_down_att</option>
          <option value="third_down_conv">third_down_conv</option>
          <option value="third_down_failed">third_down_failed</option>
          <option value="timeout">timeout</option>
          <option value="xp_aborted">xp_aborted</option>
          <option value="yards_to_go">yards_to_go</option>
        </select>
      </div>
    );
  }
}

class ComparisonField extends React.Component {
  render() {
    return (
      <div className="label-input-box">
        <label>Comparison:&nbsp;</label>
        <select name="table" onChange={this.props.onChange} 
        data-stat-index={this.props.statIndex}
        data-stat-field="conditions" 
        data-condition-index={this.props.conditionIndex}
        data-condition-field="comparison"
        value={this.props.value}>
          <option value=""></option>
          <option value="=">&#61;</option>
          <option value="<">&lt;</option>
          <option value=">">&gt;</option>
          <option value="<=">&lt;&#61;</option>
          <option value=">=">&gt;&#61;</option>
        </select>
      </div>
    );
  }
}

class ConditionFields extends React.Component {
  render() {
    return (
      <div className="conditions-container">
        <div className="conditions-icon">
          <span role="img" aria-label="delete" 
          data-stat-index={this.props.statIndex}
          data-condition-index={this.props.conditionIndex}
          onClick={this.props.removeCondition}>❌</span>
        </div>
        <div className="conditions-content">
          <TableField onChange={this.props.onChange} 
          statIndex={this.props.statIndex}
          statField="conditions" conditionIndex={this.props.conditionIndex} 
          conditionField="table" value={this.props.table} />
          <ColumnField onChange={this.props.onChange} 
          statIndex={this.props.statIndex}
          statField="conditions" conditionIndex={this.props.conditionIndex} 
          conditionField="column" value={this.props.column} />
          <ComparisonField onChange={this.props.onChange} 
          statIndex={this.props.statIndex}
          statField="conditions" conditionIndex={this.props.conditionIndex} 
          conditionField="comparison" value={this.props.comparison} />
          <div className="label-input-box">
            <label>Value:&nbsp;</label>
            <input type="number" name="name" onChange={this.props.onChange}
            data-stat-index={this.props.statIndex}
            data-stat-field="conditions"
            data-condition-index={this.props.conditionIndex}
            data-condition-field="value" value={this.props.value} />
          </div>
        </div>
      </div>
    );
  }
}

class StatFields extends React.Component {
  constructor(props) {
    super(props);
    this.state = {conditionFields: null, updateNeeded: false};
    this.conditions = this.props.conditions;
    this.handleConditionChange = this.handleConditionChange.bind(this);
  }
  buildConditionFields() {
    let conditionFields = [];
    for (let condIndex = 0; condIndex < this.conditions.length; condIndex++) {
      const thisCondition = this.conditions[condIndex];
      conditionFields.push(
        // this key value ensures updates made to the object cause a re-render
        <ConditionFields key={JSON.stringify(thisCondition)} 
        statIndex={this.props.statIndex} 
        conditionIndex={condIndex} onChange={this.handleConditionChange} 
        table={thisCondition.table} column={thisCondition.column} 
        comparison={thisCondition.comparison} value={thisCondition.value}
        removeCondition={this.props.removeCondition} />
      );
    }
    return conditionFields;
  }
  handleConditionChange(event) {
    this.props.onChange(event);
    this.setState({
      updateNeeded: true
    })
  }
  componentDidMount() {
    const conditionFields = this.buildConditionFields();
    this.setState({
      conditionFields: conditionFields
    });
  }
  componentDidUpdate() {
    if (this.state.updateNeeded) {
      const conditionFields = this.buildConditionFields();
      this.setState({
        conditionFields: conditionFields,
        updateNeeded: false
      });
    }
  }
  render() {
    return (
      <div className="stats-container">
        <div className="stats-content">
          <div className="label-input-box">
            <label>Name:&nbsp;</label>
            <input type="text" name="name" onChange={this.props.onChange}
            data-stat-index={this.props.statIndex}
            data-stat-field="name" value={this.props.name} />
          </div>
          <TableField onChange={this.props.onChange} statIndex={this.props.statIndex}
          statField="table" value={this.props.table} />
          <ColumnField onChange={this.props.onChange} statIndex={this.props.statIndex}
          statField="column" value={this.props.column} />
          <div className="label-input-box">
            <label>Multiplier:&nbsp;</label>
            <input type="number" name="name" onChange={this.props.onChange}
            data-stat-index={this.props.statIndex}
            data-stat-field="multiplier" value={this.props.multiplier} />
          </div>
          <p>{this.state.conditionFields ? 'Conditions' : null}</p>
          {this.state.conditionFields}
          <button onClick={this.props.addCondition} 
          data-stat-index={this.props.statIndex}>New Condition</button>
        </div>
        <div className="stats-icon">
          <span role="img" aria-label="delete" onClick={this.props.removeStat}
          data-stat-index={this.props.statIndex}>🗑️</span>
        </div>
      </div>  
    );
  }
}

export class LeagueSettingsScoring extends React.Component {
  constructor(props) {
    super(props);
    this.state = {message: null, error: null, redirect: false,
      updateNeeded: false, form: null};
    this.scoringSettings = [];
    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.addStat = this.addStat.bind(this);
    this.removeStat = this.removeStat.bind(this);
    this.addCondition = this.addCondition.bind(this);
    this.removeCondition = this.removeCondition.bind(this);
  }
  handleInputChange(event) {
    const target = event.target;
    const statIndex = target.dataset.statIndex;
    const statField = target.dataset.statField;
    const conditionIndex = target.dataset.conditionIndex;
    const conditionField = target.dataset.conditionField;
    const value = target.value;
    if (conditionIndex) {
      (this.scoringSettings[statIndex][statField][conditionIndex][conditionField] 
        = value);
      this.setState({
        updateNeeded: true  
      });
    }
    else {
      this.scoringSettings[statIndex][statField] = value;
      this.setState({
        updateNeeded: true  
      });
    }
  }
  handleSubmit(event) {
    event.preventDefault();
    let options = requestOptions('PATCH');
    options.body = {'property': 'scoring_settings', 'data': 
      this.scoringSettings};
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
            this.scoringSettings = result.scoring_settings;
            this.setState({
              updateNeeded: true
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
  addStat(event) {
    event.preventDefault();
    this.scoringSettings.push({'name':'', 'table':'', 'column':'', 
      'conditions':[], 'multiplier':0});
    this.setState({
      updateNeeded: true  
    });
  }
  removeStat(event) {
    event.preventDefault();
    const statIndex = event.target.dataset.statIndex;
    this.scoringSettings.splice(statIndex, 1);
    this.setState({
      updateNeeded: true  
    });
  }
  addCondition(event) {
    event.preventDefault();
    const statIndex = event.target.dataset.statIndex;
    this.scoringSettings[statIndex]['conditions'].push({'table':'', 'column':'', 
      'comparison':'', 'value':0});
    this.setState({
      updateNeeded: true
    });
  }
  removeCondition(event) {
    const statIndex = event.target.dataset.statIndex;
    const conditionIndex = event.target.dataset.conditionIndex;
    this.scoringSettings[statIndex]['conditions'].splice(conditionIndex, 1);
    this.setState({
      updateNeeded: true
    });
  }
  buildForm() {
    let form = [];
    for (let statIndex = 0; statIndex < this.scoringSettings.length; statIndex++) {
      const thisStat = this.scoringSettings[statIndex];
      form.push(
        // this key value ensures updates made to the conditions cause a re-render
        <StatFields key={'' + statIndex + thisStat.conditions.length} 
        statIndex={statIndex} onChange={this.handleInputChange} 
        name={thisStat.name} table={thisStat.table} 
        column={thisStat.column} multiplier={thisStat.multiplier} 
        conditions={thisStat.conditions} addCondition={this.addCondition}
        removeCondition={this.removeCondition} removeStat={this.removeStat} />
      );
    }
    return form;
  }
  componentDidUpdate() {
    if (this.state.updateNeeded) {
      this.setState({
        form: this.buildForm(),
        updateNeeded: false
      });
    }
  }
  render() {
    if (this.state.redirect) {
      return <Redirect to='/league/settings' />;
    }
    return (
      <React.Fragment>
      <LeagueHeader />
      <p className="title">Update Scoring Settings</p>
      <div className="form-message">{this.state.message}</div>
      <form className="default-form" onSubmit={this.handleSubmit}>
        {this.state.form}
        <button onClick={this.addStat}>Add New Stat</button>
        <input type="submit" value="Update" />
      </form>
      {this.state.error && <Error message={this.state.error} />}
      </React.Fragment>
    );
  }
}