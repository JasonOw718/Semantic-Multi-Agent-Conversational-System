import pandas as pd
import os
import re
from bs4 import BeautifulSoup
import shutil


class HTMLTableConverter:
    """
    Converts HTML tables to CSV files with appropriate formatting and naming.
    """

    def __init__(self, output_folder, llm):
        """
        Initialize the converter with an output folder.

        Args:
            output_folder (str): Path to the output folder for CSV files
        """
        self.__output_folder = output_folder
        self.__llm = llm

    def convert_tables(self, table_list):
        """
        Convert HTML tables to CSV files.

        Args:
            table_list (dict): Dictionary containing tables organized by filename
        """
        if os.path.exists(self.__output_folder):
            shutil.rmtree(self.__output_folder)
        os.makedirs(self.__output_folder)
        print(f"Recreated csv folder: {self.__output_folder}")

        for filename, results in table_list.items():
            file_folder = os.path.join(
                self.__output_folder, filename.replace(".pdf", "")
            )
            os.makedirs(file_folder, exist_ok=True)

            for index, merged_table in enumerate(results.get("merged", [])):
                self._process_table(merged_table, file_folder, f"merged_{index}")

            for index, not_merged_table in enumerate(results.get("not_merged", [])):
                self._process_table(
                    not_merged_table, file_folder, f"not_merged_{index}"
                )

    def _process_table(self, table_data, folder_path, table_id):
        """
        Process a single table and convert it to CSV.

        Args:
            table_data (dict): Table data containing content and metadata
            folder_path (str): Path to save the CSV file
            table_id (str): Identifier for the table
        """
        content = table_data.get("content", "")
        title = table_data.get("title", "")
        column_count = table_data.get("table_column", 0)

        # Generate filename based on title and content
        csv_filename = self._generate_filename(title, content)

        # Parse HTML table
        soup = BeautifulSoup(content, "html.parser")
        table = soup.find("table")

        if not table:
            print(f"No table found in {table_id}")
            return

        # Extract table data with handling for rowspan and colspan
        max_cols = self._get_max_columns(table)
        matrix = self._build_table_matrix(table, max_cols)

        # Convert matrix to table data, replacing None with empty strings
        table_data_rows = []
        for row in matrix:
            if any(cell is not None for cell in row):
                table_data_rows.append(
                    [cell if cell is not None else "" for cell in row]
                )

        if not table_data_rows:
            print(f"No data found in table {table_id}")
            return

        # If column_count wasn't provided or is incorrect, use the max cols found
        if column_count == 0 or column_count != max_cols:
            column_count = max_cols

        # Generate column names
        column_names = self._generate_column_names(column_count, content)

        # Create DataFrame
        df = pd.DataFrame(table_data_rows, columns=column_names)

        # Save to CSV
        csv_path = os.path.join(folder_path, f"{csv_filename}.csv")
        df.to_csv(csv_path, index=False)
        print(f"Created CSV file: {csv_path}")

    def _get_max_columns(self, table):
        """
        Get the maximum number of columns in a table.

        Args:
            table: BeautifulSoup table element

        Returns:
            int: Maximum number of columns
        """
        max_cols = 0
        for tr in table.find_all("tr"):
            col_count = 0
            for td in tr.find_all(["td"]):
                colspan = int(td.get("colspan", 1))
                col_count += colspan
            max_cols = max(max_cols, col_count)
        return max_cols

    def _build_table_matrix(self, table, max_cols):
        """
        Build a matrix representation of the table handling rowspan and colspan.

        Args:
            table: BeautifulSoup table element
            max_cols (int): Maximum number of columns

        Returns:
            list: Matrix representation of the table
        """
        matrix = []

        # Row by row, fill in the matrix
        row_idx = 0
        for tr in table.find_all("tr"):
            # Extend matrix if necessary
            while len(matrix) <= row_idx:
                matrix.append([None] * max_cols)

            col_idx = 0
            for td in tr.find_all(["td"]):
                # Find the next available column
                while col_idx < max_cols and matrix[row_idx][col_idx] is not None:
                    col_idx += 1

                if col_idx >= max_cols:
                    break

                # Get cell attributes
                colspan = int(td.get("colspan", 1))
                rowspan = int(td.get("rowspan", 1))
                cell_value = td.get_text(strip=True)

                # Fill in the cell and any cells it spans
                for i in range(rowspan):
                    # Extend matrix if necessary
                    while len(matrix) <= row_idx + i:
                        matrix.append([None] * max_cols)

                    for j in range(colspan):
                        if col_idx + j < max_cols:
                            matrix[row_idx + i][col_idx + j] = cell_value

                # Move to next column, accounting for colspan
                col_idx += colspan

            row_idx += 1

        return matrix

    def _generate_filename(self, title, content):
        """
        Generate a filename based on title and content.
        This would typically use LLM logic in your original code.

        Args:
            title (str): Table title
            content (str): Table content

        Returns:
            str: Generated filename
        """
        prompt = (
            "Generate a short,concise and relevant file name (without file extension) "
            "for a CSV file containing the following HTML table title and content :\n\n"
            f"Title: {title}\n\n"
            f"{content}\n\n"
            "Provide only the file name."
        )
        generated_name = self.__llm.invoke(prompt)
        generated_name = generated_name.content.strip().replace(" ", "_")
        return generated_name

    def _generate_column_names(self, column_count, table_content):
        """
        Generate column names for the table.
        This would typically use LLM logic in your original code.

        Args:
            column_count (int): Number of columns
            content (str): Table content

        Returns:
            list: List of column names
        """
        prompt = (
            f"Based on the following HTML table content, generate {column_count} descriptive and "
            f"relevant column names that would be appropriate for a CSV file:\n\n"
            f"{table_content}\n\n"
            f"Provide exactly {column_count} column names as a comma-separated list with no additional text."
        )

        response = self.__llm.invoke(prompt)

        # Split the response by commas and clean up any whitespace
        column_names = [name.strip() for name in response.content.split(",")]

        # Ensure we have exactly the requested number of columns
        if len(column_names) != column_count:
            # If we got the wrong number, create generic column names
            column_names = [f"Column_{i+1}" for i in range(column_count)]

        return column_names
