import argparse
import webbrowser

# ---------------------------------------------------- Simply WallSt ----------------------------------------------------
def simply_wallst(l_args):
    parser = argparse.ArgumentParser(prog='simply_wallst', description='''Simply Wall Street Research. The following industries
                                     are acceptable: any, autombiles, banks, capital-goods, commercial-services, consumer-durables,
                                     consumer-services, diversified-financials, energy, consumer-retailing, food-beverage-tobacco,
                                     healthcare, household, insurance, materials, media, pharmaceuticals-biotech, real-estate, retail,
                                     semiconductors, software, tech, telecom, transportation, and utilities. ''')

    parser.add_argument('-i', "--industry", action="store", dest="s_industry", type=str, default="any", help="Industry type",
                        choices=['any', 'automobiles', 'banks', 'capital-goods', 'commercial-services', 'consumer-durables',
                                 'consumer-services', 'diversified-financials', 'energy', 'consumer-retailing', 
                                 'food-beverage-tobacco', 'healthcare', 'household', 'insurance', 'materials',
                                 'media', 'pharmaceuticals-biotech', 'real-estate', 'retail', 'semiconductors',
                                 'software', 'tech', 'telecom', 'transportation', 'utilities'] )

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    
        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        webbrowser.open(f"https://simplywall.st/stocks/us/{ns_parser.s_industry}?page=1")
        print("")

    except SystemExit:
        print("")
        return