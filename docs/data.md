# Data

Since the data for these calculations is gathered from various different sources,
I have decided to implement a database to store the match results for faster calculations.

In order to accomplish this I will periodically need to run an import for match data that will
reach out to various different data sources and import match data.  Once this has been completed
all subsequent calculations will be done from the database.