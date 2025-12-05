#!/usr/bin/env python
# author markpurcell@ie.ibm.com

import psycopg2
import psycopg2.pool
from contextlib import contextmanager


class PostgresSQLDriver:
    """
    Utility class wrapping postgres connections and functions
    """

    def __init__(self, schema: str):
        """
        Use connection pooling, and rely on environment variables
        PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
        """
        self.schema = schema
        # self.connection = psycopg2.connect()
        # self.connection = psycopg2.pool.SimpleConnectionPool(1, 20)
        self.connection = psycopg2.pool.ThreadedConnectionPool(1, 20)

    def close(self):
        if self.connection:
            self.connection.closeall()

    @contextmanager
    def cursor(self):
        con = self.connection.getconn()
        con.autocommit = True
        cur = None

        try:
            cur = con.cursor()
            yield cur
        finally:
            cur.close()
            self.connection.putconn(con)

    def call_proc(self, procedure, results=True, to_lower=False, params=None):
        """
        Call a stored procedure
        Return: params (which could be modified), row count, array of rows
        """
        count = 0
        data = []

        with self.cursor() as cur:
            cur.execute("SET SCHEMA '{}'".format(self.schema))

            if params:
                cur.callproc(procedure, params)
            else:
                cur.callproc(procedure)

            if results:
                rows = cur.fetchall()

                # Each row will be a dictionary of name value pairs, get the names
                column_names = [desc[0] for desc in cur.description]

                for row in rows:
                    count += 1
                    if to_lower:
                        data.append({k.lower(): v for k, v in zip(column_names, row)})
                    else:
                        data.append({k: v for k, v in zip(column_names, row)})
            else:
                row = cur.fetchone()
                params = row[0]

        return params, count, data
