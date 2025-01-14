from django_q.tasks import schedule
from bank.models import VerificationCode
import datetime

def delete_code(code_id):
    code=VerificationCode.objects.filter(id=code_id)
    if code.exists():
        code.first().delete()

def delete_code_async(code_id, delay_time = 300):
    schedule("bank.tasks.delete_code",
         code_id,
         next_run=datetime.datetime.now()+datetime.timedelta(seconds=delay_time))