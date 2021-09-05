interface ITerminalSettingsObject {
  default?: string | number;
  description?: string;
  form?: string;
  title?: string;
  type?: string;
  value?: string;
}

export interface ITerminalSettingsInterface {
  key: string;
  value: ITerminalSettingsObject;
}
