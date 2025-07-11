import schedule
import time
import data_collection

schedule.every().day.at("18:00").do(data_collection.collect(),'It is 18:00')

while True:
    schedule.run_pending()
    time.sleep(600) # wait 10 minutes