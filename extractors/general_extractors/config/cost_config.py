cost_per_token = {
    "input": {
        "gpt-4-turbo": -100,
        "gpt-4": 0.000028,
        "gpt-3.5-turbo-16k": 0.000003,
        "gpt-3.5-turbo": 0.0000014,
    },
    "output": {
        "gpt-4-turbo": -100,
        "gpt-4": 0.000055,
        "gpt-3.5-turbo-16k": 0.000004,
        "gpt-3.5-turbo": 0.0000019,
    },
    "azure": 0.01,
}
available_costs=[
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo",
    "azure",
]
