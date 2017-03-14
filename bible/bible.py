from discord.ext import commands 
from requests import get 
from json import loads 
from collections import OrderedDict
from Cogs.Utils.Discord import makeEmbed


class Scriptures:

    def __init__(self, bot):
        self.bot = bot
        self.bible = 'https://getbible.net/json?scrip={}'
        self.biblePicture = 'http://pacificbible.com/wp/wp-content/uploads/2015/03/holy-bible.png'

    def getBiblePassage(self, passage):
        '''Goes through the getbible api to get a list of applicable bible passages'''
        toRetrieveFrom = self.bible.format(passage)
        data = get(toRetrieveFrom).content
        strData = str(data)
        realData = strData[3:-3] # Takes off some characters that shouldn't be there
        jsonData = loads(realData)
        return jsonData


    @commands.command(aliases=['christianity', 'bible'])
    async def christian(self, *, passage:str):
        '''Gets a passage from the bible
        Usage :: christian luke 14:34
              :: christian luke 14:34-36'''


        # Generate the string that'll be sent to the site
        getString = passage

        # Work out how many different quotes you need to get
        tempPass = passage.split(':')[1]  # Gets the 34-35 from 14:34-35
        if len(tempPass.split('-')) == 2:
            passage = int(tempPass.split('-')[0])
            lastpassage = int(tempPass.split('-')[1])
        else:
            passage = lastpassage = int(tempPass)

        # Actually go get all the data from the site
        bibleData = self.getBiblePassage(getString)

        # Get the nice passages and stuff
        passageReadings = OrderedDict()
        chapterName = bibleData['book'][0]['book_name']
        chapterPassages = bibleData['book'][0]['chapter']
        chapterNumber = bibleData['book'][0]['chapter_nr']
        for i in range(passage, lastpassage + 1):
            passageReadings['{}:{}'.format(chapterNumber, i)] = chapterPassages[str(i)]['verse']

        # Make it into an embed
        em = makeEmbed(values=passageReadings, icon=self.biblePicture, name=chapterName)

        # Boop it to the user
        await self.bot.say('', embed=em)


def setup(bot):
    bot.add_cog(Scriptures(bot))
