import schedule
import time, os
import datetime, pdb

# from datetime import datetime

def job4():
     the_date = datetime.datetime.now()
     result_date = the_date + datetime.timedelta(days=-3)
     result_date = result_date.strftime('%Y%m%d')
     txtFile =  os.path.join('log','Log'+result_date+'.txt')
     commenLine = ' sh killbytxt.sh ' + txtFile
     os.system(commenLine)




if __name__ == '__main__':
    schedule.every().day.at('23:00').do(job4)

    while True:
        schedule.run_pending()
