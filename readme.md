# PM Weather API  
  
**/search/\<location\>**  
Searches the Geonames database for the corresponding location, takes the coordinates of the first results and   sends them to the Darksky API request. Fetches full data if no further endpoint is specified. (/current, /  basic, /forecast, /\<unix_timestamp\> for detailed requests). e.g. /search/helsinki/current  


**/estonian_map (/\<one_of_15_cities\>)**  
Estonian map. Endpoint pulls the basic weather information for the 15 county capitals of Estonia. (All   together or separately). Displays the name of the city, icon, temperature, apparent temperature, wind speed,   wind direction and a verbal summary (in English).  


**/\<one_of_15_cities\>**  
Fetches the Darksky API full data for one of the cities. (/current, /basic, /forecast, /\<unix_timestamp\>  for detailed requests). e.g. /jõhvi/forecast  


**/coordinates/\<coordinates\>**  
Works the same way as ‘/search’. (/current; /forecast, /basic, /\<unix_timestamp\> for detailed requests)   e.g. /coordinates/59.4372,24.7454  
Coordinates also gives the address of the specified coordinates. Its JSON field is 'address'   e.g "19, Väike-Tähe, Kesklinn, Tartu, Tartu maakond, 50103, Eesti",  


**endpoints:**  
/current: displays the current information  
/forecast: displays the information for the following week   
/basic: displays basic information for today, tomorrow and the day after tomorrow  
/\<unix_timestamp\>: displays a full data request for the specified time. e.g. /1476738000  
  
Every response is in **JSON:** first element is 'location' and every 'location' has a 'name' attribute.   (Coordinates has an 'address' field instead.)  
  
**Environment variables:**
'DARK_SKY_SUFFIX': '?units=si&lang=et' is default (Estonian).  
'API-KEY'  
'GRAYLOG-SERVER-HOST'  
'GRAYLOG-SERVER-PORT': 12201 is default.  
'APP-PORT': 80 is default.  
'APP-URL-PREFIX'  
  

**15 cities (county capitals of Estonia):**  
Tallinn  
Tartu  
Viljandi  
Pärnu  
Haapsalu  
Jõgeva  
Kärdla  
Kuressaare  
Võru  
Rakvere  
Paide  
Rapla  
Jõhvi  
Põlva  
Valga



