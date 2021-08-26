import { ReactWidget } from '@jupyterlab/apputils';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { useState } from 'react';
import TextInput from './components/TextInput';

/**
 * Gamestonk Terminal Settings Menu
 *
 * @class GamestonkTerminalSettingsComponent (name)
 * @param root0 - s: Settings object
 * @param root0.s - s: Accissible settings object
 * @returns - JSX.Element Settings form component
 */
export function GamestonkTerminalSettingsComponent({ s }: any): JSX.Element {
  const [token, setToken] = useState(s.get('IEX_KEY').composite as string);
  const [password, setPassword] = useState(
    s.get('DG_PASSWORD').composite as string
  );

  /**
   * handleSubmit
   *
   * @param event - Form submission event
   */
  function handleSubmit(event: any) {
    console.log(event);
    event.preventDefault();
    s.set('IEX_KEY', token);
    s.set('DG_PASSWORD', password);
    alert(token + '\n' + password);
  }

  return (
    <div className="gamestonkSettings">
      <form className="settingsForm" onSubmit={handleSubmit}>
        <fieldset>
          <TextInput name={'token'} value={token} updateFuction={setToken} />
          <label className="settingsLabel" htmlFor="password">
            Password:
          </label>
          <br />
          <input
            type="password"
            id="password-input"
            name="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
            }}
            data-form-required
          />
          <br />
          <br />
          <input type="submit" value="Submit" />
        </fieldset>
      </form>
    </div>
  );
}

/**
 * A Lumino Widget that wraps a GamestonkTerminalSettingsComponent.
 *
 * @class      TerminalSettingsWidget (name)
 */
export class TerminalSettingsWidget extends ReactWidget {
  /**
   * Constructs a new TerminalSettingsWidget.
   */
  s: ISettingRegistry.ISettings;
  constructor(s: ISettingRegistry.ISettings) {
    super();
    this.addClass('gamestonkSettingsWidget');
    this.s = s;
  }

  render(): JSX.Element {
    return <GamestonkTerminalSettingsComponent s={this.s} />;
  }
}
