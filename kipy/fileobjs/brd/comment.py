from .brditem import BrdItem
'''
Classes based on BrdItem for parsing and rendering comments
inside a .brd file.
'''
class Comment(BrdItem):
    keyword = '#'
    _by_keyword = {}

    @classmethod
    def subparse(cls, brdpage, tokens, lineiterator):
        cls.text = [tokens]

    def render(self, linelist):
        linelist.append('# %s' % self.text)
