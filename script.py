from datetime import datetime
import time



def main():
    
    date = datetime.now()

    stringformat = time.mktime(date.timetuple())
    print(stringformat)
    return ""



if __name__ == "__main__":
    main()