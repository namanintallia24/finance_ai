def prepare_chart_data(tool_result_data_list):
    """
    Convert list of dict financial data into Chart.js format dynamically.

    Example input:
    [
        {
            "comparison": {
                "3i Infotech Ltd": {
                    "2020-03-31": {"net income": 68.0, "sales": 698.0}
                }
            },
            "year": "2020"
        },
        {
            "comparison": {
                "TCS": {
                    "2020-03-31": {"net income": 63.0, "sales": 28.0}
                }
            },
            "year": "2020"
        }
    ]

    Output:
    {
        "labels": ["2020-03-31"],
        "datasets": [
            {"label": "3i Infotech Ltd - net income", "data": [68.0]},
            {"label": "3i Infotech Ltd - sales", "data": [698.0]},
            {"label": "TCS - net income", "data": [63.0]},
            {"label": "TCS - sales", "data": [28.0]}
        ]
    }
    """
    chart_data = {"labels": [], "datasets": []}
    datasets_map = {}  # store dataset dynamically

    for item in tool_result_data_list:
        comparison = item.get("comparison", {})
        for company, years_data in comparison.items():
            for year, metrics in years_data.items():
                # ensure year/label is added
                if year not in chart_data["labels"]:
                    chart_data["labels"].append(year)

                # iterate over dynamic financial metrics
                for metric, value in metrics.items():
                    dataset_key = f"{company} - {metric}"

                    if dataset_key not in datasets_map:
                        datasets_map[dataset_key] = {
                            "label": dataset_key,
                            "data": []
                        }

                    # maintain alignment with labels
                    while len(datasets_map[dataset_key]["data"]) < chart_data["labels"].index(year):
                        datasets_map[dataset_key]["data"].append(None)

                    datasets_map[dataset_key]["data"].append(value)

    # Normalize missing values for datasets
    label_count = len(chart_data["labels"])
    for dataset in datasets_map.values():
        while len(dataset["data"]) < label_count:
            dataset["data"].append(None)

    chart_data["datasets"] = list(datasets_map.values())
    return chart_data
