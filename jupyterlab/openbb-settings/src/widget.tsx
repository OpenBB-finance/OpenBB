import { ReactWidget } from "@jupyterlab/apputils";
import { ISettingRegistry } from "@jupyterlab/settingregistry";
import FormInput from "./components/FormInput";

/**
 * OpenBB Terminal Settings Menu
 *
 * @class GamestonkTerminalSettingsComponent (name)
 * @param {} root0 - s: Settings object
 * @param {} root0.s - s: Accessible settings object
 * @returns {} JSX.Element Settings form component
 */
export function GamestonkTerminalSettingsComponent({ s }: any): JSX.Element {
  /**
   * Get the section settings values.
   *
   * The section settings are taken from the user space (`s.user` if section keys
   * exist there) or from the default values of the settings schema.
   *
   * @param  section  The section name
   * @returns   The state of the section settings.
   */
  function getSectionState(section: string): Record<string, unknown>[] {
    const values: Array<Record<string, unknown>> = [];
    Object.keys(s.schema.properties[section].default).forEach((element) => {
      const settingsValue =
        typeof s.user[section] === "undefined"
          ? s.schema.properties[section].default[element]
          : s.user[section][element];
      values.push({
        key: element,
        value: settingsValue,
      });
    });
    return values;
  }

  const featureFlags = getSectionState("FEATURE_FLAGS");
  const appSettings = getSectionState("APP_SETTINGS");
  const apiKeys = getSectionState("API_KEYS");

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
   * @param event - Update button click event
   */
  function handleSubmit(event: any) {
    event.preventDefault();

    const featureFlagsObject = {} as any;
    featureFlags.forEach((flag: any) => {
      featureFlagsObject[flag.key] = flag["value"];
    });
    s.set("FEATURE_FLAGS", featureFlagsObject);

    const apiKeysObject = {} as any;
    apiKeys.forEach((apiKey: any) => {
      apiKeysObject[apiKey.key] = apiKey["value"];
    });
    s.set("API_KEYS", apiKeysObject);

    const appSettingsObject = {} as any;
    appSettings.forEach((appSetting: any) => {
      appSettingsObject[appSetting.key] = appSetting["value"];
    });
    s.set("APP_SETTINGS", appSettingsObject);

    alert("Settings updated.");
  }

  return (
    <div className="gamestonkSettings">
      <div className="settingsForm">
        <form>
          <fieldset id="featureFlags">
            <p className="settingsSectionLabel">Feature Flags</p>
            <div className="fieldSetData">
              {featureFlags.map((item: any, index: any) => (
                <FormInput
                  key={index}
                  itemParent={item}
                  index={index}
                  onChangeParent={onFeatureFlagsChange}
                />
              ))}
            </div>
            <div className="container">
              <div className="center">
                <button
                  className="settingsSectionButton"
                  onClick={handleSubmit}
                >
                  Update Flags
                </button>
              </div>
            </div>
          </fieldset>
        </form>
        <br />
        <br />

        <form onSubmit={handleSubmit}>
          <fieldset id="appSettings">
            <p className="settingsSectionLabel">Configurations</p>
            <div className="fieldSetData">
              {appSettings.map((item: any, index: any) => (
                <FormInput
                  key={index}
                  itemParent={item}
                  index={index}
                  onChangeParent={onAppSettingsChange}
                />
              ))}
            </div>
            <div className="container">
              <div className="center">
                <button
                  className="settingsSectionButton"
                  onClick={handleSubmit}
                >
                  Update Configurations
                </button>
              </div>
            </div>
          </fieldset>
        </form>
        <br />
        <br />

        <form onSubmit={handleSubmit}>
          <fieldset id="apiKeys">
            <p className="settingsSectionLabel">API keys</p>
            <div className="fieldSetData">
              {apiKeys.map((item: any, index: any) => (
                <FormInput
                  key={index}
                  itemParent={item}
                  index={index}
                  onChangeParent={onApiKeysChange}
                />
              ))}
            </div>
            <div className="container">
              <div className="center">
                <button
                  className="settingsSectionButton"
                  onClick={handleSubmit}
                >
                  Update API keys
                </button>
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
    this.addClass("gamestonkSettingsWidget");
    this.s = s;
  }

  render(): JSX.Element {
    return <GamestonkTerminalSettingsComponent s={this.s} />;
  }
}
