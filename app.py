@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        pos51_amount = float(request.form['pos51_amount'])
        pos51_denom = request.form.getlist('pos51_denom')

        pos52_amount = float(request.form['pos52_amount'])
        pos52_denom = request.form.getlist('pos52_denom')

        petty_cash_amount = float(request.form['petty_cash_amount'])
        petty_cash_denom = request.form.getlist('petty_cash_denom')

        safe_amount = float(request.form['safe_amount'])
        safe_denom = request.form.getlist('safe_denom')

        # Perform the exchange for each location
        results = {
            "POS51": exchange_denominations(pos51_amount, pos51_denom),
            "POS52": exchange_denominations(pos52_amount, pos52_denom),
            "Petty Cash": exchange_denominations(petty_cash_amount, petty_cash_denom),
            "Safe": exchange_denominations(safe_amount, safe_denom)
        }

        # Calculate final summary and total exchanged
        total_amount_exchanged = 0
        final_summary = {'10': 0, '5': 0, '2': 0}
        for location, result in results.items():
            if result:
                # Exclude 'total_bills' from the calculation
                total_amount_exchanged += sum([int(denom) * result[denom] for denom in result if denom.isdigit()])
                for denom in result.keys():
                    if denom.isdigit():  # Only update summary for numeric denominations
                        final_summary[denom] += result[denom]

        return render_template('result.html', all_results=results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

    return render_template('index.html')
