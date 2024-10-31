import re

def clean_sql(sql):
    """Clean and standardize SQL statement"""
    # Remove extra whitespace while preserving newlines for readability
    sql = re.sub(r' +', ' ', sql)
    sql = re.sub(r'\n\s*\n', '\n', sql)
    
    # Remove comments
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    
    # Remove GO statements
    sql = re.sub(r'\bGO\b', '', sql)
    
    # Fix file paths
    sql = re.sub(r'\\', r'\\\\', sql)
    
    # Clean up any remaining whitespace
    sql = sql.strip()
    
    return sql

def format_sql(sql):
    """Format SQL statement with proper indentation and line breaks"""
    # Add line breaks after major clauses
    sql = re.sub(r'\b(CREATE|ALTER|USE|ON|LOG)\b', r'\n\1', sql)
    
    # Format CREATE TABLE statements
    sql = re.sub(r'CREATE TABLE \[([^\]]+)\]\s*\((.*?)\)', 
                 lambda m: f'CREATE TABLE [{m.group(1)}] (\n    ' + 
                         ',\n    '.join(re.findall(r'\[[^\]]+\]\s+\[[^\]]+\](?:\([^)]+\))?\s*(?:NULL|NOT NULL)?', m.group(2))) +
                         '\n)',
                 sql, flags=re.DOTALL)
    
    # Format database creation
    sql = re.sub(r'(CREATE DATABASE.*?)\s*\((.*?)\)', 
                 lambda m: f'{m.group(1)} (\n    ' + 
                         ',\n    '.join(re.split(r',\s*', m.group(2))) +
                         '\n)',
                 sql, flags=re.DOTALL)
    
    lines = sql.split('\n')
    formatted_lines = []
    indent_level = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Adjust indent level based on parentheses
        indent_level += line.count('(') - line.count(')')
        
        # Add proper indentation
        if line.startswith(('CREATE', 'ALTER', 'USE')):
            formatted_lines.append(line)
        else:
            formatted_lines.append('    ' * max(0, indent_level) + line)
            
    return '\n'.join(formatted_lines)

def extract_statements(sql_file):
    """Extract SQL statements from file and format them"""
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract statements between triple quotes
    statements = re.findall(r'r?"""([^"]*?)"""', content, re.DOTALL)
    
    # Clean and format each statement
    formatted_statements = []
    for stmt in statements:
        stmt = stmt.strip()
        if stmt and not stmt.isspace():
            cleaned = clean_sql(stmt)
            formatted = format_sql(cleaned)
            if formatted:
                formatted_statements.append(formatted)
    
    return formatted_statements

def format_as_python(statements):
    """Format SQL statements as Python function with proper escaping"""
    output = [
        "def get_ddl_statements():",
        '    """Get DDL SQL statements for database setup"""',
        "    return [",
    ]
    
    for stmt in statements:
        if stmt.strip():
            # Format each statement as a raw triple-quoted string
            formatted = f'        r"""\n{stmt}\n        """,'
            output.append(formatted)
    
    output.append("    ]")
    return '\n'.join(output)

def main():
    # Extract statements from SQL DDL file
    statements = extract_statements('sql_ddl.py')
    
    # Format as Python code
    python_code = format_as_python(statements)
    
    # Write formatted code back to file
    with open('sql_ddl.py', 'w', encoding='utf-8') as f:
        f.write(python_code)

if __name__ == '__main__':
    main()
