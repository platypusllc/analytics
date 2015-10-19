#!/usr/bin/env python
"""
Module for handling database interactions.
Copyright 2015. Platypus LLC. All rights reserved.
"""
import argparse
import gridfs
import logging
import mongoengine
import pandas
import pymongo
from . import logs
from bson.objectid import ObjectId
from pymongo.cursor import CursorType

logger = logging.getLogger(__name__)


def process(db, dataset_id):
    """
    Processes a dataset and uploads the processed data to a MongoDB database.

    :param db: connection to the database to use
    :type  db: pymongo.Database
    :param dataset_id: reference to the dataset that should be processed
    :type  dataset_id: str (MongoDB ObjectID)
    """
    # Open GridFS connection to the Meteor cfs-gridfs collection.
    fs = gridfs.GridFS(db, 'cfs_gridfs.logs_gridfs')

    # Retrieve the dataset document from MongoDB.
    datasets = db['datasets']
    dataset = datasets.find_one(dataset_id)
    if dataset is None:
        raise ValueError("Invalid or unknown dataset ID '{:s}'."
                         .format(dataset_id))

    # Load the data from the logs in this dataset.
    data = {}
    for log_id in dataset['logs']:

        # Get the filerecord for this log from the DB.
        log_record = db['cfs.logs.filerecord'].find_one(log_id)

        # Attempt to load the log content from any available sources.
        log_content = None
        if 'logs_gridfs' in log_record['copies']:
            # Retrieve the data from GridFS.
            log_id = ObjectId(log_record['copies']['logs_gridfs']['key'])
            log_cursor = fs.find_one(log_id)
            log_content = log_cursor.read().splitlines()

        elif 'logs_s3' in log_record['copies']:
            # Retrieve the log file from Amazon S3.
            # TODO: implement this.
            pass

        # Fail if none of the data sources were interpretable.
        if not log_content:
            raise ValueError("Invalid or unknown logfile sources for '{:s}'."
                             .format(dataset_id))

        # Append the data from all of the logs together.
        log_data = logs.read(log_content,
                             filename=log_record['original']['name'])
        for k, v in log_data.iteritems():
            if k in data:
                data[k] = pandas.concat(data[k], v)
            else:
                data[k] = v

    # Compute the bounding region for this dataset.
    # TODO: finish this.
    dataset.region = None

    # Mark processing as complete and save results.
    dataset.processed = 1.0
    dataset.save()


def server(host='mongodb://localhost:27017',
           database='meteor'):
    """
    Database processing server that processes unprocessed logs.

    :param host: a mongodb:// URI for the database server
    :type  host: str
    :param database: the name of the database to use within the server
    :type  database: str
    """

    # Create a connection to the database.
    c = pymongo.MongoClient(host=host)
    mongoengine.connect(database, host=host)
    ns = '{:s}.datasets'.format(database)

    # Tail oplog to get updates.
    oplog = c.local.oplog.rs
    logger.info("Dataset processing server started.")

    # Find current timestamp in oplog.
    first = next(oplog.find().sort('$natural', pymongo.DESCENDING).limit(-1))
    ts = first['ts']

    # Stream remaining elements in oplog.
    while True:
        # Find 'update' events in the specified namespace newer than timestamp.
        # TODO: handle insert events as well.
        cursor = oplog.find({'ts': {'$gt': ts}, 'ns': ns, 'op': 'u'},
                            cursor_type=CursorType.TAILABLE_AWAIT,
                            oplog_replay=True)
        while cursor.alive:
            for doc in cursor:
                logger.info("Processing dataset '{:s}'"
                            .format(doc['o2']['_id']))

                # Process dataset and put results in MongoDB.
                process(c[database], doc['o2']['_id'])

                # Update latest oplog timestamp.
                ts = doc['ts']


def server_script():
    """
    Database processing server that processes unprocessed logs.

    This is a command-line script that wraps the `server()` method.
    """
    parser = argparse.ArgumentParser(
        description='Process datasets and upload results to MongoDB.')
    parser.add_argument('-h', '--host', type=str,
                        default='mongodb://localhost:27017',
                        help='a mongodb:// URI for the database')
    parser.add_argument('-d', '--database', type=str,
                        default='meteor',
                        help='the MongoDB database name to monitor')
    args = parser.parse_args()

    # Call the internal server method with these arguments.
    server(host=args.host, database=args.database)
