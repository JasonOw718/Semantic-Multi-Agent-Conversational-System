import pandas as pd
import os
import re
import shutil
import sqlite3


class CSVToSQLConverter:
    """
    Converts CSV files to SQLite databases with appropriate data types.
    """

    def __init__(self, database_folder, csv_folder):
        """
        Initialize the converter with a database folder.

        Args:
            database_folder (str): Path to store the created SQLite databases
        """
        self.__database_folder = database_folder
        self.__csv_folder = csv_folder

    def convert_csvs(self):
        """
        Convert CSV files in subfolders to SQLite databases.

        Args:
            csv_folder (str): Path to the folder containing subfolders with CSV files
        """
        # Create the database folder
        if os.path.exists(self.__database_folder):
            shutil.rmtree(self.__database_folder)
        os.makedirs(self.__database_folder)
        print(f"Recreated database folder: {self.__database_folder}")

        # Skip hidden folders and process only valid subfolders
        for folder_name in os.listdir(self.__csv_folder):
            # Skip hidden folders or files
            if folder_name.startswith("."):
                print(f"Skipping hidden folder/file: {folder_name}")
                continue

            folder_path = os.path.join(self.__csv_folder, folder_name)
            if os.path.isdir(folder_path):
                print(f"Processing folder: {folder_name}")

                # Create a database for this folder
                db_path = os.path.join(self.__database_folder, f"{folder_name}.db")
                conn = sqlite3.connect(db_path)

                # Process each CSV file
                csv_count = 0
                csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

                if not csv_files:
                    print(f"No CSV files found in {folder_name}")
                    conn.close()
                    # Remove empty database file
                    if os.path.exists(db_path):
                        os.remove(db_path)
                    continue

                for file_name in csv_files:
                    csv_count += self._process_csv_file(
                        folder_path, file_name, conn, folder_name
                    )

                # Close the database connection
                conn.close()

                if csv_count > 0:
                    print(f"Created database {folder_name}.db with {csv_count} tables")
                else:
                    print(f"Failed to create tables in {folder_name}.db")
                    # Remove empty database file
                    if os.path.exists(db_path):
                        os.remove(db_path)

    def _process_csv_file(self, folder_path, file_name, conn, folder_name):
        """
        Process a single CSV file and convert it to a SQLite table.

        Args:
            folder_path (str): Path to the folder containing the CSV file
            file_name (str): Name of the CSV file
            conn: SQLite connection
            folder_name (str): Name of the parent folder

        Returns:
            int: 1 if successful, 0 if failed
        """
        csv_path = os.path.join(folder_path, file_name)

        try:
            # Read the CSV with flexible handling for various formats
            try:
                # First attempt with standard settings
                df = pd.read_csv(csv_path)
            except:
                # Try with more flexible settings for problematic files
                df = pd.read_csv(csv_path, encoding="utf-8", sep=None, engine="python")

            # Skip empty dataframes
            if df.empty:
                print(f"  Skipping empty file: {file_name}")
                return 0

            # Clean column names for SQL compatibility
            df.columns = [re.sub(r"[^\w]", "_", col).strip("_") for col in df.columns]

            # Convert data types
            df = self._convert_data_types(df)

            # Create table name from file name
            table_name = os.path.splitext(file_name)[0]
            table_name = re.sub(r"[^\w]", "_", table_name)

            # Save to the database
            df.to_sql(table_name, conn, if_exists="replace", index=False)

            print(f"  Converted {file_name} to table {table_name} in {folder_name}.db")
            return 1

        except Exception as e:
            print(f"  Error processing {file_name}: {str(e)}")
            return 0

    def _convert_data_types(self, df):
        """
        Convert DataFrame column types based on content analysis.

        Args:
            df (pandas.DataFrame): DataFrame to convert

        Returns:
            pandas.DataFrame: DataFrame with converted types
        """
        for col in df.columns:
            data_type = self._detect_data_type(df[col])

            if data_type == "numeric":
                # Clean and convert
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "")
                    .str.replace(r"[\(\)]", "", regex=True)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

                # Check if all non-NA values are equal to their integer conversion
                non_na_values = df[col].dropna()
                if len(non_na_values) > 0:
                    try:
                        is_all_int = (non_na_values == non_na_values.astype(int)).all()
                        if is_all_int:
                            df[col] = df[col].astype(
                                "Int64"
                            )  # Use Int64 to handle NaN values
                    except:
                        pass  # Keep as numeric if comparison fails

            elif data_type == "date":
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except:
                    pass  # Keep as is if conversion fails

        return df

    def _detect_data_type(self, series):
        """
        Detect the most likely data type for a pandas Series.

        Args:
            series (pandas.Series): Series to analyze

        Returns:
            str: Detected data type ('numeric', 'date', or 'string')
        """
        cleaned_series = (
            series.astype(str)
            .str.replace(",", "")
            .str.replace(r"[\(\)]", "", regex=True)
        )

        numeric_series = pd.to_numeric(cleaned_series, errors="coerce")

        if numeric_series.notna().mean() > 0.7:
            return "numeric"

        date_pattern = r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}"
        if series.astype(str).str.match(date_pattern).mean() > 0.7:
            return "date"

        return "string"
