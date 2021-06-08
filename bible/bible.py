from discord import Embed
from discord.ext import commands 
from requests import get 
from json import loads 
from collections import OrderedDict


class Scriptures:

    def __init__(self, bot):
        self.bot = bot
        self.bible = 'https://getbible.net/json?scrip={}'
        self.biblePicture = 'http://pacificbible.com/wp/wp-content/uploads/2015/03/holy-bible.png'

    def getBiblePassage(self, passage):
        '''Goes through the getbible api to get a list of applicable bible passages'''
        toRetrieveFrom = self.bible.format(passage)
        data = get(toRetrieveFrom).text[1:-2]
        return loads(data)

    @commands.command(aliases=['christianity', 'bible'])
    async def christian(self, *, passage:str):
        '''
        Gets a passage from the bible.
        '''

        # Get the passasges into a nice variable setup
        chapter = []
        sPassage = passage.split(' ')
        while True:
            if ':' in sPassage[0]:
                break
            chapter.append(sPassage[0])
            del sPassage[0]

        chapter = ' '.join(chapter)
        passagesVerses = sPassage[0].split(':')
        verse = passagesVerses[0]
        passages = passagesVerses[1].replace(' ','').split('-')
        if len(passages) == 1: passages = passages + passages

        # So from here, luke 14:34-35 is split up as so:
        #     chapter = 'luke'
        #     passages = ['34', '35']

        # Actually go get all the data from the site
        bibleData = self.getBiblePassage(passage)

        # Get the nice passages and stuff
        bookName = bibleData['book'][0]['book_name']
        verses = bibleData['book'][0]['chapter']
        listedVerses = [(i['verse_nr'], i['verse']) for i in verses.values()]
        '''[('34', 'Salt is good'), ('35', 'Beef is bad')]'''

        # Order the list properly
        passageInt = sorted([int(i) for i in passages])
        sortedVerses = []
        i = passageInt[0]
        while i < passageInt[1] + 1:
            q = [w for w in listedVerses if w[0] == str(i)]
            sortedVerses.append(q[0])
            i += 1

        # Embed it
        embeddableDict = OrderedDict()
        for i in sortedVerses:
            embeddableDict[i[0]] = i[1]

        em = Embed()
        em.set_author(name=bookName, icon_url=self.biblePicture)
        for i, o in embeddableDict.items():
            em.add_field(name=i, value=o, inline=False)

        # Boop it to the user
        await self.bot.say(embed=em)


def setup(bot):
    bot.add_cog(Scriptures(bot))
