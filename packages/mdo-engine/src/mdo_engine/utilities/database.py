# -*- coding: utf-8 -*-


import abc
import contextlib
import logging
import socket
from abc import ABC

from sqlalchemy import MetaData, Table, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .misc import safe_update

# Set up logging
module_logger = logging.getLogger(__name__)

# Create and engine and get the metadata
Base = declarative_base()


class Database(ABC):
    def __init__(self, adapter_name, config_dict=None):
        self._adapter = self._init_adapter(adapter_name)
        self._credentials = self._init_credentials()
        self._echo = False
        self._engine = None
        self._meta = None
        self._timeout = None
        self.session = None

        if config_dict is not None:
            self.set_credentials(config_dict)

        return

    @property
    @abc.abstractmethod
    def default_port(self):
        """The default port for connecting to the database"""

        return

    @property
    @abc.abstractmethod
    def default_user_id(self):
        """The default user id for connecting to the database"""

        return

    @property
    @abc.abstractmethod
    def default_password(self):
        """The default password for connecting to the database"""

        return

    @property
    @abc.abstractmethod
    def default_database(self):
        """The default databse name"""

        return

    @property
    @abc.abstractmethod
    def valid_adapters(self):
        """List of valid adapters for the SQL manager"""

        return

    def _init_adapter(self, adapter_name):
        if not self._is_valid_adapter(adapter_name):
            errStr = ("Adapter {} is not valid for this SQL manager.").format(
                adapter_name
            )
            raise ValueError(errStr)

        return adapter_name

    def _init_credentials(self):
        credentials_dict = {
            "host": None,
            "port": None,
            "dbname": None,
            "user": None,
            "pwd": None,
        }

        return credentials_dict

    def set_echo(self, echo):
        self._echo = echo

        return

    def set_timeout(self, timeout):
        self._timeout = timeout

        return

    def set_credentials(self, config_dict):
        self._credentials = safe_update(self._credentials, config_dict)

        return

    def get_credentials(self):
        default_dict = {
            "host": None,
            "port": self.default_port,
            "dbname": self.default_database,
            "user": self.default_user_id,
            "pwd": self.default_password,
        }

        credentials = safe_update(default_dict, self._credentials)

        return credentials

    @abc.abstractmethod
    def get_connection_string(self):
        raise NotImplementedError(
            "This superclass can not be used to generate a connection string."
        )

    def configure(self, engine_args=None, connect_args=None):
        connection_string = self.get_connection_string()

        kwargs = {"echo": self._echo}

        if engine_args is not None:
            kwargs.update(engine_args)

        if connect_args is not None:
            kwargs["connect_args"] = connect_args

        self._engine = create_engine(connection_string, **kwargs)
        self._meta = MetaData()

        Session = sessionmaker(bind=self._engine)
        self.session = Session()

        return

    def reflect_table(self, table_name, remove_trailing_space=True):
        if self._meta is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        # Sanitise the table names if required
        if remove_trailing_space:
            table_name = table_name.rstrip()

        reflected = Table(table_name, self._meta, autoload_with=self._engine)

        return reflected

    def safe_reflect_table(self, table_name):
        """If the table is already in the meta data take that version rather
        than reflecting again."""

        if self._meta is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        meta_name = table_name

        if meta_name in self._meta.tables:
            table = self._meta.tables[meta_name]

        else:
            table = self.reflect_table(table_name)

        return table

    @contextlib.contextmanager
    def exectute_query(self, query):
        if self._engine is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        connection = self._engine.connect()

        try:
            result = connection.execute(text(query))
            yield result

        finally:
            connection.close()

    def execute_transaction(self, query):
        if self._engine is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        # runs a transaction
        with self._engine.begin() as connection:
            connection.execute(query)

        return

    def call_stored_proceedure(self, proceedure_name, proceedure_args):
        """Return the results from calling a stored proceedure. Note this
        is not DB agnostic as not all SQL DBs support stored proceedures."""

        if self._engine is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        connection = self._engine.raw_connection()

        try:
            cursor = connection.cursor()
            cursor.callproc(proceedure_name, proceedure_args)
            results = list(cursor.fetchall())
            cursor.close()
            connection.commit()

        finally:
            connection.close()

        return results

    def close(self):
        if self._engine is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        self._engine.dispose()
        self.session = None

        return

    def _is_valid_adapter(self, adapter_name):
        """Return true if the adapter is valid for the SQL manager."""

        valid_adapters = self.valid_adapters

        result = False

        if adapter_name in valid_adapters:
            result = True

        return result

    def _get_first_entries(self, query_str):
        with self.exectute_query(query_str) as result:
            first_entries = [row[0] for row in result]

        return first_entries

    def __del__(self):
        self.close()


class PostgreSQL(Database):
    def __init__(self, adapter_name, config=None):
        super(PostgreSQL, self).__init__(adapter_name, config)

    @property
    def default_port(self):
        return 5432

    @property
    def default_user_id(self):
        return "postgres"

    @property
    def default_password(self):
        return "postgres"

    @property
    def default_database(self):
        return "postgres"

    @property
    def valid_adapters(self):
        return ["psycopg"]

    def get_connection_string(self):
        credentials = self.get_credentials()

        host = credentials["host"]
        port = credentials["port"]
        uid = credentials["user"]
        pwd = credentials["pwd"]
        db_name = credentials["dbname"]

        hostString = "postgresql+{}://{}:{}@{}:{}".format(
            self._adapter, uid, pwd, host, port
        )

        conn_string = "{}/{}".format(hostString, db_name)

        return conn_string

    def configure(self):
        engine_args = None
        connect_args = None

        if self._timeout is not None:
            engine_args = {"pool_timeout": self._timeout}
            connect_args = {"connect_timeout": self._timeout}

        super(PostgreSQL, self).configure(engine_args, connect_args)

        return

    def reflect_table(
        self,
        table_name,
        schema="public",
        remove_trailing_space=True,
    ):
        if self._meta is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        # Sanitise the table names if required
        if remove_trailing_space:
            table_name = table_name.rstrip()

        kwargs = {"autoload_with": self._engine, "schema": schema}

        reflected = Table(table_name, self._meta, **kwargs)

        return reflected

    def safe_reflect_table(self, table_name, schema="public"):
        """If the table is already in the meta data take that version rather
        than reflecting again."""

        if self._meta is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        meta_name = "{}.{}".format(schema, table_name)

        if meta_name in self._meta.tables:
            table = self._meta.tables[meta_name]

        else:
            table = self.reflect_table(table_name, schema)

        return table

    def drop_columns(self, table_name, column_list, schema="public"):
        table_name = "{}.{}".format(schema, table_name)

        for column_name in column_list:
            query_str = ("ALTER TABLE {} DROP COLUMN " '"{}";').format(
                table_name, column_name
            )
            self.execute_transaction(query_str)

        return

    def get_table_names(self, schema=None):
        query_str = "SELECT table_name FROM information_schema.tables"
        if schema is not None:
            query_str += (" WHERE table_schema = " "'{}'").format(schema)
        query_str += ";"

        table_names = self._get_first_entries(query_str)

        return table_names

    def get_column_names(self, table, schema=None):
        query_str = (
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = '{}'"
        ).format(table)
        if schema is not None:
            query_str += (" AND table_schema = " "'{}'").format(schema)
        query_str += ";"

        column_names = self._get_first_entries(query_str)

        return column_names

    def get_db_names(self):
        query_str = "SELECT datname FROM pg_database;"

        with self.exectute_query(query_str) as result:
            db_names = [row[0] for row in result]

        return db_names

    def has_permission(self, table_name):
        query_str = ("select has_table_privilege('{}','select');").format(table_name)

        with self.exectute_query(query_str) as result:
            permissions = [row[0] for row in result]

        return permissions[0]

    def server_execute_query(
        self,
        query,
        fetch_limit=1000,
        cursor_limit=None,
    ):
        """"""

        if self._engine is None:
            errStr = "No connection has been made."
            raise IOError(errStr)

        # Sanitise the line limit and query string
        safe_fetch_limit = int(fetch_limit)
        new_query = query.strip()

        # Add cursor limit to query if requested and its not already been set
        if cursor_limit is not None and "LIMIT" not in new_query:
            safe_cursor_limit = int(cursor_limit)

            if new_query[-1] == ";":
                new_query = new_query[:-1]
            new_query += " LIMIT {:d};".format(int(safe_cursor_limit))

        connection = self._engine.raw_connection()

        msg = "Executing server side query: {}".format(new_query)
        module_logger.debug(msg)

        try:
            cursor = connection.cursor()
            cursor.execute(new_query)

            results = []

            while True:
                rows = cursor.fetchmany(safe_fetch_limit)
                if not rows:
                    break

                module_logger.debug("Fetched {} rows".format(len(rows)))

                for row in rows:
                    results.append(row)

            cursor.close()
            connection.commit()

        finally:
            connection.close()

        return results


class SQLite(Database):
    def __init__(self):
        super(SQLite, self).__init__(None)

    @property
    def default_port(self):
        return None

    @property
    def default_user_id(self):
        return None

    @property
    def default_password(self):
        return None

    @property
    def default_database(self):
        return ""

    @property
    def valid_adapters(self):
        return [None]

    def set_dbname(self, dbname):
        config_dict = {"dbname": dbname}

        self.set_credentials(config_dict)

        return

    def get_connection_string(self):
        credentials = self.get_credentials()

        db_name = credentials["dbname"]

        host_root = "sqlite://"

        if db_name:
            conn_string = "{}/{}".format(host_root, db_name)

        else:
            conn_string = host_root

        return conn_string

    def get_table_names(self):
        query_str = "SELECT name FROM sqlite_master WHERE type='table'"

        table_names = self._get_first_entries(query_str)

        return table_names


def check_host_port(host_ip, port):
    """Check if a connection can be established to the given host and port."""

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    address_str = "Host: {} Port: {} ".format(host_ip, port)

    try:
        s.connect((host_ip, port))
        result = True
        msg = address_str + "OPEN"

    except socket.error:
        result = False
        msg = address_str + "CLOSED"

    finally:
        s.close()

    return result, msg
