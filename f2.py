import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use( 'ggplot' )

#sdt = dt.datetime( 2019, 1, 1 )
#edt = dt.datetime( 2020, 4, 5 )
#
#df  = web.DataReader( 'TSLA', 'yahoo', sdt, edt )
#print( df.head() )
#df.to_csv( 'tesla.csv' )
df = pd.read_csv( 'tesla.csv', parse_dates = True, index_col = 0 )
print( df.head() )

df[ 'Adj Close' ].plot()
plt.show()
