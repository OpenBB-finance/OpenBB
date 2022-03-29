import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";

import { ICommandPalette } from "@jupyterlab/apputils";

import { ILauncher } from "@jupyterlab/launcher";
import { IMainMenu } from "@jupyterlab/mainmenu";
import { ISettingRegistry } from "@jupyterlab/settingregistry";

import { LabIcon } from "@jupyterlab/ui-components";

import { TerminalManager } from "@jupyterlab/services";
import { Terminal } from "@jupyterlab/terminal";

import appStr from "../style/terminal.svg";

import { ITerminalSettingsInterface } from "./interfaces";

const CATEGORY = "OpenBB Terminal";

/**
 * The command IDs used by the OpenBB Terminal Launcher plugin.
 */
namespace CommandIDs {
  export const create = "gamestonk:terminal";
}

/**
 * Get the section settings values.
 *
 * The section settings are taken from the user space (`s.user` if section keys
 * exist there) or from the default values of the settings schema.
 *
 * @param section.section
 * @param  section  The section name
 * @param section.s
 * @returns   The state of the section settings.
 */
function getSettingsAsArray({ s }: { s: any }): any {
  const values: Array<Record<string, unknown>> = [];
  for (const section of ["APP_SETTINGS", "FEATURE_FLAGS", "API_KEYS"]) {
    Object.keys(s.schema.properties[section].default).forEach(
      (element: string) => {
        const settingsValue =
          typeof s.user[section] === "undefined"
            ? s.schema.properties[section].default[element]
            : s.user[section][element];
        values.push({
          key: element,
          value: settingsValue,
        });
      }
    );
  }
  return values;
}

/**
 * Initialization data for the OpenBB Terminal Launcher extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: "gamestonk:terminal",
  autoStart: true,
  optional: [ILauncher, IMainMenu, ICommandPalette, ISettingRegistry],
  activate: async (
    app: JupyterFrontEnd,
    launcher: ILauncher | null,
    menu: IMainMenu | null,
    palette: ICommandPalette | null,
    settings: ISettingRegistry
  ) => {
    const { commands } = app;

    const command = CommandIDs.create;
    const icon = new LabIcon({
      name: "gamestonk:terminal",
      svgstr: appStr,
    });

    const s = await settings.load("@gamestonk/settings:settings");

    commands.addCommand(command, {
      label: (args) =>
        args["isPalette"] ? "New OpenBB Terminal" : "OpenBB Terminal",
      caption: "New OpenBB Terminal",
      icon: (args) => (args["isPalette"] ? null : icon),
      execute: async () => {
        const appSettings = getSettingsAsArray({ s: s });
        let settingsAsBashVariablesString = "";

        for (const appSetting of appSettings) {
          settingsAsBashVariablesString = `${settingsAsBashVariablesString} && export ${
            appSetting.key
          }=${
            appSetting.value.value === ""
              ? appSetting.value.default
              : appSetting.value.value
          }`;
        }

        const manager = new TerminalManager();
        const session = await manager.startNew();
        const terminal = new Terminal(session, { theme: "dark" });
        terminal.title.closable = true;

        session.send({
          type: "stdin",
          content: ["clear\n"],
        });

        await new Promise((f) => setTimeout(f, 1000));

        session.send({
          type: "stdin",
          content: [`clear${settingsAsBashVariablesString}\nclear\n`],
        });

        const pythonBinarySetting: ITerminalSettingsInterface = appSettings.find(
          (i: ITerminalSettingsInterface) => i.key === "PYTHON_BINARY"
        );
        const terminalPath: ITerminalSettingsInterface = appSettings.find(
          (i: ITerminalSettingsInterface) => i.key === "TERMINAL_PATH"
        );

        const launchCommand = `${
          pythonBinarySetting.value.value === ""
            ? pythonBinarySetting.value.default
            : pythonBinarySetting.value.value
        } ${
          terminalPath.value.value === ""
            ? terminalPath.value.default
            : terminalPath.value.value
        }\n`;

        session.send({
          type: "stdin",
          content: [launchCommand],
        });
        return terminal;
      },
    });

    if (launcher) {
      launcher.add({
        command,
        category: CATEGORY,
        rank: 2,
      });
    }

    // Add the command to the palette
    if (palette) {
      palette.addItem({
        command,
        args: { isPalette: true },
        category: CATEGORY,
      });
    }

    // Add the command to the menu
    if (menu) {
      menu.fileMenu.newMenu.addGroup([{ command }], 30);
    }
    console.log("Added OpenBB Terminal Launcher Exstension.");
  },
};

export default extension;
