from setuptools import setup, find_packages

setup(
    name="db_connect",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        'pandas>=3.1.0',
        'sqlalchemy>=2.1.6',
        'pyodbc>=5.3.0',
        'duckdb>=2.0.0',
        'duckdb-engine>=0.17.0',
        'psycopg[binary]>=3.2.0',
        'azure-identity>=1.26.0',
        'python-dotenv>=1.2.4',
        'polars>=2.0.0',
        'setuptools>=80.0.0',
    ],
    python_requires='>=3.11'
)