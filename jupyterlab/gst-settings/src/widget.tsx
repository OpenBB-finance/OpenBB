import { ReactWidget } from '@jupyterlab/apputils';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { useState } from 'react';
import FormInput from './components/FormInput';

/**
 * Gamestonk Terminal Settings Menu
 *
 * @class GamestonkTerminalSettingsComponent (name)
 * @param root0 - s: Settings object
 * @param root0.s - s: Accissible settings object
 * @returns - JSX.Element Settings form component
 */
export function GamestonkTerminalSettingsComponent({ s }: any): JSX.Element {
  const getSectionState = (section: string) => {
    const env_values = s.schema.properties;
    const values: any = [];

    Object.keys(env_values[section].default).forEach((element) => {
      values.push({
        key: element,
        value: env_values[section].default[element],
      });
    });
    return values;
  }

  const [featureFlags, setFeatureFlags] = useState(getSectionState("FEATURE_FLAGS"));
  const [appSettings, setAppSettings] = useState(getSectionState("GENERAL"));
  const [apiKeys, setApiKeys] = useState(getSectionState("API_KEYS"));

  const onFeatureFlagsChange = (index: any, item: any) => {
    featureFlags[index] = item;
  };

  const onAppSettingsChange = (index: any, item: any) => {
    appSettings[index] = item;
  };

  const onApiKeysChange = (index: any, item: any) => {
    apiKeys[index] = item;
  };

  /**
   * @param event
   */
  function handleSubmit(event: any) {
    console.log(event);
    event.preventDefault();
    setFeatureFlags(event.target.value);
    setAppSettings(event.target.value);
    setApiKeys(event.target.value);
    // s.set('IEX_KEY', token);
    // s.set('DG_PASSWORD', password);
    alert(featureFlags);
  }

  return (
    <div className="gamestonkSettings">
    <div className="settingsForm">
      <form onSubmit={handleSubmit}>
        <fieldset id="featureFlags">
          <p className="settingsSectionLabel">Feature Flags</p>
          <div className="fieldSetData">
          {featureFlags.map((item: any, index: any) => (
            <FormInput
              itemParent={item}
              index={index}
              onChangeParent={onFeatureFlagsChange}
            />
          ))}
          </div>
          <div className="container">
          <div className="center">
          <button className="settingsSectionButton" onClick={handleSubmit}>Update Flags</button>
            </div>
            </div>
        </fieldset>
      </form>
      <br/>
      <br/>

      <form onSubmit={handleSubmit}>
        <fieldset id="appSettings">
          <p className="settingsSectionLabel">Configurations</p>
          <div className="fieldSetData">
          {appSettings.map((item: any, index: any) => (
            <FormInput
              itemParent={item}
              index={index}
              onChangeParent={onAppSettingsChange}
            />
          ))}
          </div>
          <div className="container">
          <div className="center">
          <button className="settingsSectionButton" onClick={handleSubmit}>Update Configurations</button>
          </div>
          </div>
        </fieldset>
      </form>
      <br/>
      <br/>

      <form onSubmit={handleSubmit}>
        <fieldset id="apiKeys">
          <p className="settingsSectionLabel">API keys</p>
          <div className="fieldSetData">
          {apiKeys.map((item: any, index: any) => (
            <FormInput
              itemParent={item}
              index={index}
              onChangeParent={onApiKeysChange}
            />
          ))}
          </div>
          <div className="container">
          <div className="center">
          <button className="settingsSectionButton" onClick={handleSubmit}>Update API keys</button>
          </div>
          </div>
        </fieldset>
      </form>
    </div>
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
