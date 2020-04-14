import numpy as np
import pandas as pd
import pickle
from collections import Counter
from sklearn import svm, neighbors
from sklearn.model_selection import train_test_split
from sklearn.ensemble import VotingClassifier, RandomForestClassifier

def process_data_for_labels( ticker ) :
    hm_days = 7
    df      = pd.read_csv( 'sp500_joined_closes.csv', index_col = 0 )
    tickers = df.columns.values.tolist()
    df.fillna( 0, inplace = True )

    for i in range( 1, hm_days + 1 ) :
        df[ '{}_{}d'.format( ticker, i ) ] = ( df[ ticker ].shift( -i )  - df[ ticker ] ) / df[ ticker ]

    df.fillna( 0, inplace = True )
    return tickers, df

def buy_sell_hold( *args ) :
    cols = [ c for c in args ]
    requirements = 0.02
    for col in cols :
        if col > requirements :
            return 1
        if col < -requirements :
            return -1
    return 0

def extract_featureset( ticker ) :
    tickers, df = process_data_for_labels( ticker )
    df[ '{}_target'.format( ticker ) ] = list( map( buy_sell_hold, 
                                                    df[ '{}_1d'.format( ticker ) ],
                                                    df[ '{}_2d'.format( ticker ) ],
                                                    df[ '{}_3d'.format( ticker ) ],
                                                    df[ '{}_4d'.format( ticker ) ],
                                                    df[ '{}_5d'.format( ticker ) ],
                                                    df[ '{}_6d'.format( ticker ) ],
                                                    df[ '{}_7d'.format( ticker ) ] ) )
    vals = df[ '{}_target'.format( ticker ) ].values.tolist()
    str_vals = [ str(i) for i in vals ]
    print( 'Data spread:', Counter( str_vals ) )
    df.fillna( 0, inplace = True )

    df = df.replace( [ np.inf, -np.inf ], np.nan )
    df.dropna( inplace = True )

    df_vals = df[ [ ticker for ticker in tickers ] ].pct_change()
    df_vals = df_vals.replace( [np.inf, -np.inf], 0 )
    df_vals.fillna( 0, inplace = True )
    X = df_vals.values
    Y = df[ '{}_target'.format(ticker) ].values
    return X, Y, df

def do_ml( ticker ) :
    X, Y, df = extract_featureset( ticker )
    X_train, X_test, Y_train, Y_test = train_test_split( X, Y, test_size = 0.25 )
    #clf = neighbors.KNeighborsClassifier()
    clf = VotingClassifier([ ( 'lsvc', svm.LinearSVC() ),
        ( 'knn', neighbors.KNeighborsClassifier() ), 
        ( 'rfor', RandomForestClassifier() )])
    clf.fit( X_train, Y_train )
    confidence = clf.score( X_test, Y_test )
    print( 'Accuracy:', confidence )
    predictions = clf.predict( X_test )
    print( 'Predicted Spread:', Counter( predictions ) )
    return confidence

do_ml( 'BAC' )

