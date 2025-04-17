class TableOrganizer:

    def categorize_tables(
        self, table_integral_span_list, final_table_list, result_dict
    ):
        for filename in table_integral_span_list:
            if filename in final_table_list:
                # Get all indices from table_integral_span_list for this file
                integral_indices = [
                    item["idx"] for item in table_integral_span_list[filename]
                ]

                # Get all indices from final_table_list for this file
                final_indices = []
                for merged_item in final_table_list[filename].get("merged", []):
                    final_indices.extend(merged_item.get("table_idx_list", []))

                # Find missing indices
                missing_indices = [
                    idx for idx in integral_indices if idx not in final_indices
                ]

                if missing_indices:
                    print(f"File: {filename} - Missing indices: {missing_indices}")
                    for idx in missing_indices:
                        # Find the table info for this index
                        table_info = next(
                            (
                                item
                                for item in table_integral_span_list[filename]
                                if item["idx"] == idx
                            ),
                            None,
                        )
                        if table_info:

                            min_off = table_info["min_offset"]
                            max_off = table_info["max_offset"]
                            unmerged_table = {
                                "table_idx_list": [idx],
                                "offset": {
                                    "min_offset": min_off,
                                    "max_offset": max_off,
                                },
                                "content": result_dict[filename][0].content[
                                    min_off:max_off
                                ],
                                "table_column": table_info["table_column"],
                                "title": table_info["title"],
                            }
                            final_table_list[filename]["not_merged"].append(
                                unmerged_table
                            )
            else:

                for table_info in table_integral_span_list[filename]:
                    min_off = table_info["min_offset"]
                    max_off = table_info["max_offset"]
                    unmerged_table = {
                        "table_idx_list": [table_info["idx"]],
                        "offset": {
                            "min_offset": min_off,
                            "max_offset": max_off,
                        },
                        "content": result_dict[filename][0].content[min_off:max_off],
                        "column_count": table_info["column_count"],
                        "title": table_info["title"],
                    }
                    final_table_list[filename]["not_merged"].append(unmerged_table)
        return final_table_list