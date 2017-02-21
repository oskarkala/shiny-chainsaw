# PM Weather API  

**/\<language\>/\<location\>**  
Searches the Geonames database for the corresponding location, takes the coordinates of the first results and  sends them to the Darksky API request. Fetches full data if no further endpoint is specified. (/current, /  basic, /forecast for detailed requests). e.g. et/helsinki/current    


**/\<language\>/coordinates/\<coordinates\>**  
Works the same way as ‘\<location\>’. (/current; /forecast, /basic for detailed requests)   e.g. ru/coordinates/59.4372,24.7454  
Coordinates also gives the address of the specified coordinates. Its JSON field is 'address'   e.g "19, Väike-Tähe, Kesklinn, Tartu, Tartu maakond, 50103, Eesti",  


**endpoints:**  
/current: displays the current information  
/forecast: displays the information for the following week   
/basic: displays basic information for today, tomorrow and the day after tomorrow  
  
Every response is in **JSON:** first element is 'location' and every 'location' has a 'name' attribute.   (Coordinates has an 'address' field instead.)  
  
**Environment variables:**  
'DARK_SKY_SUFFIX': '?units=si&lang=et' is default (Estonian).  
'API_KEY'  
'GRAYLOG_SERVER_HOST'  
'GRAYLOG_SERVER_PORT': 12201 is default.  
'APP_PORT': 80 is default.  
'APP_URL_PREFIX'  
  

**languages:**  
  et for Estonian  
  en for English
  ru for Russian  
  lv for Latvian

