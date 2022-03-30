# PRESETS

- [How to add presets](#how-to-add-presets)
- [template](#template)

---

## How to add Presets

1. Go to the folder OpenBBTerminal/openbb_terminal/options/presets.

2. There should be a `README.md` file and multiple `.ini` files. One of these `.ini` files should be named `template.ini`.

   <img width="470" alt="Image1" src="https://user-images.githubusercontent.com/25267873/123706416-2be7be80-d860-11eb-9255-58787e264f49.png">

3. Copy the `template.ini` file and paste it in the same directory.
4. Rename that file to something you find meaningful, e.g. `my_own_filter.ini`.

   <img width="450" alt="Image2" src="https://user-images.githubusercontent.com/25267873/123706424-2db18200-d860-11eb-9523-e4647a073645.png">

5. Open the file you just renamed (e.g. `my_own_filter.ini`), and set the parameters you want to filter.

   <img width="472" alt="Image3" src="https://user-images.githubusercontent.com/25267873/123706427-2e4a1880-d860-11eb-8523-24654013d3e4.png">

6. It may be useful to play with the main source <https://ops.syncretism.io> since you can tweak these and understand
   how they influence the outcome of the filtered stocks.

   <img width="1036" alt="Image4" src="https://user-images.githubusercontent.com/25267873/123708702-c85f9000-d863-11eb-835e-13ea07e45e04.png">

7. Update the Author and Description name. E.g.

   <img width="462" alt="Image5" src="https://user-images.githubusercontent.com/25267873/123711451-6b1a0d80-d868-11eb-9887-3389bbff6514.png">

8. Start the terminal, and go to the `> op` menu. In there, you can play with it on the terminal as shown:

   - **disp**: Allows to see the screeners available. I.e. all `.ini` files in presets folder.
   - **disp <selected_preset>**: Allows to see the specific parameters set for the preset selected.
   - **scr <selected_preset>**: Allows to show stocks that are filtered using the selected preset.
     - Note: As default, if the user does **scr** this will use the `template.ini` file. So, the user can do some tests
       with tweaking of parameters on the `template.ini` file.

   <img width="1220" alt="Image6" src="https://user-images.githubusercontent.com/25267873/123711622-aa485e80-d868-11eb-8c9f-ed9e6453632b.png">

9. Share with other Apes. You can do so by either creating yourself a Pull Request with this change, or asking a dev
   (e.g. @Sexy_Year) on our discord server to add it for you.

---

## template

- **Author of preset:** OpenBBTerminal
- **Contact:** <https://github.com/OpenBB-finance/OpenBBTerminal>
- **Description:** Template with all available filters and their options menu. More information can be found in <https://ops.syncretism.io/index.html>.

---
