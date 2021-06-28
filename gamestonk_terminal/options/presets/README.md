# PRESETS

* [How to add presets](#how-to-add-presets)
* [template](#template)

---

## How to add Presets

1. Go to the folder GamestonkTerminal/gamestonk_terminal/options/presets. 

2. There should be a `README.md` file and multiple `.ini` files. One of these `.ini` files should be named `template.ini`.

<img width="470" alt="Captura de ecrã 2021-06-28, às 22 00 14" src="https://user-images.githubusercontent.com/25267873/123706416-2be7be80-d860-11eb-9255-58787e264f49.png">

3. Copy the `template.ini` file and paste it in the same directory.
4. Rename that file to something you find meaningful, e.g. `my_own_filter.ini`.

<img width="450" alt="Captura de ecrã 2021-06-28, às 22 04 27" src="https://user-images.githubusercontent.com/25267873/123706424-2db18200-d860-11eb-9523-e4647a073645.png">

5. Open the file you just renamed (e.g. `my_own_filter.ini`), and set the parameters you want to filter. 

<img width="472" alt="Captura de ecrã 2021-06-28, às 22 08 16" src="https://user-images.githubusercontent.com/25267873/123706427-2e4a1880-d860-11eb-8523-24654013d3e4.png">

6. It may be useful to play with the main source https://ops.syncretism.io since you can tweak these and understand how they influence the outcome of the filtered stocks. 

<img width="1036" alt="Captura de ecrã 2021-06-28, às 22 53 13" src="https://user-images.githubusercontent.com/25267873/123708702-c85f9000-d863-11eb-835e-13ea07e45e04.png">

Then you can play with it on the terminal as shown:
* **disp**: Allows to see the screeners available. I.e. all `.ini` files in presets folder.
* **disp <selected_preset>**: Allows to see the specific parameters set for the preset selected.
* **scr <selected_preset>**: Allows to show stocks that are filtered using the selected preset.
  * Note: As default, if the user does **scr** this will use the `template.ini` file. So, the user can do some tests with teaking of parameters on the `template.ini` file.

<img width="1218" alt="Captura de ecrã 2021-06-28, às 22 10 25" src="https://user-images.githubusercontent.com/25267873/123706431-2f7b4580-d860-11eb-9074-efa96278d241.png">


---

## template

* **Author of preset:** GamestonkTerminal
* **Contact:** https://github.com/DidierRLopes/GamestonkTerminal#contacts
* **Description:** Template with all available filters and their options menu. More information can be found in https://ops.syncretism.io/index.html.

---
