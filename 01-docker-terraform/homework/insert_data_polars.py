import polars as pl
from time import time
from decouple import config, AutoConfig
from sqlalchemy import create_engine


def create_connection():
    config = AutoConfig(search_path='./')
    user = config('user')
    password = config('password')
    host = config('host')
    port = config('port')
    db = config('db')

    connection = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    return connection

def insert_data(file_name, table_name):
    connection = create_connection()

    # Batch the csv file for reading later
    csv_reader = pl.read_csv_batched(file_name)

    # First chunk should replace existing table
    if_table_exists = "replace"

    # Loop through all csv data
    while (batches := csv_reader.next_batches(1)) is not None:
        load_start = time()
        record_counts = (
            batches[0]
            .write_database(
                table_name=table_name,
                connection=connection,
                engine="adbc",
                if_table_exists=if_table_exists,
            )
        )

        # After the first chunk, we need to append records
        if_table_exists = "append"

        print(
            f"Inserted chunk to table: {table_name} containing {record_counts} records, taking {format(time()-load_start,'.3f')} seconds"
        )

if __name__ == "__main__":
    start_time = time()
    file_name = 'green_tripdata_2019-09.csv'
    table_name ='green_taxi_trips'
    insert_data(file_name, table_name)

    file_name = 'taxi+_zone_lookup.csv'
    table_name ='zones'
    insert_data(file_name, table_name)

    print(f"Total Time Taken: {format(time()-start_time,'.3f')} seconds")
