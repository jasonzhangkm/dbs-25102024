from flask import Flask, render_template, request

app = Flask(__name__)

# Function to calculate the exchange
def calculate_exchange(amount, selected_denom):
    denominations = [10, 5, 2]
    results = {10: 0, 5: 0, 2: 0}
    
    remaining_amount = amount
    for denom in denominations:
        if str(denom) in selected_denom:
            num_bills = remaining_amount // denom
            results[denom] = num_bills
            remaining_amount -= num_bills * denom
    
    if remaining_amount != 0:
        raise ValueError(f"Invalid input: unable to fully exchange amount={amount} with selected_denom={selected_denom}")
    
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            all_results = []
            total_amount_exchanged = 0
            final_summary = {10: 0, 5: 0, 2: 0}

            # Get data for each location
            locations = ['POS51', 'POS52', 'Petty Cash', 'Safe']
            for location in locations:
                amount = float(request.form[f'amount_{location}'])
                selected_denom = request.form.getlist(f'denom_{location}')
                
                if not selected_denom:
                    raise ValueError(f"Invalid input for {location}: amount={amount}, selected_denom={selected_denom}")
                
                exchange_results = calculate_exchange(amount, selected_denom)
                total_exchanged = sum(exchange_results[denom] * denom for denom in exchange_results)
                
                # Save the results for this location
                all_results.append({
                    'location': location,
                    '10': exchange_results[10],
                    '5': exchange_results[5],
                    '2': exchange_results[2],
                    'total_exchanged': total_exchanged
                })
                
                # Add to the final summary
                for denom in exchange_results:
                    final_summary[denom] += exchange_results[denom]
                
                total_amount_exchanged += total_exchanged

            return render_template('results.html', all_results=all_results, total_amount_exchanged=total_amount_exchanged, final_summary=final_summary)

        except Exception as e:
            return f"An error occurred: {e}"

    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
