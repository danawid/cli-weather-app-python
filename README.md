# Weather CLI

#### Video Demo: https://www.youtube.com/watch?v=nd-VpkDMXHU

#### Description:

Weather CLI was coded as my final project for Harvard's CS50’s Introduction to Programming with Python. It's a command line interface weather app that asks the user for the city is willing to know the weather about, uses the [GeonamesCache library](https://pypi.org/project/geonamescache/) to get the geographic coordinates (latitude and longitude), also asks for the required units to present the information (metric or imperial) and gets the current weather using the [OpenWeather API](https://openweathermap.org/api). Finally asks the user if they would like to obtain a 5 day / 3 hour forecast for the same city, calls the API to the new required information and presents it to the screen organized by days if the user accepted so.

### Imports:

- Imports `os` to read environment variables where the API key will be stored.
- Imports `sys` to exit the program when something goes wrong.
- Imports `flag` to print to the terminal country flags (sadly only prints the country code and not the flag, but I hope one day the country flags will be added as emojis and this little feature will be finally fully supported and useful :) )
- Imports `emoji` to print weather-related emojis while presenting the information and it's also used with some ASCII Art as welcome message.
- Imports `random` to choose some random emojis from a list while generating the welcome message.
- Imports `requests` to handle API calls.
- Imports `geonamescache` to get a list of cities and their coordinates.
- Imports `pyfiglet` to generate a stylized "Weather CLI" welcome message.
- Imports `datetime` to handle the timestamps returned by the API, sunrise and sunset times, convert returned UTC to local or user time, etc.
- Imports `dotenv` to read the API key from the .env file.
- Imports `colorama` to print colored output on Windows terminal, presenting error messages in red, normal program questions in green, "conflicts" in yellow, city information in magenta, and weather information in cyan.

## Initial Setup 

- Complete "API_KEY = ..." on line 18 with your own API key from [OpenWeather API](https://openweathermap.org/)

- For a more complete list of available cities replace default value of min_city_population=15000 with 500, 1000 or 5000.

## How Weather CLI Works:

- `main()`:
    1. Prints welcome message calling `generate_ascii_art()`.
    2. Calls `get_user_input()` to get the city name.
    3. Prompts the user for the desired units to use calling `ask_units()`.
    4. Parses some information from the required city, generates a couple of variables and prints the information to the terminal.
    5. Calls `generate_current_api_url()` to generate the URL to be used to make the API call, passing the previously gathered coordinates and measurement units.
    6. Executes the API call, parses the response and stores the returned respone as `current_response()`.
    7. If the returned status response code IS NOT HTTP 200 OK success, exit the program.
    8. Calls `print_current_response()` passing the just returned response and the selected measurement units.
    9. Asks user if they want to get a 5 day forecast for the same city calling `ask_forecast()` and storing the response as a boolean.
    10. If the user responded yes, `wants_forecast` will be true, and a new API URL will be generated using the same coordinates a units but this time using `generate_forecast_api_url()` to contact the right end point.
    11. Calls the API with the generated URL.
    12. Stores the response as `forecast_response`.
    13. Again, if the returned status response code IS NOT HTTP 200 OK success, exit the program.
    14.  Calls `print_forecast_response()` passing the new returned response and the selected measurement units.
    15. Prints goodbye message.

## Functions

- `generate_ascii_art()`: Creates a welcome message using `Figlet` module to generate a stylized "Weather CLI", surrounded by randomly chosen weather-related emojis.

- `get_user_input()`: Asks the user for a city and searches for similar cities names using `GeonamesCache` library, plus takes care of the error handling for user input. If no similar cities were found, prints an error message and prompts the user again for a city name. If more than one city was found, prints a list of options to the user to choose from. If only a city with that name was found, asks for confirmation. Finally, returns a dictionary containing information of the chosen city.

- `get_country_name_from_code(code)`: Uses the built-in mapper function from `GeonamesCache` to get the country full-name from a country code, since the city information dictionaries only contains country code and not the full name.
    - A bit more of information about the mapper module can be found in https://pypi.org/project/geonamescache/, "Mappers" section.

- `get_emoji_from_id(weather_id, timestamp, sunrise, sunset)`: Considering the passed `weather_id`, returns the appropriate weather emoji based on the weather conditions code that OpenWeather API uses. 
    - Weather condition codes list: https://openweathermap.org/weather-conditions
    - If the sky is clear, It will also return a sun emoji if the time in the city is between `sunrise` and `sunset` or a moon emoji if the time is between `sunset` and `sunrise`.

- `deg_to_compass(deg)`: Takes the wind direction degrees `deg` provided by the
    API response and "translates" it to more human-readable cardinal points
    - Implementation taken from: https://stackoverflow.com/questions/7490660/converting-wind-direction-in-angles-to-text-words
    - Credits to: https://stackoverflow.com/users/697151/steve-gregory

- `calculate_visibility(raw_visibility, units)`: Takes the `visibility` value returned by the API and simply divides it by 1000 if the value indicates "maximum visibility" (10000 metres) to use as default maximum visibility possible value, either 10.00 km or 10.00 miles. If the value is other than 10000, it converts it to miles if the chosen units system is Imperial. If the chosen units system is Metric, again simply returns the value divided by 1000 to use it as kilometres instead of metres.

- `generate_current_api_url(latitude, longitude, units)`: Generates the URL to access the current weather for the provided coordinates and with the chosen units.

- `ask_units()`: Asks what system of units the user would prefer to see the information and handles wrong user inputs while doing so.

- `set_units_current(units)`: Returns correct measurement units for temperature, speed and distance based on the previously chosen units to be used on the current weather.

- `set_units_forecast(units)`: Returns correct measurement units for temperature and speed based on the previously chosen units to be used on the weather forecast (Distance units not used when presenting 5 days forecast).

- `print_current_response(current_response, units)`: Takes the returned dictionary by `get_user_input()`, parses the relevant information, formats and prints the required data for the current weather.

- `ask_forecast()`: Asks the user if they would like to get a weather report for the next 5 days and handles bad user inputs while doing so.

- `print_forecast_response(forecast_response, units)`: Takes the returned dictionary by the second API call, parses the relevant information, formats and prints the required parameters for the 5 day / 3 hour weather forecast, looping through the returned list of dictionaries and converting the forecast time from UTC to local time.

- `generate_forecast_api_url(latitude, longitude, units)`: Generates the URL to access the 5 day weather forecast for the provided coordinates and with the previously chosen units.

## Use Examples:

#### Welcome Message
![](https://lh3.googleusercontent.com/pw/AJFCJaVLvFm2tL4iwdSPOvTSKInj2uzBzunBX3cbRcJWhMyHByrP-3cwWTSkYFEtvJq0__xHF8s0jBC5RQjm45FYjucnFqo0ZIXcgfBZK4PmgtIYUpHD3lVKW4laYWpDKgx_GPCbmCc1gFz0cRx_W35zj96T=w626-h268-s-no)

#### Multiple Cities Found (min_city_population=15000)
![](https://lh3.googleusercontent.com/pw/AJFCJaXOsFQkBoMuDfmi2md1rfbMEOpH-O3-tQJEmktBSBEDpPbai0G5FssBJ2nOLrT-NFNjMAiTecwZlH6sfH9g_1MTUNAo9iSWGg_u6iZQQz15i6VhRhQUIGD9Rp1W1IjtA2iFWeLUnufpdzNI8Fm1K-kp=w628-h451-s-no)

#### Multiple Cities Found (min_city_population=500)
![](https://lh3.googleusercontent.com/pw/AJFCJaUuhZ0xDSt-odAyzKlLKcKnXR4iYBYDOkjmaineTBH1QegDrj0vqr8B_YnBRrDp8umYVxWOc0ymIjPYUXXe8ypsbS-wrZT_NH7Cs6UG9ILFHPoCbHIfeQZdrtcMbAiCjDK92xAMfAT7U5MfIdz0nRZd=w568-h813-s-no)

#### No City Found
![](https://lh3.googleusercontent.com/pw/AJFCJaW8-lmPB0kT_ojO6yjQio-jsWTMV6DtVKW3sbsDyV53RATQUCYXA5gjtYsDCYCb4hM-C8GO0eMPea8P-yPxbAhskhOABp_XXm4wuTF_s07584ZCn1Q_QlHMqApY-uvYC3A8PPvQNDDfmz6aHCLvlAEh=w589-h390-s-no)

#### Only One City Found
![](https://lh3.googleusercontent.com/pw/AJFCJaVRPqAFP3XoOnmhEuBmIqQHwyAX8voIQJStFrd3CdSj5X-t2SCkJHkjshRHN333LdlkbY5s1lLXLUiGQWvekyPndaATCa7qSOHahRJZT546l6gCsHVKuJahL6kf1OPYIc8frC1fkcmfogOHgJKfTCEm=w610-h273-s-no)

#### Wrong User Selection / Asking For Units
![](https://lh3.googleusercontent.com/pw/AJFCJaU_pZt-GV13NwHUD6e-0CyPjlESeOidd2_1st0fzUNXrJlb94BHPGNvb4KaUdAQrm3FWdnTW-6WGgAzIfZa18Oakt7KgQdO7hmMUxn_jnYk3bmu7HjSzMWvsFoG8oe8xRc0ZhP2FP4C7VQbDLjcqlqg=w657-h654-s-no)

#### Displaying Current Weather Using Metric System
![](https://lh3.googleusercontent.com/pw/AJFCJaVQm8Urn4sDG5UxjA7i9oIv8FKYbxo37R6evkDCUymXmApvr9a7BpfrRnjnw5XcEmUi9B2WQHDcmWRpZpvV7Mxto8bx2eCa1CtGhJ7Lcw1AX7nb6jgsSg13kA803iHuarHXAVX3_aMSzV8PdxQWo3Am=w718-h943-s-no)

#### Displaying Current Weather Using Imperial System
![](https://lh3.googleusercontent.com/pw/AJFCJaWyyd7bsVTOrYrYQDN6vFLaI9nMp0CUfuhlULhfLx3ZTthqGGT5U3Rx5I9g4s5zfvvVFF9bK45UnD4w6nkQUyI7rK0zkLLMed_IxeYtw4tgkcl7-SQbhnPPxFZHyChIJdqsiDN9IRYUpjCC_oWOc-Mu=w673-h934-s-no)

#### Displaying Weather Forecast Using Metric System
![](https://lh3.googleusercontent.com/pw/AJFCJaWgCSxGGs5vf0kL5-6_1bGVawJ735lc4rZKm4lw0mjb_WrPlkJ3tNPiQexVa57Qg18YiyQLL5TlTBT-da1PRBNiBoD05-JoRARhqT9R_TT2hYhNZt1U3RrMBrBk622A_tDfxb0VwUuDd_4aUrWz_tmT=w502-h909-s-no)

#### Displaying Weather Forecast Using Imperial System
![](https://lh3.googleusercontent.com/pw/AJFCJaX8B1PNZvn_UcU-UWG8LtfcTRGWPgv0As8uDIb3q_oPgrpNOKTmp0P3aMsu1sB0CppL0OFmOPkLilVp9Ajytu4FMo2iX26a1-FzrL3PtTI26kHv9iczxIknRpOnji3Nq5spGaaluETKRpkzSeTwxjMA=w510-h915-s-no)
  # Lab 6 CI/CD changes
