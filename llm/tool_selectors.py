TOOLS = {
    "sector_wise_company": {
        "description": "Get all companies belonging to a specific sector",
        "params": {
            "sector": ["List of requested sector fields.\
    Options: Agro Chemicals, Air Transport Service, Alcoholic Beverages, Auto Ancillaries, Automobile, Banks, Bearings, Cables, \
    Capital Goods - Electrical Equipment, Capital Goods-Non Electrical Equipment, Castings Forgings & Fastners, Cement, Cement - Products,\
    Ceramic Products, Chemicals, Computer Education, Construction, Consumer Durables, de Oil & Natural Gas, Diamond Gems and Jewellery, \
    dit Rating Agencies, Diversified, Dry cells, E-Commerce/App based Aggregator, Edible Oil, Education, Electronics, Engineering, \
    Entertainment, Ferro Alloys, Fertilizers, Finance, FMCG, Gas Distribution, Glass & Glass Products, Healthcare, Hotels & Restaurants, \
    Infrastructure Developers & Operators, Infrastructure Investment Trusts, Insurance, IT - Hardware, IT - Software, Leather, Logistics, \
    Marine Port & Services, Media - Print/Television/Radio, Mining & Mineral products, Miscellaneous, Non Ferrous Metals, Oil Drill/Allied, \
    Packaging, Paints/Varnish, Paper, Petrochemicals, Pharmaceuticals, Plantation & Plantation Products, Plastic products, Power Generation & Distribution,\
    Power Infrastructure, Printing & Stationery, Quick Service Restaurant, Railways, Readymade Garments/ Apparells, Real Estate Investment Trusts, \
    Realty, Refineries, Refractories, Retail, Ship Building, Shipping, Steel, Stock/ Commodity Brokers, Sugar, Telecom-Handsets/Mobile, \
    Telecomm Equipment & Infra Services, Telecomm-Service, Textiles, Tobacco Products, Trading, Tyres"]
        }
    },
    "quarterly_shareholding": {
       "description": "Fetch quarterly shareholding pattern of a company for a given year and quarter. \
    If the user asks for the complete shareholding pattern, then set fields = ['shareholding pattern']. \
    If the user asks for specific categories (e.g., promoters, FIIs, DIIs, public), \
    then include only those requested categories in fields.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "quarter": "Quarter (first, second, third, fourth)",
                "fields": "List of requested shareholding categories. \
    Options: promoters, fiis, diis, government, public, others, no of shareholders, shareholding pattern"
        }
    },
    "compare_quarterly_income": {
        "description": "Compare quarterly income of a company for a given year or between quarters. \
    If the user asks for 'quarterly performance' or 'quarterly income statement', \
    then set fields = ['quarterly performance'] (all income statement fields). \
    If the user asks for specific fields like sales, net profit, EPS, etc., \
    then include only those fields in the list.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "quarter_month": "Quarter name (one or more: ['first', 'second', 'third', 'fourth']) or an empty list [] to fetch all quarters",
                "fields": "List of requested income statement fields. \
    Options: profit before tax, depreciation, interest, other income, opm percentage, \
    operating profit, expenses, sales, net npa, gross npa, financing margin, \
    financing profit, revenue, eps_in_rs, net profit, tax percentage, \
    quarterly performance, quarterly income statement"
        }
    },
    "financial_ratio": {
        "description": "Retrieve financial ratios of a company. \
    If the user asks for 'financial ratio' (general), then set fields = ['financial ratio'] \
    which means return all available ratios. \
    If the user asks for specific ratios like PE, ROE, ROCE, working capital days, etc., \
    then include only those fields in the list.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "fields": "List of requested ratio fields. \
    Options: PE ratio, ROE percentage, ROCE percentage, working capital days, \
    cash conversion cycle, days payable, inventory days, debtor days, financial ratio"
        }
   },
    "yearly_shareholding": {
        "description": "Fetch yearly shareholding pattern of a company. \
    If the user asks for 'shareholding pattern' (general), then set fields = ['shareholding pattern'] \
    which means return all available categories. \
    If the user asks for specific categories like promoters, FIIs, DIIs, public, etc., \
    then include only those fields in the list.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "fields": "List of requested shareholding fields. \
    Options: promoters, FIIs, DIIs, public, government, others, no of shareholders, shareholding pattern"
        }
   },
    "summarize_balance_sheet": {
        "description": "Summarize a company's balance sheet for a specific year. \
        If the user asks for the full balance sheet, then set fields = 'balance sheet'. \
        If the user asks for specific items (e.g., fixed assets, reserves, total assets), \
        then include only those requested items in fields.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "fields": "List of requested financial fields. \
        Options: fixed assets, other liabilities, reserves, equity capital, net loans, \
        total liabilities, total assets, preference capital, other assets, investments, cwip, balance sheet"
        }
    },
    "cash_flow": {
        "description": "Retrieve the cash flow statement of a company. \
    If the user asks for 'cash flow statement' or 'cash flow' (general), then set fields = ['cash flow statement'] \
    which means return all major components (operating, investing, financing, net cash flow). \
    If the user asks for specific categories like only 'net cash flow' or 'cash from operating activity', \
    then include only those fields in the list.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "fields": "List of requested cash flow fields. \
    Options: net cash flow, cash from financing activity, cash from investing activity, cash from operating activity, cash flow statement"
        }
    },
   "compare_net_income": {
       "description": "Retrieve income statement of a company. \
    If the user asks for 'income statement' or 'net income statement' (general), then set fields = ['income statement'] \
    which means return all major income statement components (net income, sales, revenue, margins, etc). \
    If the user asks for specific categories like only 'net income' or 'revenue', \
    then include only those fields in the list.",
            "params": {
                "company_names": "Name of the company",
                "year": "Financial year (string, e.g., '2020')",
                "fields": "List of requested income statement fields. \
    Options: net income, sales, net margin, financing margin percentage, financing profit, revenue, eps in rs, \
    tax percentage, profit before tax, depreciation, other income, operating profit, expenses, interest, eps_n_rs, income statement"
        }
    },
    "company_info_": {
        "description": "Fetch general company information or performance metrics. \
    If the user asks for EPS trends → set fields = ['eps trends']. \
    If the user asks for return ratios → set fields = ['return ratios']. \
    If the user asks for (debt trends or debt growth) → set fields = ['debt trends']. \
    If the user asks for Company info or wants all company-related info → set fields = ['company details']. \
    If the user asks for specific fields, include only those fields.",
            "params": {
                "company_names": "Name(s) of the company",
                "year": "Financial year as string (e.g., '2020')",
                "fields": "List of requested company informations fields. Options include: \
    company name, high low, current price, sales growth 3years, sales growth 5years, sales growth 7years, sales growth 10years, \
    profit growth 3years, debt trends, eps trends, profit growth 5years, profit growth 7years, profit growth 10years, \
    price to sales, face value, stock pe, market cap, bse, sector, roce, roe, debt, debt 3years back, debt 5years back, debt 7years back, debt 10years back, eps last year, eps"
        }
    },
    "cash_flow_to_debt_": {
       "description": "Fetch the cash flow to debt ratio of a company",
       "params": {
            "company_names": "Name of the company",
            "year": "Financial year (string, e.g., '2020')",
            "fields": ["cash from operating activity", "net loans"]
        }
    },
   "debt_to_financing_ratio_": {
       "description": "Fetch the debt to financing ratio of a company",
       "params": {
            "company_names": "Name of the company",
            "year": "Financial year (string, e.g., '2020')",
            "fields": ["net loans", "cash from financing activity"]
        }
    },
   "operating_cf_to_interest_": {
       "description": "Fetch the operating cash flow to interest of a company",
       "params": {
            "company_names": "Name of the company",
            "year": "Financial year (string, e.g., '2020')",
            "fields": ["cash from operating activity", "interest"]
        }
    },
   "_net_c_f_margin": {
       "description": "Fetch the net cash flow margin of a company",
       "params": {
            "company_names": "Name of the company",
            "year":"Financial year (string, e.g., '2020')",
            "fields": ["net cash flow", "sales"]
        }
    },
   "_fixed_asset_turnover_ratio": {
       "description": "Fetch the fixed asset turnover ratio of a company",
       "params": {
            "company_names": "Name of the company",
            "year":"Financial year (string, e.g., '2020')",
            "fields": ["sales", "fixed assets"]
        }
    },
   "_operating_cf_to_liablities": {
       "description": "Fetch the operating cf to liablities of a company",
       "params": {
            "company_names": "Name of the company",
            "year": "Financial year (string, e.g., '2020')",
            "fields": ["cash from operating activity", "total liabilities"]

        }
    },
   "three_statements_": {
       "description": "Fetch the three financial statements(like compare_net_income, cash flow, summarize_balance_sheet) of a company",
       "params": {
            "company_names": "Name of the company",
            "year": "Financial year (string, e.g., '2020')",
            "fields": ["three financial statement"]

        }
    }
    
}
