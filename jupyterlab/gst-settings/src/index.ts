import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from "@jupyterlab/application";

import { ICommandPalette } from "@jupyterlab/apputils";
import { MainAreaWidget } from "@jupyterlab/apputils";

import { ILauncher } from "@jupyterlab/launcher";
import { ISettingRegistry } from "@jupyterlab/settingregistry";

import { IMainMenu } from "@jupyterlab/mainmenu";

import { LabIcon } from "@jupyterlab/ui-components";
import svgIconStr from "../style/settings-icon.svg";

import { TerminalSettingsWidget } from "./widget";

const CATEGORY = "Gamestonk Terminal";

/**
 * The command IDs used by the Gamestonk Settings plugin.
 */
namespace CommandIDs {
  export const create = "gamestonk:settings";
}

/**
 * Initialization data for the Gamestonk Settings extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: "gst:settings",
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
      name: "launcher:gst-settings-icon",
      svgstr: svgIconStr,
    });

    const s = await settings.load("@gamestonk/settings:settings");

    commands.addCommand(command, {
      caption: "Edit Gamestonk Terminal Settings",
      label: "Settings",
      icon: (args) => (args["isPalette"] ? null : icon),
      execute: () => {
        const content = new TerminalSettingsWidget(s);
        const widget = new MainAreaWidget<TerminalSettingsWidget>({ content });
        widget.title.label = "Gamestonk Settings";
        widget.title.icon = icon;
        app.shell.add(widget, "main", { activate: true, mode: "split-right" });
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
    console.log("Added Gamestonk Settings Extension.");
  },
};

export default extension;
