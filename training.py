import pandas as pd
from sqlserver import MyVanna
from vanna.ollama import Ollama
from get_sample_queries import get_sample_queries
from results.sql_ddl_reformatted import get_ddl_statements

def initialize_vanna():
    # Initialize Vanna with NV-Embed model
    vn = MyVanna(config={'model': 'llama3.2'})
    return vn

def get_business_documentation():
    """Get business context and documentation"""
    return [
        "GL Strings are used for accounting entries and consist of Account, Activity, and GL Unit/Location/Department segments",
        "Active flag in GL tables indicates whether the code combination is currently valid for use",
        "OneLink Contract system manages supplier contracts and their relationships",
        "Supplier Master contains the authoritative source for vendor information including status and replacements",
        "Contract numbers are unique identifiers for agreements with suppliers",
        "Vendor replacement occurs when an existing vendor is superseded by another vendor ID",
        "External Ref Code and External Ref Num are used to map GL codes to external systems"
    ]

def train_vanna():
    """Main function to train Vanna"""
    vn = initialize_vanna()
    
    # Train schema information
    print("Training schema information...")
    for query in get_ddl_statements():
        vn.train(ddl=query)
    
    # # Train business documentation
    print("Training business documentation...")
    for doc in get_business_documentation():
        vn.train(documentation=doc)
    
    # # Train sample queries
    print("Training sample queries...")
    for query in get_sample_queries():
        vn.train(sql=query)
    
    # Get information schema for comprehensive training
    print("Training from information schema...")
    vn.connect_to_mssql(
        odbc_conn_str="DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=localhost;DATABASE=kpdb;Trusted_Connection=yes"
    )
    df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    plan = vn.get_training_plan_generic(df_information_schema)
    print(plan)
    vn.train(plan=plan)
    
    return vn

if __name__ == "__main__":
    trained_vanna = train_vanna()
