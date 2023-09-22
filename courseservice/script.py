import json, requests
import time
import os
import concurrent.futures

"""
Script to download course data from wagolf association.
"""

URL = "https://wagolf.org/wp-admin/admin-ajax.php?action=ghin_get_course&id="

HEADERS = {
    'User-Agent': 'Postman',
    'Accept': "*/*",
    'Accept-Encoding': "gzip, deflate, br",
    "Connection": "keep-alive",
    "authority": "wagolf.org",
    "accept": "application/json; charset=UTF-8, text/javascript, */*; q=0.01",
    "accept-language": "en-US,en;q=0.6",
    "referer": "https://wagolf.org/keep-score/post-a-score/"
}

def filter(data):
    if not data["CourseStatus"] or data["CourseStatus"] != "Active":
        return None

    return_object = {}
    return_object["course_id"] = data["CourseId"]
    return_object["course_name"] = data.get('CourseName', None)
    return_object["facility_name"] = data["Facility"].get('FacilityName', None)
    return_object["course_city"] = data.get('CourseCity', None)
    return_object["course_state"] = data.get('CourseState', None)
    return_object["formatted_address"] = data["Facility"].get("GeoLocationFormattedAddress", None)
    return_object["longitude"] = data["Facility"].get("GeoLocationLongitude", None)
    return_object["latitude"] = data["Facility"].get("GeoLocationLatitude", None)

    return_object["tee_sets"] = []
    for tee_set in data["TeeSets"]:
        if tee_set["Gender"] == "Female":
            continue
        filtered_tee_set = {}
        filtered_tee_set["tee_set_id"] = tee_set["TeeSetRatingId"]
        filtered_tee_set["name"] = tee_set["TeeSetRatingName"]
        filtered_tee_set["num_holes"] = tee_set["HolesNumber"]
        filtered_tee_set["total_yardage"] = tee_set["TotalYardage"]
        filtered_tee_set["total_par"] = tee_set["TotalPar"]
        filtered_tee_set["ratings"] = tee_set["Ratings"]
        filtered_tee_set["holes"] = tee_set["Holes"]
        return_object["tee_sets"].append(filtered_tee_set)
    return return_object


def process_request(id):
    url = URL + str(id)
    print("Now requesting for course id:", id)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 200:
        body = json.loads(resp.content)
        if body is not None:
            new_data = filter(body)
            return new_data
        else:
            return None
    elif resp.status_code == 429:
        print("Rate Limiting Has Occured")
        print("Headers:", resp.headers)
        print()
        print("Content", resp.content)
        input("Press any key to continue, will delay for 10 seconds")
        return None
    else:
        print(resp.status_code)
        print("Error", resp.content)
        input("Solved?")
        return None

def main():
    array = []

    print("Starting requests...")
    time1 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=14) as executor:
        futures = [executor.submit(process_request, i) for i in range(30000,35000)]
        for future in concurrent.futures.as_completed(futures):
            if future.result() is not None:
                array.append(future.result())
        #
    time2 = time.perf_counter()
    print(f"Requests finished! That took {time2 - time1} seconds.")
    print("Starting write...")
    time3 = time.perf_counter()
    with open('courses4.json', 'w') as course_file:
        json.dump(array, course_file, indent=2)
    time4 = time.perf_counter()
    print(f"Finished. The write took {time4 - time3} seconds. Total time: {time4 - time1} seconds.")
        
            

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user.")