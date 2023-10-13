import time
from prefect import flow, get_run_logger, task, serve
from prefect.deployments import Deployment

@task
def sample_task(sleep_time=20):
    logger = get_run_logger()
    logger.info('Task running!')
    time.sleep(sleep_time)


def on_cancellation(flow, flow_run, state):
    print('Hi this is the cancellation hook!')
    


@flow(on_cancellation=[on_cancellation], log_prints=True)
def cancel_hook_flow(sleep_time=20):
    sample_task.submit(sleep_time=sleep_time)

if __name__ == '__main__':

    cancel_hook_flow.serve(name='hook-with-task-runner', tags=['hook'])