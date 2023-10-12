from prefect import flow, task
from prefect_aws.s3 import S3Bucket
from prefect.deployments import run_deployment
from prefect.task_runners import ConcurrentTaskRunner
import time
from pydantic import BaseModel


class SimulatedFailure(BaseModel):
    child_flow_a: bool = False
    child_flow_b: bool = False
    downstream_task_j: bool = False

# -- Normal Tasks --

@task()
def upstream_task_h():
    print("upstream task")
    return {"h": "upstream task"}


@task()
def upstream_task_i():
    print("upstream task")
    return {"i": "upstream task"}


@task()
def mid_subflow_upstream_task_f():
    print("mid subflow task")
    return {"f": "mid subflow task"}


@task()
def downstream_task_p(h):
    print(h)
    return {"p": "downstream task"}


@task()
def downstream_task_j(a, c=None, sim_failure_downstream_task_j=False):
    if sim_failure_downstream_task_j:
        raise Exception("This is a test exception")
    else:
        print("downstream task")
        return {"j": "downstream task"}


@task()
def downstream_task_k(b=None):
    k = b
    print("downstream task")
    return {"k": "downstream task"}

# -- Tasks that Wrap Deployments --

@task()
def wrapper_task_a(i, sim_failure_child_flow_a, sleep_time=0):
    print("wrapper task")
    a = run_deployment(
        "child-flow-a/dep-child-a",
        parameters={
            "i": i,
            "sim_failure_child_flow_a": sim_failure_child_flow_a,
            "sleep_time": sleep_time,
        },
    )
    return {"a": a.state.result()}


@task()
def wrapper_task_b(sim_failure_child_flow_b, sleep_time=0):
    print("wrapper task")
    b = run_deployment(
        name="child-flow-b/dep-child-b",
        parameters={
            "sim_failure_child_flow_b": sim_failure_child_flow_b,
            "sleep_time": sleep_time,
        },
    )
    # WARNING: We do not evaluate the result or state in this
    # wrapper task decoupling this wrapper task from its
    # subflow's state. This is the "fire and forget" approach.
    return {"b": "not flow result"}


@task()
def wrapper_task_c(sleep_time=0):
    print("wrapper task")
    c = run_deployment(
        name="child-flow-c/dep-child-c", parameters={"sleep_time": sleep_time}
    )
    return {"c": c.state.result()}


@flow(
    task_runner=ConcurrentTaskRunner(),
    persist_result=True,
    result_storage=S3Bucket.load("result-storage"),
)
def task_wrapped_deployments(
    sim_failure: SimulatedFailure = SimulatedFailure(), sleep_time_subflows: int = 0
):
    h = upstream_task_h.submit()
    i = upstream_task_i.submit()
    p = downstream_task_p.submit(h)
    a = wrapper_task_a.submit(
        i, sim_failure.child_flow_a, sleep_time=sleep_time_subflows
    )
    f = mid_subflow_upstream_task_f.submit()
    b = wrapper_task_b.submit(
        sim_failure_child_flow_b=sim_failure.child_flow_b,
        sleep_time=sleep_time_subflows,
        wait_for=[i],
    )
    c = wrapper_task_c.submit(sleep_time=sleep_time_subflows)
    j = downstream_task_j.submit(a, c, sim_failure.downstream_task_j)
    k = downstream_task_k.submit(wait_for=[b])
    time.sleep(sleep_time_subflows)

    return {"j": j, "k": k}
 
# ---

if __name__ == "__main__":
    task_wrapped_deployments(
        sim_failure=SimulatedFailure(
            child_flow_a=False, child_flow_b=False, downstream_task_j=False
        ),
        sleep_time_subflows=0,
    )