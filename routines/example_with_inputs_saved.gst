# Select location folder to export data to (if doesn't exist, will be created by default)
export didier_analysis_on_$ARGV[0]

# Go into the stocks context
stocks

# Load a ticker that's given as a first argument of the routine
load $ARGV[0]

# Go into the Sector and Industry analysis
sia

# When filtering by industry peers remove market cap filtering
clear mktcap

# Compare ticker against industry peers regarding their revenues over time
vis re --export jpg

# Filter by large market cap
mktcap Large

# Compare industry peers (with large market cap) regarding their current quick ratio
metric qr --export jpg

# Take these companies to Comparison Analysis menu
ca

# Access these companies historical raw price since 2019
historical -s 2019-01-01 -n --export jpg

# Compute their correlation of price
hcorr -s 2019-01-01 --export jpg

# Compare their income statements for current year
income --export csv

# Go back one menu to the main stocks context
..

# Enter in the Dark Pool short menu
dps

# Shows stock price vs short interest volume 
psi --export jpg,csv

# Go back one menu and go into Behavioural Analysis menu
../ba

# Check interest on google search of covid and quarantine correlated with ticker price
interest -s 2019-01-01 -w covid,quarantine --export interest_with_covid_quarantine.jpg

# Correlate headlines news sentiment with stock price
snews --export jpg

# Check shareholders of company (leave menu, go into Fundamental Analysis command and call command)
../fa/shrs --export csv

# Get SEC filings
../dd/sec --export csv

# Analyst ratings over time
rot --export jpg

# Price targets over time vs stock price
pt --export jpg

# Apply Relative Strength Index to the stock price
../ta/rsi --export jpg

# Get similar companies arccording to Finnhub API
../ca/getfinnhub

# Compare their volume
volume  --export jpg