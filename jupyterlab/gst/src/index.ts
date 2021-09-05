import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";

import { ICommandPalette } from "@jupyterlab/apputils";
// import { MainAreaWidget } from "@jupyterlab/apputils";

import { ILauncher } from "@jupyterlab/launcher";
import { IMainMenu } from "@jupyterlab/mainmenu";
import { ISettingRegistry } from "@jupyterlab/settingregistry";

import { LabIcon } from "@jupyterlab/ui-components";

import { TerminalManager } from "@jupyterlab/services";
import { Terminal } from "@jupyterlab/terminal";

import appStr from "../style/terminal.svg";

import { ITerminalSettingsInterface } from "./interfaces";

const CATEGORY = "Gamestonk Terminal";

/**
 * The command IDs used by the Gamestonk Terminal Launcher plugin.
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
function getSectionState({ section, s }: { section: string; s: any }): any {
  const values: Array<Record<string, unknown>> = [];
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
  return values;
}

/**
 * Initialization data for the Gamestonk Terminal Launcher extension.
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
        args["isPalette"] ? "New Gamestonk Terminal" : "Gamestonk Terminal",
      caption: "New Gamestonk Terminal",
      icon: (args) => (args["isPalette"] ? null : icon),
      execute: async () => {
        const appSettings = getSectionState({ section: "APP_SETTINGS", s: s });
        const featureFlags = getSectionState({
          section: "FEATURE_FLAGS",
          s: s,
        });
        const apiKeys = getSectionState({ section: "API_KEYS", s: s });

        /**
         * @param root0
         * @param root0.launchCommand
         * @param root0.settingsArray
         */
        function appendLaunchCommand({
          launchCommand,
          settingsArray,
        }: {
          launchCommand: string;
          settingsArray: any;
        }): string {
          for (const setting of settingsArray) {
            var settingValue: string =
              setting.value.value === ""
                ? setting.value.default
                : setting.value.value;
            if (setting.value.type === "bool" && settingValue !== undefined) {
              settingValue = String(settingValue)[0].toUpperCase() + String(settingValue).slice(1);
            };
            launchCommand = `${launchCommand}${settingValue}\n`;
          }
          return launchCommand;
        }

        let launchCommand =
          " source GamestonkTerminal/jupyterlab/scripts/terminal_env.sh\n";

        launchCommand = appendLaunchCommand({
          launchCommand: launchCommand,
          settingsArray: appSettings,
        });
        launchCommand = appendLaunchCommand({
          launchCommand: launchCommand,
          settingsArray: featureFlags,
        });
        launchCommand = appendLaunchCommand({
          launchCommand: launchCommand,
          settingsArray: apiKeys,
        });

        const manager = new TerminalManager();
        const session = await manager.startNew();
        const terminal = new Terminal(session, { theme: "dark" });
        terminal.title.closable = true;

        const customPython: string = "GamestonkTerminal/venv/bin/python";
        // const customPython: ITerminalSettingsInterface = appSettings.find(
        //   (i: ITerminalSettingsInterface) => i.key === "CUSTOM_PYTHON"
        // );
        const terminalPath: ITerminalSettingsInterface = appSettings.find(
          (i: ITerminalSettingsInterface) => i.key === "TERMINAL_PATH"
        );

        launchCommand = `${launchCommand}${customPython} ${terminalPath.value.value}\n`;

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
    console.log("Added Gamestonk Terminal Launcher Exstension.");
  },
};

export default extension;
