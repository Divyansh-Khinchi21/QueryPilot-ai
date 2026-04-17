def optimize_query(query):
    query = query.strip()

    # Replace SELECT * with specific columns
    if "select *" in query.lower():
        query = query.replace("*", "customer, revenue, date")

    return query