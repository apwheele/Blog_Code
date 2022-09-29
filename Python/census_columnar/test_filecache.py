'''
Example of downloading
and saving the census data
very columnar oriented

Andy Wheeler
'''

import pandas as pd
import duckdb
import os

# my local census functions
# grabbing small area 2019 data
# here defaults to just Texas/Delaware
# still takes a few minutes
import census_funcs
cen2019_small, fields2019 = census_funcs.get_data(year=2019)
print(cen2019_small.shape) # (21868, 17145)

# Save locally to CSV file
cen2019_small.to_csv('census_test.csv')

# Trying zip compression
cen2019_small.to_csv('census_test.csv.zip',compression="zip")

# Save to parquet files
cen2019_small.to_parquet('census.parquet.gzip',compression='gzip',engine='pyarrow')

# Save to DuckDB, should make the DB if does not exist
con = duckdb.connect(database='census.duckdb',read_only=False)
con.execute('CREATE TABLE census_2019 AS SELECT * FROM cen2019_small')

# Lets check out the file sizes
files = ['census_test.csv','census_test.csv.zip',
         'census.parquet.gzip','census.duckdb']

for fi in files:
    file_size = os.path.getsize(fi)
    print(f'File size for {fi} is {file_size/1024**3:,.1f} gigs')

# File size for census_test.csv is 0.8 gigs
# File size for census_test.csv.zip is 0.2 gigs
# File size for census.parquet.gzip is 0.2 gigs
# File size for census.duckdb is 0.7 gigs

# Can add in another table into duckdb
cen2018_small, fields2018 = census_funcs.get_data(year=2018)
con.execute('CREATE TABLE census_2018 AS SELECT * FROM cen2018_small')
con.close()

ducksize = os.path.getsize(files[-1])
print(f'File size for {files[-1]} with two tables is {ducksize/1024**3:,.1f} gigs')
# File size for census.duckdb with two tables is 1.5 gigs

# Now cleaning up the files
for fi in files:
    os.remove(fi)