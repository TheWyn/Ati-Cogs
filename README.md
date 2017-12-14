# Ati-Cogs

bible - Search bible verses.

btcprice - Gives the price of BTC in 22 currencies.

cowsay - Say it with a cow. Or think it with a cow.



### Red v3 install instructions for the music cog:

You will need to modify discord.py for this to work. There is a PR currently open to add the needed line.

Your mileage may vary! This is in alpha and is still being developed. If you run into issues you may need to do a little googling.

- Install Ati-Cogs and install the music cog. You may need to sideload this cog by downloading the zip and placing it in your cogs folder for v3.

- `[p]repo add AtiCogs https://github.com/atiwiex/Ati-Cogs v3`
- `[p]cog install AtiCogs music`

- `pip install lavalink`

- Find your Python lib directory.
- In the lavalink directory, open lavalink.py, and go to line 12. Change the port from 80 to 81.
- In the discord directory, open state.py, and go to line 791.
- Add the line: `self.dispatch('voice_server_update', data)` under the `def parse_voice_server_update(self, data):` line.

- Install Java.
- Get the latest Lavalink jar and server. `https://ci.fredboat.com/viewLog.html?buildId=lastSuccessful&buildTypeId=Lavalink_Build&tab=artifacts&guest=1`
- Place them in a Lavalink folder on your computer.
- Download [application.yml](https://tinyurl.com/yddqwr6z) and place it in the Lavalink folder.
- Run the jar with `java -jar lavalink.jar`
- If configured properly, Lavalink will start running.

- Load the music cog with [p]load music.
- Success!



If you have trouble where bot won't connect to voice or won't play the track because of server connection issues, make sure that the port, the ip, and the password is consistent in all three files:

- /lib/python3.6/site-packages/lavalink, line 12
- /cogs/CogManager/cogs/music, line 11
- lavalink/application.yaml

These directories may be different on your system.


