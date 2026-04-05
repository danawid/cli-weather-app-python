import os
import sys
import flag
from emoji import emojize
import random
import requests
import geonamescache
from pyfiglet import Figlet
from datetime import datetime
from dotenv import load_dotenv
from geonamescache.mappers import country
from colorama import Fore, Style

load_dotenv()

# Get API Key for https://openweathermap.org/ from a .env file
# Replace with your own API Key.
API_KEY = os.getenv("API_KEY")

# https://pypi.org/project/geonamescache/
# When creating a GeonamesCache you can set the min_city_population parameter
# to either of 500, 1000, 5000 or the default 15000.
# The smaller the minimum population the more cities are included
# in the cities dataset.
gc = geonamescache.GeonamesCache(min_city_population=15000)

# Get a list of countries
countries_list = gc.get_countries_by_names()


def main():
    # Print welcome ASCII Art
    print(generate_ascii_art())

    # Ask user for a city (error handling included)
    # city_data will store a dictionary with all the necessary information
    city_data = get_user_input()

    # Ask user for measurement units to use
    units = ask_units()

    # Get information from the above returned dictionary
    city_name = city_data["name"]
    country_code = city_data["countrycode"]
    latitude = city_data["latitude"]
    longitude = city_data["longitude"]
    country_name = get_country_name_from_code(country_code)

    # Print information about the selected city
    print(Fore.MAGENTA, end="")
    print("\nCity name:", city_name)
    print("Country:", country_name)
    print("Latitude:", latitude)
    print("Longitude:", longitude)
    print(Style.RESET_ALL, end="")

    # Generate URL to call the current weather API using previous
    # determined arguments to get current weather information
    current_api_url = generate_current_api_url(latitude, longitude, units)

    # Execute API call
    try:
        # Store response from openweathermap.org in current_response
        current_response = requests.get(current_api_url, timeout=10)
    except requests.RequestException:
        # Error message if something goes wrong during API call
        print(Fore.RED)
        sys.exit("Oops!Something went wrong." + Style.RESET_ALL)

    # Parse the response as JSON
    current_response = current_response.json()

    if current_response["cod"] != 200:
        # Error message if something is wrong in the API response
        print(Fore.RED)
        sys.exit("Oops!Something went wrong." + Style.RESET_ALL)

    # print_current_response() will take care of parsing, formatting
    # and printing the useful information.
    else:
        print_current_response(current_response, units)

    # Once the current weather of the city was printed, ask the user
    # if they want to get a 5 day/3 hour forecast for the same city.
    wants_forecast = ask_forecast()

    # If the user accepts, generate URL to call now the forecast API
    if wants_forecast:
        forecast_api_url = generate_forecast_api_url(latitude,
                                                     longitude,
                                                     units)

        # Execute API call
        try:
            forecast_response = requests.get(forecast_api_url, timeout=10)
        except requests.RequestException:
            # Error message if something goes wrong during API call
            print(Fore.RED)
            sys.exit("Oops!Something went wrong." + Style.RESET_ALL)

        # Parse the response as JSON
        forecast_response = forecast_response.json()

        if forecast_response["cod"] != "200":
            # Error message if something is wrong in the API response
            print(Fore.RED)
            sys.exit("Oops!Something went wrong." + Style.RESET_ALL)
        else:
            # print_forecast_response() will take care of parsing, formatting
            # and printing the useful information.
            print_forecast_response(forecast_response, units)

    # Print goodbye message
    print(Fore.GREEN, end="")
    print("\nThanks for using Weather CLI!")
    print("Bye!")
    print(Style.RESET_ALL)


# Validate user input
def get_user_input():
    """
    Asks the user for a city and searches for similar cities and
    takes care of the error handling.
    If no similar cities were found, prints an error message and
    asks again for a city name.
    If more than one city was found, prints a list of options to the
    user to choose from.
    If only a city with that name was found, asks for confirmation.
    Finally, returns a dictionary containing information of the chosen city.
    """
    while True:
        user_input = input(
            Fore.GREEN
            + """What city would you like\
 to know about the weather?: """
            + Style.RESET_ALL
        )
        # If user input has less than characters, show an error message
        # The amount of returned values could be huge
        if len(user_input) < 3:
            print(
                emojize(
                    Fore.YELLOW
                    + """Sorry, that would return\
 a huge list :grinning_face_with_sweat:"""
                )
            )
            print(Fore.YELLOW + "Please be more specific." + Style.RESET_ALL)
            # Try again
            continue
        # If user input has 3 characters or more, look for a list of
        # cities with similar name
        similar_results = gc.search_cities(
            user_input, case_sensitive=False, attribute="name"
        )
        # Sort the list by population (most populated city will show
        # up on top)
        similar_results = sorted(
            similar_results, key=lambda d: d["population"], reverse=True
        )

        if len(similar_results) > 1:
            # If more than one city was found, show city options:
            print(Fore.YELLOW)
            print("Well, we have a couple of coincidences here.")
            print("(Sorted by population)\n")
            option_lists = []

            # Print options, generate a list of valid options
            for i, cities in enumerate(similar_results, start=1):
                option_lists.append(i)
                city = cities["name"]
                country_code = cities["countrycode"]
                country_name = get_country_name_from_code(country_code)
                print(f"Option [{i}]: {city}, {country_name}", end=" ")
                print(flag.flag(country_code))

            # Get option from user / handle incorrect inputs
            while True:
                try:
                    user_selection = int(
                        input(
                            Fore.YELLOW
                            + f"\nWhich one is the one you \
are after? (1 to {len(similar_results)}): "
                            + Style.RESET_ALL
                        )
                    )
                except ValueError:
                    print(Fore.RED)
                    print("Not a valid option! Try again.")
                    print(Style.RESET_ALL)
                    continue
                if user_selection in option_lists:
                    city_data = similar_results[user_selection - 1]
                    return city_data
                else:
                    print(Fore.RED)
                    print("Not a valid option! Try again.", end="")
                    print(Style.RESET_ALL)

        # If length of similar_results equals 0, no cities wit
        # a similar name were found
        elif len(similar_results) == 0:
            # If no city was found, try again:
            print(Fore.RED)
            print("\nSorry, no city found with that name.")
            print("Please try again.\n")
            print(Style.RESET_ALL)
            continue

        # Otherwise (a single city with similar name was found)...
        else:
            # Present option and ask for confirmation
            city_name = similar_results[0]["name"]
            country_code = similar_results[0]["countrycode"]
            city_data = similar_results[0]
            country_name = get_country_name_from_code(country_code)

            while True:
                print(Fore.GREEN)
                user_confirmation = input(f"Are we talking about {city_name},\
 {country_name} {flag.flag(country_code)}? (Y/N): " + Style.RESET_ALL).lower()
                # If that's the right city, return city_data
                # dictionary to main()
                if user_confirmation in ["y", "yes"]:
                    return city_data
                # If it's not, break the while loop
                # (and it will ask again for the city name)
                elif user_confirmation in ["n", "no"]:
                    print(Fore.YELLOW)
                    print("Ok, let's try again then.")
                    print(Style.RESET_ALL)
                    break
                # If user answers other than y, yes, n or no ask again
                else:
                    print(Fore.RED)
                    print("Not a valid option. Try again (Y/N): ", end="")
                    print(Style.RESET_ALL)


def generate_ascii_art():
    """
    generate_ascii_art() will generate some ASCII Art (lol) using the Figlet
    library to print the script name, and choosing random weather-related
    emojis from the list below.
    """
    figlet = Figlet()

    font = "slant"

    figlet.setFont(font=font)

    text = "Weather CLI"

    emojis_list = [
        ":cloud:",
        ":cloud_with_lightning:",
        ":cloud_with_lightning_and_rain:",
        ":cloud_with_rain:",
        ":cloud_with_snow:",
        ":closed_umbrella:",
        ":sun_behind_cloud:",
        ":sun:",
        ":sun_behind_large_cloud:",
        ":sunrise:",
        ":sun_with_face:",
        ":sunrise_over_mountains:",
        ":sun_behind_small_cloud:",
        ":sun_behind_rain_cloud:",
        ":umbrella_with_rain_drops:",
        ":umbrella_on_ground:",
        ":umbrella:",
        ":snowflake:",
        ":snowman:",
        ":beach_with_umbrella:",
        ":desert_island:",
        ":water_wave:",
    ]

    emojis_to_print = 20
    string_to_return = ""

    string_to_return += "\n\n"
    for _ in range(emojis_to_print):
        string_to_return += emojize(random.choice(emojis_list)) + "  "
    string_to_return += "\n"
    string_to_return += Fore.CYAN + figlet.renderText(text)
    for _ in range(emojis_to_print - 2):
        string_to_return += emojize(random.choice(emojis_list)) + "  "
    string_to_return += "\n\n"

    return string_to_return


def get_country_name_from_code(code):
    """
    The mapper module is documented in https://pypi.org/project/geonamescache/
    """
    mapper = country(from_key="iso", to_key="name")
    return mapper(code)


def get_emoji_from_id(weather_id, timestamp, sunrise, sunset):
    """
    get_emoji_from_id() will return the right weather emoji based on
    the weather conditions code that OpenWeather API uses.
    Weather condition codes list: https://openweathermap.org/weather-conditions
    If the sky is clear, It will also return a sun emoji if the time in the
    city is between sunrise and sunset or a moon emoji if the time is
    between sunset and sunrise.
    """
    if weather_id.startswith("2"):
        return ":cloud_with_lightning_and_rain:"
    elif weather_id.startswith("3"):
        return ":cloud_with_rain:"
    elif weather_id.startswith("5"):
        return ":cloud_with_rain:"
    elif weather_id.startswith("6"):
        return ":snowflake:"
    elif weather_id.startswith("7"):
        return ":fog:"
    elif weather_id == "800":
        if timestamp > sunrise and timestamp < sunset:
            return ":sun:"
        else:
            return ":last_quarter_moon:"
    elif weather_id.startswith("8"):
        return ":cloud:"
    else:
        return ""


def deg_to_compass(deg):
    """
    Implementation taken from:
    https://stackoverflow.com/questions/7490660/converting-wind-direction-in-angles-to-text-words
    Credits to: https://stackoverflow.com/users/697151/steve-gregory
    deg_to_compass() will take the wind direction degrees provided by the
    API response and "translate" it to more human-readable cardinal points
    """
    value = int((deg / 22.5) + 0.5)
    compass_directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    return compass_directions[(value % 16)]


def calculate_visibility(raw_visibility, units):
    """
    If raw_visibility is the maximum value possible (10000 metres)
    calculate_visibility() will simply return 10.00 (to use as kms or miles).
    Otherwise, it will return the value transformed to miles if the chosen
    units are imperial, or the original values (in metres) divided by 1000
    to get a return value in kms.
    """
    if raw_visibility == 10000:
        visibility = raw_visibility / 1000.00
    else:
        if units == "imperial":
            visibility = (raw_visibility / 1000) / 1.609
        else:
            visibility = raw_visibility / 1000.00
    return round(visibility, 2)


def generate_current_api_url(latitude, longitude, units):
    """
    Generates the URL to access the current weather for the provided
    coordinates and with the chosen units.
    """
    return f"""https://api.openweathermap.org/data/2.5/weather?\
lat={latitude}&lon={longitude}&appid={API_KEY}&units={units}"""


def ask_units():
    """
    Asks what system of units the user would prefer / Handle wrong inputs.
    """
    while True:
        user_preference = input(
            Fore.GREEN
            + """\nIn which units do you \
prefer the information? (M)etric or (I)mperial? """
            + Style.RESET_ALL
        ).lower()
        if user_preference in ["m", "metric"]:
            return "metric"
        elif user_preference in ["i", "imperial"]:
            return "imperial"
        else:
            print(Fore.RED)
            print("Sorry! Wrong input, please try again.", end="")
            print(Style.RESET_ALL)
            continue


def set_units_current(units):
    """
    Returns correct measurement units for temperature, speed and distance
    based on the previously chosen units to be used on the current weather
    """
    if units == "metric":
        return "°C", "meters/sec", "kms"
    elif units == "imperial":
        return "°F", "miles/hour", "miles"
    else:
        raise ValueError("Units were not properly defined.")


def set_units_forecast(units):
    """
    Returns correct measurement units for temperature and speed
    based on the previously chosen units to be used on the weather forecast
    (Distance units not used when presenting 5 days forecast)
    """
    if units == "metric":
        return "°C", "meters/sec"
    elif units == "imperial":
        return "°F", "miles/hour"
    else:
        raise ValueError("Units were not properly defined.")


def print_current_response(current_response, units):
    """
    print_current_response() takes the returned dictionary by get_user_input(),
    parses the relevant information, formats and prints the required parameters
    for the current weather
    """
    temp_unit, speed_unit, distance_unit = set_units_current(units)
    timestamp = current_response["dt"]
    city_name = current_response["name"]
    country_code = current_response["sys"]["country"]
    country_name = get_country_name_from_code(country_code)

    weather_id = str(current_response["weather"][0]["id"])
    main_weather = current_response["weather"][0]["main"]
    description = current_response["weather"][0]["description"]
    sunrise = current_response["sys"]["sunrise"]
    sunset = current_response["sys"]["sunset"]
    weather_emoji = get_emoji_from_id(weather_id,
                                      timestamp,
                                      sunrise,
                                      sunset)
    temp = current_response["main"]["temp"]
    feels_like = current_response["main"]["feels_like"]
    temp_min = current_response["main"]["temp_min"]
    temp_max = current_response["main"]["temp_max"]
    pressure = current_response["main"]["pressure"]
    humidity = current_response["main"]["humidity"]
    raw_visibility = current_response["visibility"]
    visibility = calculate_visibility(raw_visibility, units)
    wind_speed = current_response["wind"]["speed"]
    wind_direction = deg_to_compass(current_response["wind"]["deg"])
    clouds = current_response["clouds"]["all"]
    dt = current_response["dt"]
    timezone = current_response["timezone"]
    # Convert sunrise and sunset to local time
    sunrise = sunrise + timezone
    sunset = sunset + timezone
    sunrise = datetime.fromtimestamp(sunrise).strftime("%I:%M:%S %p")
    sunset = datetime.fromtimestamp(sunset).strftime("%I:%M:%S %p")
    last_updated = datetime.fromtimestamp(dt).strftime("%I:%M:%S %p")

    print(Fore.CYAN, end="")
    print(f"\nThe current weather in {city_name}, {country_name} is:\n")
    print(emojize(f"{weather_emoji}   {main_weather} ({description})"))
    print(emojize(f":thermometer:   Temperature: {temp}{temp_unit}"))
    print(
        emojize(
            f""":person_mountain_biking:  \
Feels Like: {feels_like}{temp_unit}"""
        )
    )
    print(
        emojize(
            f""":red_circle:  Max currently \
observed temperature in {city_name}: {temp_max}{temp_unit}"""
        )
    )
    print(
        emojize(
            f""":blue_circle:  Min currenty observed \
temperature in {city_name}: {temp_min}{temp_unit}"""
        )
    )
    print(emojize(f":balance_scale:   Pressure: {pressure} hPa"))
    print(emojize(f":droplet:  Humidity: {humidity}%"))
    print(
        emojize(
            f""":telescope:  Visibility: \
{visibility:.2f} {distance_unit}"""
        )
    )
    print(
        emojize(
            f""":wind_face:   Wind speed: \
{wind_speed} {speed_unit}"""
        )
    )
    print(emojize(f":compass:  Wind direction: {wind_direction}"))
    print(emojize(f":cloud:   Cloudiness: {clouds}%"))
    print(
        emojize(
            f":sunrise:  Sunrise: {sunrise} \
({city_name} time)"
        )
    )
    print(
        emojize(
            f":sunset:  Sunset: {sunset} \
({city_name} time)"
        )
    )
    print(
        emojize(
            f":hourglass_done:  Last updated: \
{last_updated} (Your time)\n"
        )
    )
    print(Style.RESET_ALL, end="")


def ask_forecast():
    """
    Asks the user if they would like to get a weather report for the
    next 5 days / Handle wrong inputs.
    """
    while True:
        user_response = input(Fore.GREEN + "Would you like to get a 5 day\
 forecast? (Y/N) " + Style.RESET_ALL).lower()
        if user_response in ["y", "yes"]:
            return True
        elif user_response in ["n", "no"]:
            return False
        else:
            print(Fore.RED)
            print("Sorry! Wrong input, please try again.", end="")
            print(Style.RESET_ALL)
            continue


def print_forecast_response(forecast_response, units):
    """
    print_forecast_response() takes the returned dictionary by the second API
    call, parses the relevant information, formats and prints the required
    parameters for the 5 day / 3 hour weather forecast, looping through the
    returned list of dictionaries and converting the forecast time from UTC
    to local time.
    """
    temp_unit, speed_unit = set_units_forecast(units)

    city_name = forecast_response["city"]["name"]
    timezone = int(forecast_response["city"]["timezone"])
    sunrise = forecast_response["city"]["sunrise"] + timezone
    sunrise = datetime.fromtimestamp(sunrise)
    sunset = forecast_response["city"]["sunset"] + timezone
    sunset = datetime.fromtimestamp(sunset)
    date = ""

    for forecast in forecast_response["list"]:
        timestamp = forecast["dt"]

        local_time = timestamp + timezone

        forecast_time = (
            datetime.fromtimestamp(local_time).strftime("%I:%M:%S %p")
        )

        forecast_hour = datetime.fromtimestamp(local_time)

        new_date = (
            datetime.fromtimestamp(local_time).strftime("%A, %d %B %Y")
        )

        timestamp = datetime.fromtimestamp(timestamp)

        weather_id = str(forecast["weather"][0]["id"])
        weather_main = forecast["weather"][0]["main"]
        description = forecast["weather"][0]["description"]
        weather_emoji = get_emoji_from_id(weather_id,
                                          forecast_hour.hour,
                                          sunrise.hour,
                                          sunset.hour)
        temp = forecast["main"]["temp"]
        pressure = forecast["main"]["pressure"]
        humidity = forecast["main"]["humidity"]
        wind_speed = forecast["wind"]["speed"]
        wind_direction = deg_to_compass(forecast["wind"]["deg"])
        clouds = forecast["clouds"]["all"]

        if new_date != date:
            print(Fore.YELLOW, end="")
            print(emojize(f"\n:calendar:  {new_date}"))
            date = new_date
        print(Fore.MAGENTA, end="")
        print(emojize(f":hourglass_done:  {forecast_time} \
({city_name} time)"))
        print(Fore.CYAN, end="")
        print(emojize(f"{weather_emoji}   {weather_main} ({description})  \
    :thermometer:  Temperature: {temp}{temp_unit}  :balance_scale:   \
Pressure: {pressure} hPa"))
        print(emojize(f":droplet:  Humidity: {humidity}%      \
    :wind_face:   Wind: {wind_speed} {speed_unit} {wind_direction}   :cloud:  \
Cloudiness: {clouds}%"))
        print(Style.RESET_ALL, end="")


def generate_forecast_api_url(latitude, longitude, units):
    """
    Generates the URL to access the 5 day weather forecast for the provided
    coordinates and with the previously chosen units.
    """
    return f"""https://api.openweathermap.org/data/2.5/forecast?\
lat={latitude}&lon={longitude}&appid={API_KEY}&units={units}"""


if __name__ == "__main__":
    main()
