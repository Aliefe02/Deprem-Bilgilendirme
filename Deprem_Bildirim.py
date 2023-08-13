import requests
from bs4 import BeautifulSoup
import time
from winotify import Notification, audio

class TableRowData:
    def __init__(self, tds):
        self.date = tds[0].get_text(strip=True)
        self.latitude = float(tds[1].get_text(strip=True))
        self.longitude = float(tds[2].get_text(strip=True))
        self.depth = float(tds[3].get_text(strip=True))
        self.type = tds[4].get_text(strip=True)
        self.magnitude = float(tds[5].get_text(strip=True))
        self.location = tds[6].get_text(strip=True)
        self.earthquake_id = tds[7].get_text(strip=True)

    def __str__(self):
        return f"Date: {self.date}\nLatitude: {self.latitude}\nLongitude: {self.longitude}\nDepth: {self.depth}\nType: {self.type}\nMagnitude: {self.magnitude}\nLocation: {self.location}\nEarthquake ID: {self.earthquake_id}\n"



last_earthquakes = []
new_earthquakes = []
unreported_earthquakes = []
important_earthquakes = []
i = 0
while True:

    try:
        Earthquakes = requests.get('https://deprem.afad.gov.tr/last-earthquakes.html')
        soup = BeautifulSoup(Earthquakes.text, 'html.parser')
        trs = soup.find('tbody').find_all('tr')[:3]

        for tr in trs:
            tds = tr.find_all('td')
            row_data = TableRowData(tds)
            new_earthquakes.append(row_data)
            unreported_earthquakes.append(row_data)

        for earthquake in new_earthquakes:
            for last_earthquake in last_earthquakes:
                if earthquake.earthquake_id == last_earthquake.earthquake_id:
                    unreported_earthquakes.remove(earthquake)
                    break

        last_earthquakes.clear()
        for earthquake in new_earthquakes:
            last_earthquakes.append(earthquake)
        
        new_earthquakes.clear()
        
        for e in unreported_earthquakes:
            if e.magnitude >= 4.5:
                message = 'Location: '+str(e.location)+'\nMagnitude: '+str(e.magnitude)
                important_earthquakes.append(e)
                toast = Notification(app_id="windows app",
                title="Warning, New Earthquake!",
                msg=message)
                toast.set_audio(audio.LoopingCall, loop=False)
                toast.add_actions(label="More Info", 
                  launch="https://deprem.afad.gov.tr/last-earthquakes")
                toast.show()
            
        unreported_earthquakes.clear()
        time.sleep(60)
    except Exception as e:
        pass
