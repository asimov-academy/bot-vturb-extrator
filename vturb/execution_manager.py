import datetime
from tinydb import TinyDB, Query

class ExecutionManager:
    def __init__(self, db_path="./execution_db.json"):
        self.db = TinyDB(db_path)
        self.executions = self.db.table('executions')
        self.Execution = Query()
    
    def should_execute(self):
        """
        Determina se o script deve ser executado com base nas regras:
        - Primeira execução após as 5h
        - Primeira execução após as 17h
        """
        now = datetime.datetime.now()
        current_time = now.time()
        current_date = now.date()
        
        # Obtém a última execução bem-sucedida
        last_successful = self.executions.search(
            (self.Execution.success == True) & 
            (self.Execution.date == str(current_date))
        )
        
        # Verifica se estamos no período da manhã (entre 5:00 e 16:59)
        morning_period = datetime.time(5, 0) <= current_time < datetime.time(17, 0)
        
        # Verifica se já houve execução no período da manhã
        morning_execution = False
        # Verifica se já houve execução no período da tarde
        afternoon_execution = False
        
        for execution in last_successful:
            exec_time = datetime.datetime.strptime(execution['time'], '%H:%M:%S').time()
            if datetime.time(5, 0) <= exec_time < datetime.time(17, 0):
                morning_execution = True
            else:
                afternoon_execution = True
        
        # Se estamos no período da manhã e ainda não houve execução pela manhã
        if morning_period and not morning_execution:
            return True
        
        # Se estamos no período da tarde e ainda não houve execução pela tarde
        if not morning_period and not afternoon_execution:
            return True
        
        return False
    
    def register_execution(self, success=True):
        """
        Registra uma execução no banco de dados
        """
        now = datetime.datetime.now()
        self.executions.insert({
            'date': str(now.date()),
            'time': now.time().strftime('%H:%M:%S'),
            'success': success,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    def clear_old_records(self, days=7):
        """
        Remove registros antigos para manter o banco de dados organizado
        """
        cutoff_date = datetime.datetime.now().date() - datetime.timedelta(days=days)
        self.executions.remove(self.Execution.date < str(cutoff_date))
