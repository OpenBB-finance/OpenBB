# Gamestonk Terminal Web

> Warning: It works, but a few things are still broken like graphs. See the TODO section for what works and what doesn't.

## Running it

Clone the repo, go into the cloned directory, do `chmod +x ./launch`, and then run the launch script with `./launch` (you may need to do `sudo ./launch`, depending on how Docker is set up). You can set API keys my modifying the `setenv` file as documented [here](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/DOCKER_ADVANCED.md#environment-variables). The launch script will automatically create it if it doesn't exist.

You can then view the web UI at `http://host-ip:8080` or `http://localhost:8080` if it's running on your local computer.

## TODO

- [X] Terminal output works.
- [X] Pick a font that supports required characters (emojis, box-drawing characters, etc.) - I chose Consolas. Other ones, like Fira Code, don't usually come pre-installed on machines, so those are less ideal. Consolas is a reasonable tradeoff of looks-good, has the right Unicode characters, widely-supported, and reasonably-liked. If you have a different idea, feel free to ping me @CoconutMacaroon on Discord (I'm in the main Gamestonk Terminal Discord server).
- [X] API keys - Done, set them in the `setenv` file as documented [here](https://github.com/OpenBB-finance/OpenBBTerminal/blob/main/DOCKER_ADVANCED.md#environment-variables).
- [ ] Graphs - There are so many options - you can [plot them in the terminal](https://stackoverflow.com/q/37288421/), use a [web-based VNC client](https://stackoverflow.com/q/3240633/), and there are many other options. Still looking into this. Graphs don't currently work.
- [ ] Prompt emoji is broken - I don't know why, but I will replace it with one that does work once [this issue](https://github.com/OpenBB-finance/OpenBBTerminal/issues/1244) is done.
