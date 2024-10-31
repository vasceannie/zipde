import vanna
from vanna.remote import VannaDefault
from vanna.flask import VannaFlaskApp
import os

api_key = '44b9eee75ef949259f329ede6068b6a4'

vanna_model_name = 'kp-contracts'
vn = VannaDefault(model=vanna_model_name, api_key=api_key)
vn.connect_to_mssql(
    odbc_conn_str="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=kpdb;Trusted_Connection=yes"
)
app = VannaFlaskApp(
    vn=vn, 
    allow_llm_to_see_data=True, 
    logo=os.path.abspath('banner-logo-rise-now2x.png'),  # Use absolute path
    title='Database Deblunker', 
    subtitle='Deblunk that base of data real good.'
)
app.run()