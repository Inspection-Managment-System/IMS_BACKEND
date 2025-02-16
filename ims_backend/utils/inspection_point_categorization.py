def categorize_inspection_point(flammability, health_risk, reactivity):
    risk_map = {"Low": 0, "Medium": 1, "High": 2}

    total_risk = risk_map[flammability] + risk_map[health_risk] + risk_map[reactivity]

    if total_risk == 6:
        return "Severe Risk"
    elif total_risk >= 5:
        return "High Risk"
    elif total_risk >= 3:
        return "Moderate Risk"
    elif total_risk >= 2:
        return "Caution"
    else:
        return "Safe"
