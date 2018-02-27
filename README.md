# Ati-Cogs

bible - Search bible verses.

btcprice - Gives the price of BTC in 22 currencies.

cowsay - Say it with a cow. Or think it with a cow.



### Red v3 install instructions for the music cog:

- Install Ati-Cogs and install the music cog. You may need to sideload this cog by downloading the zip and placing it in your cogs folder for v3.

- `[p]repo add aticogs https://github.com/atiwiex/Ati-Cogs v3`
- `[p]cog install aticogs music`

- `pip install lavalink==2.0.2.9`

- Install Java.
- Get the latest Lavalink jar and server. https://ci.fredboat.com/viewLog.html?buildId=3005&tab=artifacts&buildTypeId=Lavalink_Build&guest=1
- Place them in a Lavalink folder on your computer, any location that is convenient.
- Download [application.yml](https://tinyurl.com/yddqwr6z) and place it in the Lavalink folder.
- Run the jar with `java -jar lavalink.jar`
- If configured properly, Lavalink will start running.

- Load the music cog with [p]load music.
- Success!


### If you are a current user:

- Thank you for helping to test and give feedback!
- Upgrade Red to the latest beta (beta 7+)
- run `pip install -U lavalink==2.0.2.9`
- Replace your current Lavalink jar files: https://ci.fredboat.com/viewLog.html?buildId=3005&tab=artifacts&buildTypeId=Lavalink_Build&guest=1


New: 

- Raise the playlist limit beyond 600 tracks. Add `youtubePlaylistLoadLimit: 2000` or any other value to your application.yml as the last line, with the same indentation as the previous line.
- Remove songs from the queue with the remove command and the song number.
- Queue bumping. Bump specific songs to the top of the queue using the song number.
- [p]queue now works with a page number.
- Starting to add Red v2 audio features. Audioset notify and audioset status make an appearance (default: off).
- The beginning of fancy audio stats with [p]audiostats.
- No more state.py edit!


Known Bugs:

- Playlist mixes from YouTube will only queue the first song. Playlist lists work fine.
- If shuffle is enabled, [p]queue will list the queue with no shuffle (shuffle track is randomly picked from the existing queue).
- Voice chat disconnects after connecting or the cog hanging at 0:00 is caused by websockets < 4.0
