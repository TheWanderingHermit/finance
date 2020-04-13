import bs4 as bs
import datetime as dt
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

style.use( 'ggplot' )

def save_sp500_tikcer() :
    resp    = requests.get( 'https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=949009265' )
    soup    = bs.BeautifulSoup( resp.text, 'lxml' )
    table   = soup.find( 'table', { 'class' : 'wikitable sortable' } )
    tickers = []
    for row in table.findAll( 'tr' )[ 1: ] :
        ticker = row.findAll( 'td' )[ 0 ].text
        tickers.append( ticker )

    with open( 'sp500tickers.pickle', 'wb' ) as f:
        pickle.dump( tickers, f )
    
    return tickers

#save_sp500_tikcer()

def get_data_from_yahoo( reload_sp500 = False ) :
    if reload_sp500 :
        ticker = save_sp500_tikcer()
    else :
        with open( 'sp500tickers.pickle', 'rb' ) as f :
            tickers = pickle.load( f )
    if not os.path.exists( 'stock_dfs' ) :
        os.makedirs( 'stock_dfs' )
    start = dt.datetime( 2020, 4, 5 )
    end   = dt.date.today()
    for ticker in tickers :
        ticker = ticker.rstrip()
        # hack to download data for symbols with dot
        ticker = ticker.replace( '.', '-' )
        if not os.path.exists( 'stock_dfs/{}.csv'.format( ticker ) ) :
            print( 'Downloading market data for {}'.format( ticker ) )
            df = web.DataReader( ticker, 'yahoo', start, end )
            df.to_csv( 'stock_dfs/{}.csv'.format( ticker ) )
        else :
            print( 'Already have {}'.format( ticker ) )
#get_data_from_yahoo()

def get_data_from_yahoo2() :
    df = pd.read_html( 'https://en.wikipedia.org/w/index.php?title=List_of_S%26P_500_companies&oldid=949009265' )
    tickers = [ x.rstrip() for x in df[0][ 'Symbol' ].values.tolist() ]
    tickers = [ x.replace( '.', '-' ) for x in tickers ]
    if not os.path.exists( 'stock_dfs' ) :
        os.makedirs( 'stock_dfs' )
    start = dt.datetime( 2000, 1, 1 )
    end   = dt.date.today()
    for ticker in tickers :
        try :
            if not os.path.exists( 'stock_dfs/{}.csv'.format( ticker ) ) :
                print( 'Downloading market data for {}'.format( ticker ) )
                df = web.DataReader( ticker, 'yahoo', start, end )
                df.to_csv( 'stock_dfs/{}.csv'.format( ticker ) )
            else :
                print( 'Already have {}'.format( ticker ) )
        except Exception as e :
            print( 'Cannot fetch data for the ticker' )

#get_data_from_yahoo2()

def compile_data() :
    with open( 'sp500tickers.pickle', 'rb' ) as f :
        tickers = pickle.load( f )
    main_df = pd.DataFrame()
    for dirName, subdirList, fileList in os.walk( 'stock_dfs' ) :
        for count, fileName in enumerate( fileList ) :
            df = pd.read_csv( 'stock_dfs/{}'.format( fileName ) )
            df.set_index( 'Date', inplace = True )
            df.rename( columns = { 'Adj Close': fileName.replace( '.csv', '' ) }, inplace = True )
            df.drop( [ 'Open', 'High', 'Low', 'Close', 'Volume'], 1, inplace = True )
            if main_df.empty :
                main_df = df
            else :
                main_df = main_df.join( df, how = 'outer' )
            if count % 10 == 0 :
                print( count )
    print( main_df.head() )
    main_df.to_csv( 'sp500_joined_closes.csv' )

#compile_data()
def visualize_data() :
    df = pd.read_csv( 'sp500_joined_closes.csv' )
    #df[ 'AAPL' ].plot()
    #plt.show()
    df_corr = df.corr()
    print( df_corr.head() )

    data = df_corr.values
    fig = plt.figure()
    ax = fig.add_subplot( 1, 1, 1 )
    heatmap = ax.pcolor( data, cmap = plt.cm.RdYlGn )
    fig.colorbar( heatmap )
    ax.set_xticks( np.arange( data.shape[ 0 ] + 0.5) )
    ax.set_yticks( np.arange( data.shape[ 1 ] + 0.5) )
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax.set_xticklabels( column_labels )
    ax.set_yticklabels( row_labels )
    plt.xticks( rotation = 90 )
    heatmap.set_clim( -1, 1 )
    plt.tight_layout()
    plt.show()

visualize_data()
