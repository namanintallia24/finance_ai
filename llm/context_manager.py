def format_tool_result(tool_name: str, result: dict) -> str:
    """
    Formats the structured tool output into a string that can be fed back into Gemini
    as part of the ongoing prompt.

    Args:
        tool_name (str): The tool that was called.
        result (dict): The output returned by the tool.

    Returns:
        str: Formatted summary to re-inject into the LLM.
    """
    if tool_name == "company_info_":
        lines = ["Comparison of company info:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "compare_net_income":
        lines = ["Comparison of Net Income:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "cash_flow":
        comparison = result.get("comparison", {})
        lines = ["Comparison of Cash Flow:"]
        
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            for year, data in yearly_data.items():
                lines.append(f"  {year}:")
                 
                # 🔁 Case 1: Full cash flow dict is present (user asked for "cash flow")
                if isinstance(data, dict) and all(key in data for key in [
                    "cash from operating activities", "cash from investing activities",
                    "cash from financing activities", "net cash flow"
                ]):
                    lines.append(f"    Cash from Operating Activities: {data.get('cash from operating activities', 'N/A')}")
                    lines.append(f"    Cash from Investing Activities: {data.get('cash from investing activities', 'N/A')}")
                    lines.append(f"    Cash from Financing Activities: {data.get('cash from financing activities', 'N/A')}")
                    lines.append(f"    Net Cash Flow: {data.get('net cash flow', 'N/A')}")

                # 🔁 Case 2: Only partial/individual fields requested
                elif isinstance(data, dict):
                    for label, value in data.items():
                        lines.append(f"    {label.title()}: {value}")

                else:
                    lines.append("    No data available.")

        return "\n".join(lines)

    elif tool_name == "summarize_balance_sheet":
        
        comparison = result.get("comparison", {})
        lines = ["Comparison of Balance Sheet:"]

        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            for year, data in yearly_data.items():
                lines.append(f"  {year}:")
                
                if isinstance(data, dict):
                    for label, value in data.items():
                        lines.append(f"    {label.title()}: {value}")

                else:
                    lines.append("    No data available.")

        return "\n".join(lines)

    elif tool_name == "yearly_shareholding":
        lines = ["Comparison of Net Income:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)
    

    elif tool_name == "financial_ratio":
        lines = ["Comparison of financial ratio:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "compare_quarterly_income":
        lines = ["Comparison of Quarterly Income:"]
        comparison = result.get("comparison", {})
        
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "quarterly_shareholding":
        lines = ["Comparison of Quarterly Shareholding:"]
        comparison = result.get("comparison", {})
        
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "three_statements_":
        lines = ["📊 Comparison of Company Info:\n"]
        for result in result:
                comparison = result.get("comparison", {})
                for company, year_data in comparison.items():
                    lines.append(f"🏢 {company}:")
                    for year, content in year_data.items():
                        lines.append(f"  📅 Year: {year}")
                        if isinstance(content, dict):
                            for section, values in content.items():
                                lines.append(f"    📂 {section.capitalize()}:")
                                if isinstance(values, dict):
                                    for key, val in values.items():
                                        lines.append(f"      • {key.capitalize()}: {val}")
                                else:
                                    lines.append(f"      • {section}: {values}")
                        else:
                            lines.append(f"    • Data: {content}")
                    lines.append("")  # Blank line between companies
        return "\n".join(lines)
    
    elif tool_name == "sector_wise_company":
        lines = ["📊 Sector-wise Company Comparison:"]
        comparison = result.get("comparison", {})

        for sector, companies in comparison.items():
            lines.append(f"\n🧩 Sector: {sector}")
            if not companies:
                lines.append("  No companies found.")
                continue

            for company in companies:
                lines.append(f"\n🏢 {company.get('company_name', 'Unknown Company')}")
                for key, value in company.items():
                    if key != "company_name":
                        lines.append(f"{key}: {value}")
        return "\n".join(lines)
    
    elif tool_name == "cash_flow_to_debt_":
        lines = ["Comparison of cash flow to debt:"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "debt_to_financing_ratio_":
        lines = ["Comparison of debt to financing ratio :"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "operating_cf_to_interest_":
        lines = ["Comparison of operating cf to interest :"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "_net_c_f_margin":
        lines = ["Comparison of net cash flow margin :"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "_fixed_asset_turnover_ratio":
        lines = ["Comparison of fixed asset turnover :"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)

    elif tool_name == "_operating_cf_to_liablities":
        lines = ["Comparison of operating cf to liablities :"]
        comparison = result.get("comparison", {})
        for company, yearly_data in comparison.items():
            lines.append(f"\n{company}:")
            if isinstance(yearly_data, dict):
                for year, value in yearly_data.items():
                    lines.append(f"  {year}: {value}")
            else:
                lines.append(f"  {yearly_data}")
        return "\n".join(lines)


    else:
        return "No context available for the requested tool."


def build_context(tool_name: str, tool_result: dict) -> str:
    """
    Prepares a formatted string that represents the context derived from tool results,
    to be inserted into the next Gemini prompt.

    Args:
        tool_name (str): The name of the tool that was used.
        tool_result (dict): The output dictionary returned by the tool.

    Returns:
        str: Context string to be added to LLM prompt.
    """
    formatted = format_tool_result(tool_name, tool_result)
    return f"\n\n[Context based on tool result]\n{formatted}"
    # return formatted




