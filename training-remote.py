import pandas as pd
import vanna
from vanna.flask import VannaFlaskApp
from vanna.remote import VannaDefault
from get_sample_queries import get_sample_queries
from results.sql_ddl_reformatted import get_ddl_statements
import os

api_key = '44b9eee75ef949259f329ede6068b6a4'

vanna_model_name = 'kp-contracts'

def initialize_vanna():
    return VannaDefault(model=vanna_model_name, api_key=api_key)

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
    # """Main function to train Vanna"""
    vn = initialize_vanna()
    
    # # Train schema information
    # print("Training schema information...")
    # for query in get_ddl_statements():
    #     vn.train(ddl=query)
    
    # # # Train business documentation
    # print("Training business documentation...")
    # for doc in get_business_documentation():
    #     vn.train(documentation=doc)
    
    # # # Train sample queries
    # print("Training sample queries...")
    # for query in get_sample_queries():
    #     vn.train(sql=query)
    
    # Get information schema for comprehensive training
    vn.connect_to_mssql(
        odbc_conn_str="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=kpdb;Trusted_Connection=yes"
    )
    # print("Training from information schema...")
    # df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    # plan = vn.get_training_plan_generic(df_information_schema)
    # print(plan)
    # vn.train(plan=plan)
    
    return vn

def run_vanna():
    vn = initialize_vanna()
    vn.run(
        vn=vn, 
        allow_llm_to_see_data=True, 
        logo=os.path.abspath('banner-logo-rise-now2x.png'),  # Use absolute path
        title='Database Deblunker', 
        subtitle='Deblunk that base of data real good.'
    )
if __name__ == "__main__":
    app = run_vanna()
