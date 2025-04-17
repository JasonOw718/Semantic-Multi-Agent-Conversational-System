class MergedTableIdentifier:
    
    def __init__(self):
        self.__merge_tables_candidates = {}
        self.__table_integral_span_list = {}
    
    def __get_table_span_offsets(self,table):
        """
        Calculates the minimum and maximum offsets of a table's spans.

        Args:
            table (Table): The table object containing spans.

        Returns:
            tuple: A tuple containing the minimum and maximum offsets of the table's spans.
                If the tuple is (-1, -1), it means the table's spans is empty.
        """
        if table.spans:
            min_offset = table.spans[0].offset
            max_offset = table.spans[0].offset + table.spans[0].length

            for span in table.spans:
                if span.offset < min_offset:
                    min_offset = span.offset
                if span.offset + span.length > max_offset:
                    max_offset = span.offset + span.length

            return min_offset, max_offset
        else:
            return -1, -1

    def __get_table_page_numbers(self,table):
        """
        Returns a list of page numbers where the table appears.

        Args:
            table: The table object.

        Returns:
            A list of page numbers where the table appears.
        """
        return [region.page_number for region in table.bounding_regions]

    def identify_merge_table_candidates_and_table_integral_span(self,filename,titles, tables):
        """
        Find the merge table candidates and calculate the integral span of each table based on the given list of tables.

        Parameters:
        tables (list): A list of tables.

        Returns:
        list: A list of merge table candidates, where each candidate is a dictionary with keys:
            - pre_table_idx: The index of the first candidate table to be merged (the other table to be merged is the next one).
            - start: The start offset of the 2nd candidate table.
            - end: The end offset of the 1st candidate table.

        list: A concision list of result.tables. The significance is to store the calculated data to avoid repeated calculations in subsequent reference.
        """
        pre_table_idx = -1
        pre_table_page = -1
        pre_max_offset = 0
        
        self.__merge_tables_candidates[filename] = []
        self.__table_integral_span_list[filename] = []

        for table_idx, table in enumerate(tables):
            min_offset, max_offset = self.__get_table_span_offsets(table)
            if min_offset > -1 and max_offset > -1:
                table_page = min(self.__get_table_page_numbers(table))
                print(
                    f"Table {table_idx} has offset range: {min_offset} - {max_offset} on page {table_page}"
                )

                # If there is a table on the next page, it is a candidate for merging with the previous table.
                if table_page == pre_table_page + 1:
                    pre_table = {
                        "pre_table_idx": pre_table_idx,
                        "start": pre_max_offset,
                        "end": min_offset,
                        "min_offset": min_offset,
                        "max_offset": max_offset,
                    }
                    self.__merge_tables_candidates[filename].append(pre_table)

                table_title = ""
                for title in titles:
                    if title["boundingRegions"][0]["pageNumber"] > table_page:
                        break
                    elif title["boundingRegions"][0]["pageNumber"] < table_page:
                        continue
                    else:
                        if min_offset - title["spans"][0]["offset"] <= 120:
                            table_title = title["content"]
                            titles.pop(0)
                self.__table_integral_span_list[filename].append(
                    {
                        "idx": table_idx,
                        "min_offset": min_offset,
                        "max_offset": max_offset,
                        "table_column": table.column_count,
                        "title": table_title,
                    }
                )

                pre_table_idx = table_idx
                pre_table_page = table_page
                pre_max_offset = max_offset
            else:
                print(f"Table {table_idx} is empty")
                self.__table_integral_span_list[filename].append(
                    {"idx": {table_idx}, "min_offset": -1, "max_offset": -1, "title": ""}
                )
                
    @property
    def merge_tables_candidates(self):
        return self.__merge_tables_candidates
    
    @property
    def table_integral_span_list(self):
        return self.__table_integral_span_list
