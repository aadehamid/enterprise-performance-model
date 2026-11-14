import pandas as pd
from typing import Optional
import sqlalchemy
import urllib
import duckdb
import logging
import time
from datetime import datetime
import time
import os
from azure.identity import InteractiveBrowserCredential, DeviceCodeCredential, ChainedTokenCredential
from typing import Tuple, Optional, Union
import polars as pl
from dotenv import load_dotenv
from pathlib import Path

ODBC_DRIVER = os.getenv("SQLSERVER_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")

# Load environment variables
# Load the .env file from the correct location
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=env_path)

def query_sql_server(query, server="sqlsrv-001.lsc.internal", database="lsc_idp", 
                     write_to_duckdb=False, duckdb_table=None, duckdb_path=":memory:",
                     log_level=logging.INFO):
    """
    Execute a SQL query against SQL Server and return results as a DuckDB result object.
    
    Parameters:
    -----------
    query : str
        SQL query to execute
    server : str
        SQL Server address
    database : str
        Database name
    write_to_duckdb : bool
        Whether to write results to a DuckDB database
    duckdb_table : str
        Table name to write results to (required if write_to_duckdb is True)
    duckdb_path : str
        Path to DuckDB database file (default is in-memory database)
    log_level : int
        Logging level (default is logging.INFO)
        
    Returns:
    --------
    DuckDB result object that can be converted to pandas (.df()) or polars (.pl())
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    # Create handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    start_time = time.time()
    logger.info(f"Starting query execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Connecting to server: {server}, database: {database}")
    
    try:
        # Step 1: Create connection to SQL Server using SQLAlchemy
        connection_string = (
            f"DRIVER={{{ODBC_DRIVER}}};SERVER={server};DATABASE={database};"
            "Trusted_Connection=yes;TrustServerCertificate=yes"
        )
        params = urllib.parse.quote_plus(connection_string)
        engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        logger.info("Successfully created SQLAlchemy engine")
        
        # Step 2: Execute query and get pandas DataFrame
        logger.info(f"Executing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        query_start = time.time()
        temp_df = pd.read_sql(query, engine)
        query_time = time.time() - query_start
        logger.info(f"Query executed in {query_time:.2f} seconds, retrieved {len(temp_df)} rows")
        
        # Step 3: Connect to DuckDB
        logger.info(f"Connecting to DuckDB at {duckdb_path}")
        duck_conn = duckdb.connect(duckdb_path)
        
        # Step 4: Register the pandas DataFrame as a view in DuckDB
        logger.info("Registering data in DuckDB")
        duck_conn.register('temp_query_results', temp_df)
        
        # Step 5: Write to DuckDB table if requested
        if write_to_duckdb:
            if duckdb_table is None:
                logger.error("duckdb_table not specified when write_to_duckdb is True")
                raise ValueError("duckdb_table must be specified when write_to_duckdb is True")
            
            logger.info(f"Writing data to DuckDB table: {duckdb_table}")
            write_start = time.time()
            duck_conn.execute(f"CREATE TABLE IF NOT EXISTS {duckdb_table} AS SELECT * FROM temp_query_results")
            write_time = time.time() - write_start
            logger.info(f"Data written to table {duckdb_table} in {write_time:.2f} seconds")
        
        # Step 6: Return DuckDB result object
        logger.info("Preparing result object")
        result = duck_conn.execute("SELECT * FROM temp_query_results")
        
        total_time = time.time() - start_time
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        
        return result
    
    except Exception as e:
        logger.error(f"Error in query_sql_server: {str(e)}", exc_info=True)
        raise


    
def query_sql_server_mfa(
    query: str,
    server: str = "sqlsrv-001.lsc.internal",
    database: str = "lsc_idp",
    write_to_duckdb: bool = False,
    duckdb_table: Optional[str] = None,
    duckdb_path: str = ":memory:",
    log_level: int = logging.INFO
) :
    """
    Execute a SQL query against SQL Server using Microsoft Entra ID with MFA authentication
    and return results as a DuckDB connection and result.
    
    Parameters:
    -----------
    query : str
        SQL query to execute
    server : str
        SQL Server address
    database : str
        Database name
    write_to_duckdb : bool
        Whether to write results to a DuckDB database
    duckdb_table : str, optional
        Table name to write results to (required if write_to_duckdb is True)
    duckdb_path : str
        Path to DuckDB database file (default is in-memory database)
    log_level : int
        Logging level (default is logging.INFO)
        
    Returns:
    --------
    A tuple containing:
    - DuckDB connection with the registered view
    - The query result (which can be used once)
    
    Usage:
    ------
    conn, result = query_sql_server_mfa("SELECT top(3) * FROM dbo._EVENTS")
    pandas_df = result.df()
    # To get polars dataframe, re-execute the query
    polars_df = conn.execute("SELECT * FROM temp_query_results").pl()
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    # Create handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    start_time = time.time()
    logger.info(f"Starting query execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Connecting to server: {server}, database: {database} using Microsoft Entra ID authentication")
    
    try:
        # Create connection string with ActiveDirectoryInteractive authentication
        connection_string = (
            f"DRIVER={{{ODBC_DRIVER}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Authentication=ActiveDirectoryInteractive;"
            f"Encrypt=yes;TrustServerCertificate=no;"
            f"AutoCommit=true;" 
        )
        
        params = urllib.parse.quote_plus(connection_string)
        engine = sqlalchemy.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
        logger.info("Successfully created SQLAlchemy engine with Microsoft Entra ID authentication")
        
        # Execute query and get pandas DataFrame
        logger.info(f"Executing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        query_start = time.time()
        temp_df = pd.read_sql(query, engine)
        query_time = time.time() - query_start
        logger.info(f"Query executed in {query_time:.2f} seconds, retrieved {len(temp_df)} rows")
        
        # Connect to DuckDB
        logger.info(f"Connecting to DuckDB at {duckdb_path}")
        duck_conn = duckdb.connect(duckdb_path)
        
        # Register the pandas DataFrame as a view in DuckDB
        logger.info("Registering data in DuckDB")
        duck_conn.register('temp_query_results', temp_df)
        
        # Write to DuckDB table if requested
        if write_to_duckdb:
            if duckdb_table is None:
                logger.error("duckdb_table not specified when write_to_duckdb is True")
                raise ValueError("duckdb_table must be specified when write_to_duckdb is True")
            
            logger.info(f"Writing data to DuckDB table: {duckdb_table}")
            write_start = time.time()
            duck_conn.execute(f"CREATE TABLE IF NOT EXISTS {duckdb_table} AS SELECT * FROM temp_query_results")
            write_time = time.time() - write_start
            logger.info(f"Data written to table {duckdb_table} in {write_time:.2f} seconds")
        
        # Return DuckDB result object
        logger.info("Preparing result object")
        result = duck_conn.execute("SELECT * FROM temp_query_results")
        
        total_time = time.time() - start_time
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        
        return duck_conn, result
    
    except Exception as e:
        logger.error(f"Error in query_sql_server_mfa: {str(e)}", exc_info=True)
        raise


# get environment varaibales


def get_connection_params(environment="dev"):
    """
    Get connection parameters for a specific environment
    
    Parameters:
    -----------
    environment : str
        The environment to get connection parameters for (dev, qa, prod)
        
    Returns:
    --------
    dict containing server and database parameters
    """
    if environment.lower() == "dev":
        return {
            "server": os.getenv("IDP_DEV_SERVER"),
            "database": os.getenv("IDP_DEV_DB")
        }
    elif environment.lower() == "qa":
        return {
            "server": os.getenv("IDP_QA_SERVER"),
            "database": os.getenv("IDP_QA_DB")
        }
    elif environment.lower() == "prod":
        return {
            "server": os.getenv("IDP_PROD_SERVER"),
            "database": os.getenv("IDP_PROD_DB")
        }
    else:
        raise ValueError(f"Unknown environment: {environment}")

# IDP Connection

def query_sql_server_mfa_idp(
    query: str,
    environment: str = "dev",
    write_to_duckdb: bool = False,
    duckdb_table: Optional[str] = None,
    duckdb_path: str = ":memory:",
    log_level: int = logging.INFO
):
    """
    Execute a SQL query against SQL Server in a specific environment
    using Microsoft Entra ID with MFA authentication
    
    Parameters:
    -----------
    query : str
        SQL query to execute
    environment : str
        Environment to connect to (dev, qa, prod)
    ... (other parameters)
    """
    # Get connection parameters for the specified environment
    conn_params = get_connection_params(environment)
    
    # Call the existing function with the environment-specific parameters
    return query_sql_server_mfa(
        query=query,
        server=conn_params["server"],
        database=conn_params["database"],
        write_to_duckdb=write_to_duckdb,
        duckdb_table=duckdb_table,
        duckdb_path=duckdb_path,
        log_level=log_level
    )