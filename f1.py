import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web

style.use( 'ggplot' )

sdt = dt.datetime( 2020, 4, 3 )
edt = dt.datetime( 2020, 5, 3 )

df  = web.DataReader( 'TSLA', 'yahoo', sdt, edt )
print( df.head() )
