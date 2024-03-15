import requests # API calls
import os
from dotenv import load_dotenv 
import xml.etree.ElementTree as ET # Parsing XML files
load_dotenv() # Load in environmental variables

userid = os.getenv("USERID")
password = os.getenv("PASSWORD")

query = f"""
https://secure.shippingapis.com/ShippingAPI.dll?API=Verify
&XML=<AddressValidateRequest USERID="{userid}" PASSWORD="{password}">
<Address ID="0">
<Address1></Address1>
<Address2>6406 Ivy Lane</Address2>
<City>Greenbelt</City>
<State>MD</State>
<Zip5></Zip5>
<Zip4></Zip4>
</Address>
</AddressValidateRequest>
USPS Web Tools Developer Guide
Development Guide for APIs (v. 4.7) 15
<AddressValidateResponse>
<Address ID="0">
<Address2>6406 IVY LN</Address2>
<City>GREENBELT</City>
<State>MD</State>
<Zip5>20770</Zip5>
<Zip4>1435</Zip4>
<ReturnText>Default address: The address you entered was found but
more information is needed (such as an apartment, suite, or box number) to
match to a specific address.</ReturnText>
</Address>
"""
c : res = requests.get(query)
print(res.headers["content-type"])
print(type(res))
tree = ET.parse(res)

