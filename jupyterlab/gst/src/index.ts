import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { TerminalManager } from '@jupyterlab/services';
import { Terminal } from '@jupyterlab/terminal';

import { ILauncher } from '@jupyterlab/launcher';

import { IFileBrowserFactory } from '@jupyterlab/filebrowser';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { LabIcon } from '@jupyterlab/ui-components';

import svgIconStr from '../style/icon_64x64.svg';

const CATEGORY = 'Gamestonk Terminal';

namespace CommandIDs {
  export const launchGamestonkTerminal = 'gamestonk:terminal';
}

const extension: JupyterFrontEndPlugin<void> = {
  id: 'gst:launcher',
  autoStart: true,
  requires: [IFileBrowserFactory],
  optional: [ILauncher, IMainMenu, ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    browserFactory: IFileBrowserFactory,
    launcher: ILauncher | null,
    menu: IMainMenu | null,
    palette: ICommandPalette | null
  ) => {
    const { commands } = app;
    const command = CommandIDs.launchGamestonkTerminal;
    const icon = new LabIcon({
      name: 'launcher:gst-terminal-icon',
      svgstr: svgIconStr,
    });

    commands.addCommand(command, {
      label: (args) => (args['isPalette'] ? 'New Terminal Tab' : 'Gamestonk Terminal'),
      caption: 'Launch a new Gamestonk Terminal tab',
      icon: (args) => (args['isPalette'] ? undefined : icon),
      execute: async (args) => {

        const manager = new TerminalManager();
        const session = await manager.startNew();
        const terminal = new Terminal(session, { theme: 'dark' });
        terminal.title.closable = true;;

        session.send({
          type: 'stdin',
          content: [
            'python terminal.py\n',
          ]
        });

        return terminal;
      },
    });

    // Add the command to the launcher
    if (launcher) {
      launcher.add({
        command,
        category: CATEGORY,
        rank: 1,
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
    console.log("Added !");
  },
};

export default extension;