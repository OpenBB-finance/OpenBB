import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { IMainMenu } from "@jupyterlab/mainmenu";

import { LabIcon } from '@jupyterlab/ui-components';

import docsIconStr from '../style/docs.svg';

const CATEGORY = "Gamestonk Terminal";

namespace CommandIDs {
  export const createNew = 'jlab-examples:create-new-python-file';
}

const extension: JupyterFrontEndPlugin<void> = {
  id: 'documentation',
  autoStart: true,
  optional: [ILauncher, ICommandPalette],
  activate: (
    app: JupyterFrontEnd,
    launcher: ILauncher | null,
    menu: IMainMenu | null,
    palette: ICommandPalette | null
  ) => {
    const { commands } = app;
    const command = CommandIDs.createNew;
    const icon = new LabIcon({
      name: 'documentation:docs-icon',
      svgstr: docsIconStr,
    });

    commands.addCommand(command, {
      label: 'Gamestonk Documentation',
      icon: icon,
      execute: (args: any) => {
        window.open(
          'https://gamestonkterminal.github.io/GamestonkTerminal/',
          '_blank'
        );
      },
    });

    // Add the command to the launcher
    if (launcher) {
      launcher.add({
        command,
        category: CATEGORY,
        rank: 3,
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
