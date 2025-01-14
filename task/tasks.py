from django_q.tasks import schedule
import os
import datetime

def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass

def delete_file_async(file_path, delay_time = 1800):
    schedule("task.tasks.delete_file",
         file_path,
         next_run=datetime.datetime.now()+datetime.timedelta(seconds=delay_time))