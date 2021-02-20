import argparse
from alpha_vantage.sectorperformance import SectorPerformances
import config_terminal as cfg
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------- SECTORS ----------------------------------------------------
def sectors(l_args):
    parser = argparse.ArgumentParser(prog='sectors', 
                                     description='''Real-time and historical sector performances calculated from S&P500 incumbents.
                                     Pops plot in terminal. [Source: Alpha Vantage]''')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    sp = SectorPerformances(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    df_sectors, d_meta_data = sp.get_sector()
    df_sectors['Rank A: Real-Time Performance'].plot(kind='bar')
    plt.title('Real Time Performance (%) per Sector')
    plt.tight_layout()
    plt.grid()
    plt.show()
    print("")
