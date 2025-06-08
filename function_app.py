import logging
import azure.functions as func
from ri_optimizer import generate_ri_recommendations

app = func.FunctionApp()

@app.function_name(name="CheckRIUtilization")
@app.schedule(schedule="0 0 1 * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False)
def run_report(myTimer: func.TimerRequest) -> None:
    logging.info("RI/SP report function triggered")
    generate_ri_recommendations()
