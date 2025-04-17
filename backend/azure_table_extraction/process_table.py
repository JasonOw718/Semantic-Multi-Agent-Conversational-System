class TableProcessor:

    def __init__(self, merged_table_identifier, document_table_merger, table_organizer,content,html_table_converter,csv_to_sql_converter):
        self.__merged_table_identifier = merged_table_identifier
        self.__document_table_merger = document_table_merger
        self.__table_organizer = table_organizer
        self.__html_table_converter = html_table_converter
        self.__csv_to_sql_converter = csv_to_sql_converter
        self.__extracted_content = content

    def merge_and_organize_tables(self):
        print("---identifying merge table candidates and table integral span---")
        for filename,results in self.__extracted_content.items():
            title_item = [item for item in results[0]["paragraphs"] if item.get('role') == 'title']
            if results[0].tables:
                self.__merged_table_identifier.identify_merge_table_candidates_and_table_integral_span(filename,title_item,results[0].tables)
        merge_tables_candidates = self.__merged_table_identifier.merge_tables_candidates
        table_integral_span_list = self.__merged_table_identifier.table_integral_span_list
        print("---merging tables---")
        self.__document_table_merger.merge_tables(self.__extracted_content,merge_tables_candidates,table_integral_span_list)
        final_table_list = self.__document_table_merger.final_table_list
        print("---organizing tables into merged and unmerged table---")
        final_table_list = self.__table_organizer.categorize_tables(table_integral_span_list,final_table_list,self.__extracted_content)
        print("---finalizing html tables---")
        for filename,results in final_table_list.items():
            for merged_table in results["merged"]:
                merged_table["content"] = self.__document_table_merger.merge_html_tables(merged_table["content"])
        print("---converting html tables to csv---")
        self.__html_table_converter.convert_tables(final_table_list)
        print("---converting csv tables to sql---")
        self.__csv_to_sql_converter.convert_csvs()
