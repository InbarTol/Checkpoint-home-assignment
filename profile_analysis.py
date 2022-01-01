import json
import os
from datetime import datetime
ZERO_TIME = 10**-8

def calc_time_in_sec(date1, date2):
    """ This function gets two dates as strings and calculates the time that
    passes between these dates in seconds """
    t1 = datetime.strptime(date1, '%a, %d.%m.%Y %H:%M:%S')
    t2 = datetime.strptime(date2, '%a, %d.%m.%Y %H:%M:%S')
    return abs(int((t1 - t2).total_seconds()))


def connections_frequency(num_connections, time):
    """ This function calculates the frequency of connections per second"""
    if time == 0:
        return ZERO_TIME
    return num_connections / time


def is_obj_similar(object, other):
    """ This helper function return True if 2 objects are similar by their properties."""
    if "service_name" in object and "service_name" in other:
        return object["protocol"] == other["protocol"] and object["port"] == other["port"] and object["service_name"] == \
               other["service_name"]
    else:
        if "port" in object and "port" in other:
            return object["protocol"] == other["protocol"] and object["port"] == other["port"]
    return object["protocol"] == other["protocol"]


def is_object_in_arr(arr, object):
    """ This function verifies if an object is in a given array arr. Returns a boolean value."""
    for i in range(len(arr)):
        if is_obj_similar(arr[i], object):
            return True
    return False


def read_json_files():
    """ This function returns all the data given in the JSON files."""
    files = os.listdir('iot_files')
    all_data = []
    for file_name in files:
        with open('iot_files/' + file_name, "r") as data_file:
            data = json.load(data_file)
            all_data.append(data)
    return all_data


def find_all_types_of_devices(all_data):
    """ This function returns the types of all devices in all given JSON files"""
    all_devices = set()
    for data in all_data:
        iot_items = data["iot_stats"]
        for item in iot_items:
            type_of_device = item["device"]["type"]
            all_devices.add(type_of_device)
    return all_devices


def create_profiles(all_data, all_devices):
    """ This function creates profiles for each device. The function returns a list of all profiles. """
    result = []
    for i, type_device in enumerate(all_devices):
        result.append({"type": type_device, "devices": []})
        j = 0
        for file_data in all_data:
            iot_items = file_data["iot_stats"]
            for iot_item in iot_items:
                seen_already = []
                if iot_item["device"]["type"] == type_device:
                    result[i]["devices"].append({"ID": iot_item["device"]["ID"], "brand": iot_item["device"]["brand"],
                                                 "vendor": iot_item["device"]["vendor"],
                                                 "rank": iot_item["device"]["rank"],
                                                 "destinations": []})
                    for dest in iot_item["destination_services"]:
                        freq_of_connection = connections_frequency(dest["connection_count"],
                                                                   calc_time_in_sec(dest["first_seen"],
                                                                                    dest["last_seen"]))
                        if "service_name" in dest:
                            tmp = {
                                "port": dest["port"],
                                "protocol": dest["protocol"],
                                "service_name": dest["service_name"]
                            }
                            if not is_object_in_arr(seen_already, tmp):
                                seen_already.append(tmp)
                                tmp["frequency"] = [freq_of_connection]
                                result[i]["devices"][j]["destinations"].append(tmp)
                            else:
                                for k in range(len(result[i]["devices"][j]["destinations"])):
                                    if is_obj_similar(result[i]["devices"][j]["destinations"][k], tmp):
                                        result[i]["devices"][j]["destinations"][k]["frequency"].append(
                                            freq_of_connection)
                        else:
                            if "port" in dest:
                                tmp = {
                                    "port": dest["port"],
                                    "protocol": dest["protocol"],
                                }
                            else:
                                tmp = {
                                    "protocol": dest["protocol"],
                                }
                            if not is_object_in_arr(seen_already, tmp):
                                seen_already.append(tmp)
                                tmp["frequency"] = [freq_of_connection]
                                result[i]["devices"][j]["destinations"].append(tmp)
                            else:
                                for k in range(len(result[i]["devices"][j]["destinations"])):
                                    if is_obj_similar(result[i]["devices"][j]["destinations"][k], tmp):
                                        result[i]["devices"][j]["destinations"][k]["frequency"].append(
                                            freq_of_connection)
                    j += 1
    return result


def calc_average_frequency(result):
    """ This function calculates for each list of frequencies in each communication service the average of all
    frequencies. """
    for profile in result:
        for device in profile["devices"]:
            for dest in device["destinations"]:
                dest["frequency"] = str(3600*24*(sum(dest["frequency"]) / len(dest["frequency"]))) + '/day'
    return result


def main():
    all_data = read_json_files()
    all_devices = find_all_types_of_devices(all_data)
    print(all_devices)
    result = create_profiles(all_data, all_devices)
    result = calc_average_frequency(result)
    with open("Profiles.json", "w") as profile:
        profile.write(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()

