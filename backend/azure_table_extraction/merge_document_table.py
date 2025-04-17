from bs4 import BeautifulSoup

class DocumentTableMerger:

    def __init__(self):
        self.__BORDER_SYMBOL = "|"
        self.__SEPARATOR_LENGTH_IN_MARKDOWN_FORMAT = 3200
        self.__final_table_list = {}

    def __check_paragraph_presence(self, paragraphs, start, end):
        """
        Checks if there is a paragraph within the specified range that is not a page header, page footer, or page number. If this were the case, the table would not be a merge table candidate.

        Args:
            paragraphs (list): List of paragraphs to check.
            start (int): Start offset of the range.
            end (int): End offset of the range.

        Returns:
            bool: True if a paragraph is found within the range that meets the conditions, False otherwise.
        """
        for paragraph in paragraphs:
            for span in paragraph.spans:
                if span.offset > start and span.offset < end:
                    # The logic role of a parapgaph is used to idenfiy if it's page header, page footer, page number, title, section heading, etc. Learn more: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-layout?view=doc-intel-4.0.0#document-layout-analysis
                    if not hasattr(paragraph, "role"):
                        return True
                    elif hasattr(paragraph, "role") and paragraph.role not in [
                        "pageHeader",
                        "pageFooter",
                        "pageNumber",
                    ]:
                        return True
        return False

    def __remove_header_from_markdown_table(self, markdown_table):
        """
        If an actual table is distributed into two pages vertically. From analysis result, it will be generated as two tables in markdown format.
        Before merging them into one table, it need to be removed the markdown table-header format string. This function implement that.

        Args:
            markdown_table: the markdown table string which need to be removed the markdown table-header.
        Returns:
            string: the markdown table string without table-header.
        """
        HEADER_SEPARATOR_CELL_CONTENT = " - "

        result = ""
        lines = markdown_table.splitlines()
        for line in lines:
            border_list = line.split(HEADER_SEPARATOR_CELL_CONTENT)
            border_set = set(border_list)
            if len(border_set) == 1 and border_set.pop() == self.__BORDER_SYMBOL:
                continue
            else:
                result += f"{line}\n"

        return result

    def __combine_table_markdown(self, md_table_1, md_table_2):
        """
        Merge two consecutive vertical markdown tables into one markdown table.

        Args:
            md_table_1: markdown table 1
            md_table_2: markdown table 2

        Returns:
            string: merged markdown table
        """
        table2_without_header = self.__remove_header_from_markdown_table(md_table_2)
        rows1 = md_table_1.strip().splitlines()
        rows2 = table2_without_header.strip().splitlines()

        num_columns1 = len(rows1[0].split(self.__BORDER_SYMBOL)) - 2
        num_columns2 = len(rows2[0].split(self.__BORDER_SYMBOL)) - 2

        if num_columns1 != num_columns2:
            raise ValueError("Different count of columns")

        merged_rows = rows1 + rows2
        merged_table = "\n".join(merged_rows)

        return merged_table

    def merge_tables(
        self, result_dict, merge_tables_candidates, table_integral_span_list
    ):

        for filename, results in result_dict.items():
            self.__final_table_list[filename] = {"merged": [], "not_merged": []}
            table_count = 0
            if filename in merge_tables_candidates:
                for i, merged_table in enumerate(merge_tables_candidates[filename]):
                    pre_table_idx = merged_table["pre_table_idx"]
                    start = merged_table["start"]
                    end = merged_table["end"]
                    result = results[0]
                    has_paragraph = self.__check_paragraph_presence(
                        result.paragraphs, start, end
                    )
                    is_vertical = (
                        not has_paragraph
                        and result.tables[pre_table_idx].column_count
                        == result.tables[pre_table_idx + 1].column_count
                        and table_integral_span_list[filename][pre_table_idx + 1][
                            "min_offset"
                        ]
                        - table_integral_span_list[filename][pre_table_idx]["max_offset"]
                        <= self.__SEPARATOR_LENGTH_IN_MARKDOWN_FORMAT
                    )
                    if is_vertical:
                        print(f"Merge table: {pre_table_idx} and {pre_table_idx + 1}")
                        print("----------------------------------------")
                        cur_content = result.content[
                            table_integral_span_list[filename][pre_table_idx + 1][
                                "min_offset"
                            ] : table_integral_span_list[filename][pre_table_idx + 1][
                                "max_offset"
                            ]
                        ]
                        merged_list_len = len(self.__final_table_list[filename]["merged"])
                        table_count += 1
                        if (
                            merged_list_len > 0
                            and len(
                                self.__final_table_list[filename]["merged"][-1][
                                    "table_idx_list"
                                ]
                            )
                            > 0
                            and self.__final_table_list[filename]["merged"][-1][
                                "table_idx_list"
                            ][-1]
                            == pre_table_idx
                        ):
                            self.__final_table_list[filename]["merged"][-1][
                                "table_idx_list"
                            ].append(pre_table_idx + 1)
                            self.__final_table_list[filename]["merged"][-1]["offset"][
                                "max_offset"
                            ] = table_integral_span_list[filename][pre_table_idx + 1][
                                "max_offset"
                            ]
                            if is_vertical:
                                self.__final_table_list[filename]["merged"][-1][
                                    "content"
                                ] = self.__combine_table_markdown(
                                    self.__final_table_list[filename]["merged"][-1][
                                        "content"
                                    ],
                                    cur_content,
                                )

                        else:
                            table_count += 2
                            pre_content = result.content[
                                table_integral_span_list[filename][pre_table_idx][
                                    "min_offset"
                                ] : table_integral_span_list[filename][pre_table_idx][
                                    "max_offset"
                                ]
                            ]
                            merged_table = {
                                "table_idx_list": [pre_table_idx, pre_table_idx + 1],
                                "offset": {
                                    "min_offset": table_integral_span_list[filename][
                                        pre_table_idx
                                    ]["min_offset"],
                                    "max_offset": table_integral_span_list[filename][
                                        pre_table_idx + 1
                                    ]["max_offset"],
                                },
                                "content": self.__combine_table_markdown(
                                    pre_content, cur_content
                                ),
                                "table_column": table_integral_span_list[filename][
                                    pre_table_idx
                                ]["table_column"],
                                "title": table_integral_span_list[filename][pre_table_idx][
                                    "title"
                                ],
                            }
                            self.__final_table_list[filename]["merged"].append(merged_table)


    def merge_html_tables(self,html_string):
        # Parse the HTML
        soup = BeautifulSoup(html_string, "html.parser")

        # Find all tables
        tables = soup.find_all("table")

        if len(tables) <= 1:
            return html_string

        # Get the first table as the main table
        main_table = tables[0]

        # Process each subsequent table
        for table in tables[1:]:
            # Check if this is a continuation table (caption contains "continued")
            caption = table.find("caption")
            is_continuation = caption and "continued" in caption.text.lower()

            # Get all rows from the table
            rows = table.find_all("tr")

            # For continuation tables, skip checking if first row has headers
            first_row_has_headers = False
            if rows and not is_continuation:
                first_row_has_headers = rows[0].find("th") is not None

            # Add each row to the main table
            for row in rows:
                # Skip the first row only if it contains th elements and it's not marked as a continuation
                if row == rows[0] and first_row_has_headers and not is_continuation:
                    continue

                # Add the row to the main table
                main_table.append(row)

        # Return the HTML of the merged table
        return str(main_table)

    @property
    def final_table_list(self):
        return self.__final_table_list
