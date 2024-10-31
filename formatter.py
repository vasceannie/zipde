import re

def reformat_sql_ddl(input_file, output_file):
    with open(input_file, 'r') as file:
        content = file.read()

    # Find all CREATE TABLE statements using regex
    tables = re.findall(r"(CREATE TABLE\s+\[dbo\].*?GO)", content, re.DOTALL)

    with open(output_file, 'w') as file:
        # Define a function to return a list of DDL statements
        file.write("def get_ddl_statements():\n")
        file.write("    return [\n")

        # Iterate over each DDL and format it
        for table in tables:
            # Add indentation and wrap each statement as a string in the list
            formatted_table = "        '''" + table.replace("\n", "\n        ") + "'''"
            file.write(formatted_table + ",\n")

        file.write("    ]\n")

# Example usage
reformat_sql_ddl('sql_ddl.py', 'sql_ddl_reformatted.py')
