import frappe
# from frappe import _, scrub
# from frappe.utils import add_to_date, flt, getdate

# def execute(filters=None):
#     return CustomerParentGroupMonthlyReport(filters).run()

# class CustomerParentGroupMonthlyReport:
#     def __init__(self, filters=None):
#         self.filters = frappe._dict(filters or {})
#         self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#         self.get_period_date_ranges()

#     def run(self):
#         self.get_columns()
#         self.get_data()
#         self.get_chart_data()
#         return self.columns, self.data, None, self.chart

#     def get_columns(self):
#         self.columns = [{
#             "label": _("Customer Parent Group"),
#             "fieldname": "customer_parent_group",
#             "fieldtype": "Link",
#             "options": "Customer Group",
#             "width": 200
#         }]
        
#         for end_date in self.periodic_daterange:
#             period = self.get_period(end_date)
#             self.columns.append({
#                 "label": _(f"Sales {period}"),
#                 "fieldname": scrub(f"sales_{period}"),
#                 "fieldtype": "Currency",
#                 "width": 120
#             })
#             self.columns.append({
#                 "label": _(f"Returns {period}"),
#                 "fieldname": scrub(f"returns_{period}"),
#                 "fieldtype": "Currency",
#                 "width": 120
#             })

#         self.columns.append({
#             "label": _("Total Sales"),
#             "fieldname": "total_sales",
#             "fieldtype": "Currency",
#             "width": 120
#         })

#         self.columns.append({
#             "label": _("Total Returns"),
#             "fieldname": "total_returns",
#             "fieldtype": "Currency",
#             "width": 120
#         })

#     def get_data(self):
#         self.get_sales_and_returns()
#         self.get_rows_by_group()

#     def get_sales_and_returns(self):
#         sales_entries = frappe.db.sql("""
#             SELECT
#                 cg.parent_customer_group as parent_group,
#                 si.posting_date,
#                 SUM(si.base_net_total) as sales_value
#             FROM `tabSales Invoice` si
#             JOIN `tabCustomer Group` cg ON si.customer_group = cg.name
#             WHERE si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.company = %s
#             GROUP BY cg.parent_customer_group, si.posting_date
#         """, (self.filters.from_date, self.filters.to_date, self.filters.company), as_dict=1)

#         return_entries = frappe.db.sql("""
#             SELECT
#                 cg.parent_customer_group as parent_group,
#                 si.posting_date,
#                 SUM(si.promotion) as return_value
#             FROM `tabSales Invoice` si
#             JOIN `tabCustomer Group` cg ON si.customer_group = cg.name
#             WHERE si.docstatus = 1
#             AND si.is_return = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND si.company = %s
#             GROUP BY cg.parent_customer_group, si.posting_date
#         """, (self.filters.from_date, self.filters.to_date, self.filters.company), as_dict=1)

#         self.sales_data = frappe._dict()
#         self.return_data = frappe._dict()

#         for d in sales_entries:
#             period = self.get_period(d.posting_date)
#             self.sales_data.setdefault(d.parent_group, frappe._dict()).setdefault(period, 0.0)
#             self.sales_data[d.parent_group][period] += flt(d.sales_value)

#         for d in return_entries:
#             period = self.get_period(d.posting_date)
#             self.return_data.setdefault(d.parent_group, frappe._dict()).setdefault(period, 0.0)
#             self.return_data[d.parent_group][period] += flt(d.return_value)

#     def get_rows_by_group(self):
#         self.data = []
#         self.get_customer_groups()

#         for group in self.group_entries:
#             if group.group:
#                 parent_group = group.group
#             else:
#                 parent_group = group.name

#             row = {
#                 "customer_parent_group": parent_group,
#                 "indent": self.depth_map.get(group.name, 0)
#             }
#             total_sales = 0
#             total_returns = 0
#             for end_date in self.periodic_daterange:
#                 period = self.get_period(end_date)
#                 sales_amount = flt(self.sales_data.get(group.name, {}).get(period, 0.0))
#                 return_amount = flt(self.return_data.get(group.name, {}).get(period, 0.0))
#                 row[scrub(f"sales_{period}")] = sales_amount
#                 row[scrub(f"returns_{period}")] = return_amount
#                 total_sales += sales_amount
#                 total_returns += return_amount

#             row["total_sales"] = total_sales
#             row["total_returns"] = total_returns

#             self.data.append(row)

#     def get_customer_groups(self):
#         self.depth_map = frappe._dict()

#         self.group_entries = frappe.db.sql("""
#             SELECT name, parent_customer_group as parent, lft, rgt
#             FROM `tabCustomer Group`
#             ORDER BY lft
#         """, as_dict=1)

#         for d in self.group_entries:
#             if d.parent:
#                 self.depth_map.setdefault(d.name, self.depth_map.get(d.parent, 0) + 1)
#             else:
#                 self.depth_map.setdefault(d.name, 0)

#     def get_period(self, posting_date):
#         period = str(self.months[posting_date.month - 1]) + " " + str(posting_date.year)
#         return period

#     def get_period_date_ranges(self):
#         from dateutil.relativedelta import relativedelta

#         from_date, to_date = getdate(self.filters.from_date), getdate(self.filters.to_date)
#         self.periodic_daterange = []
#         while from_date <= to_date:
#             self.periodic_daterange.append(from_date)
#             from_date = add_to_date(from_date, months=1, as_string=False).replace(day=1)

#     def get_chart_data(self):
#         labels = [d.get("label") for d in self.columns[1:len(self.columns) - 2]]
#         self.chart = {
#             "data": {
#                 "labels": labels,
#                 "datasets": [
#                     {"name": "Sales", "values": [row.get("total_sales") for row in self.data]},
#                     {"name": "Returns", "values": [row.get("total_returns") for row in self.data]},
#                 ]
#             },
#             "type": "line"
#         }

import calendar

def execute(filters=None):
    columns, data = [], []

    # Define the columns for the report (Month names)
    columns = get_columns()

    # Fetch the Sales and Promotion data based on the Customer Group tree
    data = get_data(filters)

    return columns, data

def get_columns():
    """Defines the columns of the report."""
    columns = [
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 250},
        {"label": "Total Sales (Including Return)", "fieldname": "total_sales", "fieldtype": "Currency", "width": 150},
        {"label": "Total Promotion Value", "fieldname": "promotion", "fieldtype": "Currency", "width": 150}
    ]

    # Add columns dynamically for each month
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    for month in months:
        columns.append({"label": f"{month} Sales", "fieldname": f"{month.lower()}_sales", "fieldtype": "Currency", "width": 120})
        columns.append({"label": f"{month} Promotion", "fieldname": f"{month.lower()}_promotion", "fieldtype": "Currency", "width": 120})
    
    return columns

def get_data(filters):
    """Fetches data based on filters applied."""
    query = """
        SELECT 
            cg.name as customer_group,
            SUM(si.total) as total_sales,
            SUM(si.promotion) as promotion,
            MONTH(si.posting_date) as month,
            si.is_return
        FROM
            `tabSales Invoice` si
        JOIN 
            `tabCustomer` c ON si.customer = c.name
        JOIN 
            `tabCustomer Group` cg ON c.customer_group = cg.name
        WHERE
            si.docstatus = 1 
            AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY 
            cg.name, MONTH(si.posting_date), si.is_return
        ORDER BY 
            cg.name, month
    """

    sales_data = frappe.db.sql(query, filters, as_dict=True)
    
    # Process the sales data and format it into rows
    processed_data = process_sales_data(sales_data)
    return processed_data

def process_sales_data(sales_data):
    """Processes sales data to group by Customer Group and distribute it by month."""
    customer_group_tree = {}
    
    for row in sales_data:
        customer_group = row.get('customer_group')
        month = row.get('month')
        is_return = row.get('is_return')

        # Create or update data for each customer group
        if customer_group not in customer_group_tree:
            customer_group_tree[customer_group] = {
                "customer_group": customer_group,
                "total_sales": 0,
                "promotion": 0
            }
            for m in range(1, 13):
                customer_group_tree[customer_group][f"{calendar.month_name[m].lower()}_sales"] = 0
                customer_group_tree[customer_group][f"{calendar.month_name[m].lower()}_promotion"] = 0

        # Update sales or promotion values
        if is_return:
            customer_group_tree[customer_group]['total_sales'] += row.get('total_sales', 0)
        else:
            customer_group_tree[customer_group]['promotion'] += row.get('promotion', 0)
        
        customer_group_tree[customer_group][f"{calendar.month_name[month].lower()}_sales"] += row.get('total_sales', 0)
        customer_group_tree[customer_group][f"{calendar.month_name[month].lower()}_promotion"] += row.get('promotion', 0)

    # Convert tree data to list of rows
    return list(customer_group_tree.values())
