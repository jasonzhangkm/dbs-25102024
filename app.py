from flask import Flask, render_template, request

app = Flask(__name__)

# Function to perform denomination exchange
def perform_exchange(amount, selected_denom):
    denom_distribution = {"10": 0, "5": 0, "2": 0}
    remaining_amount = amount

    # Exchange for $10 bills
    if "10" in selected_denom:
        denom_distribution["10"] = remaining_amount // 10
        remaining_amount = remaining_amount % 10

    # Exchange for $5 bills
    if "5" in selected_denom:
        denom_distribution["5"] = remaining_amount // 5
        remaining_amount = remaining_amount % 5

    # Exchange for $2 bills
    if "2" in selected_denom:
        denom_distribution["2"] = remaining_amount // 2
        remaining_amount = remaining_amount % 2

    # If the remaining amount is not zero and no denomination can cover it, throw an error
    if remaining_amount != 0:
        raise ValueError(f"Cannot exchange remaining amount of ${remaining_amount} with available denominations.")

    return denom_distribution

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Input amounts for each location
            pos51_amount = float(request.form['pos51_amount'])
            pos52_amount = float(request.form['pos52_amount'])
            petty_cash_amount = float(request.form['petty_cash_amount'])
            safe_amount = float(request.form['safe_amount'])

            # Input selected denominations for each location
            pos51_denom = request.form.getlist('pos51_denom')
            pos52_denom = request.form.getlist('pos52_denom')
            petty_cash_denom = request.form.getlist('petty_cash_denom')
            safe_denom = request.form.getlist('safe_denom')

            all_results = []
            total_amount_exchanged = 0
            final_summary = {"10": 0, "5": 0, "2": 0}

            # POS51 Exchange
            pos51_result = perform_exchange(pos51_amount, pos51_denom)
            pos51_total = sum(pos51_result[denom] * int(denom) for denom in pos51_result)
            all_results.append({"location": "POS51", **pos51_result, "total_exchanged": pos51_total})
            total_amount_exchanged += pos51_total
            final_summary["10"] += pos51_result["10"]
            final_summary["5"] += pos51_result["5"]
            final_summary["2"] += pos51_result["2"]

            # POS52 Exchange
            pos52_result = perform_exchange(pos52_amount, pos52_denom)
            pos52_total = sum(pos52_result[denom] * int(denom) for denom in pos52_result)
            all_results.append({"location": "POS52", **pos52_result, "total_exchanged": pos52_total})
            total_amount_exchanged += pos52_total
            final_summary["10"] += pos52_result["10"]
            final_summary["5"] += pos52_result["5"]
            final_summary["2"] += pos52_result["2"]

            # Petty Cash Exchange
            petty_cash_result = perform_exchange(petty_cash_amount, petty_cash_denom)
            petty_cash_total = sum(petty_cash_result[denom] * int(denom) for denom in petty_cash_result)
            all_results.append({"location": "Petty Cash", **petty_cash_result, "total_exchanged": petty_cash_total})
            total_amount_exchanged += petty_cash_total
            final_summary["10"] += petty_cash_result["10"]
            final_summary["5"] += petty_cash_result["5"]
            final_summary["2"] += petty_cash_result["2"]

            # Safe Exchange
            safe_result = perform_exchange(safe_amount, safe_denom)
            safe_total = sum(safe_result[denom] * int(denom) for denom in safe_result)
            all_results.append({"location": "Safe", **safe_result, "total_exchanged": safe_total})
            total_amount_exchanged += safe_total
            final_summary["10"] += safe_result["10"]
            final_summary["5"] += safe_result["5"]
            final_summary["2"] += safe_result["2"]

            return render_template('results.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
