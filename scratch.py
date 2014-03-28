import ffa.report
import ffa.football_players
import ffa.config
import ffa.draft


def main():
    clark = SuperMan()

    info = ffa.config.State()
    oDatabase = ffa.football_players.Database(info)
    oDatabase.set_to_draft()
    oDatabase.plot_position_points()

    draft = ffa.draft.Simulator(info.oLeague, oDatabase.df)
    draft.live_draft()
    print oDatabase.df
    print draft.oResults.df.sort('pick')

#    tmp = ffa.report.ReportGen(info, oDatabase.df, draft.oResults)

#    tmp.update_pages()
#    tmp.close_pages()

    print 'do i get here'


class SuperHero(object):

    # This is a parent class (this class can but should not be called often)
    print 'Do I get here?'

    def __init__(self):
        'this will not get automatically called!'

        print 'Set Type of Character'
        self.type = 'Good Guy'

    def _setup(self):
        print 'Standup Good Guy'
        self.type = 'Good Guy Classic'


class SuperMan(SuperHero):

    # THIS IS THE SUB-CLASS! - Call this class instead of SuperHero (typically)
    def __init__(self):

        # THIS OVER-WRITES PARENT (SUPERHERO) INIT FILE
        print 'Set Super Hero Name'
        self.name = 'SuperMan'

        SuperHero.__init__(self)
        self._setup()

    def pass_opt_var(self, a='', b=1, c='yes'):

        print 'a=', str(a), 'b=', str(b), 'c=', str(c), '\n'

if __name__ == "__main__":

    main()