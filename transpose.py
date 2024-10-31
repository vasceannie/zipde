import os
import re

def extract_queries(sql_content):
    """Extract individual SQL queries from content, separated by blank lines or comments."""
    queries = []
    current_query = []
    current_comment = []
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # Skip empty lines between queries
        if not line:
            if current_query:
                # Combine comment and query
                if current_comment:
                    query_text = f"-- {' '.join(current_comment)}\n{' '.join(current_query)}"
                else:
                    query_text = ' '.join(current_query)
                queries.append(query_text)
                current_query = []
                current_comment = []
            continue
            
        # Collect comments
        if line.startswith('--'):
            if current_query:  # If we have a query, this is a new one
                if current_comment:
                    query_text = f"-- {' '.join(current_comment)}\n{' '.join(current_query)}"
                else:
                    query_text = ' '.join(current_query)
                queries.append(query_text)
                current_query = []
                current_comment = []
            current_comment.append(line.strip('- ').strip())
        else:
            current_query.append(line)
    
    # Add final query if exists
    if current_query:
        if current_comment:
            query_text = f"-- {' '.join(current_comment)}\n{' '.join(current_query)}"
        else:
            query_text = ' '.join(current_query)
        queries.append(query_text)
        
    return queries

def format_training_output(queries):
    """Format queries in the training.py get_sample_queries() format."""
    output = ["def get_sample_queries():", 
              "    \"\"\"Get sample SQL queries for training\"\"\"",
              "    return ["]
    
    for query in queries:
        # Format each query as a triple-quoted string
        formatted_query = f'        """\n        {query}\n        """,'
        output.append(formatted_query)
    
    output.append("    ]")
    return '\n'.join(output)

def process_sql_files(folder_path):
    """Process all SQL files in the given folder."""
    all_queries = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.sql'):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract individual queries and add to collection
            file_queries = extract_queries(content)
            all_queries.extend(file_queries)
    
    return format_training_output(all_queries)

def main():
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scripting_dir = os.path.join(script_dir, 'scripting')
    
    # Process SQL files
    output = process_sql_files(scripting_dir)
    
    # Write output
    output_path = os.path.join(script_dir, 'training_queries.py')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)
        
if __name__ == '__main__':
    main()
