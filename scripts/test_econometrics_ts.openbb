econometrics
load longley ll
load longley ll2
options
options ll
show ll
index ll year
plot pop-ll
clean ll -f cfill
clean ll -d rdrop
type
type year-ll category
desc ll
modify -a emp_ratio-ll totemp-ll div pop-ll
modify -d totemp-ll
index ll2 year
modify -c ll totemp-ll2
modify -r ll totemp_ll2 totemp
remove ll2
ols totemp-ll gnpdefl-ll gnp-ll unemp-ll armed-ll pop-ll year-ll
norm totemp-ll
root unemp-ll
dwat -p
bgod
granger gnp-ll pop-ll
coint totemp-ll gnpdefl-ll gnp-ll unemp-ll armed-ll pop-ll year-ll
