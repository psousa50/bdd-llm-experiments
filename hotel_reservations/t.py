from langsmith import Client

client = Client()

runs = client.list_runs(
    project_name="TalkTune 3",
)

total = 0

ic = 0.03
oc = 0.06


for run in runs:
    if run.prompt_tokens is not None:
        total += run.prompt_tokens * ic
    if run.completion_tokens is not None:
        total += run.completion_tokens * oc

    if total > 0:
        for k in run.__dict__.keys():
            print(k, run.__dict__[k])
        break

print(f"Total tokens cost: {total / 1000}")
